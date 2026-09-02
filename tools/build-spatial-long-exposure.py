#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Build the public, undated data for the spatial long-exposure trace.

The source exports remain the canonical history. To update the map, replace
them with newer cumulative exports and rebuild this compact public JSON.

Public schema v4:
  coverage: aggregate source range only
  points: [longitude, latitude, recurrence, source mask]
  segments: [start longitude, start latitude, end longitude, end latitude, count]

Source masks are 1 for Day One, 2 for photographs, and 3 for both. Individual
dates and source identifiers are deliberately absent.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
from typing import Any


MAX_CONNECTION_GAP = timedelta(hours=72)
COORDINATE_PRECISION = 6
DEFAULT_CORRECTIONS = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "spatial-long-exposure-corrections.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a Day One Activity Feed backup into an undated set of "
            "points and unordered connection segments."
        )
    )
    parser.add_argument("source", type=Path, help="Day One ActivityFeedBackup.json")
    parser.add_argument("destination", type=Path, help="Public JSON destination")
    parser.add_argument(
        "--photo-locations",
        type=Path,
        help="CSV of photo filename, capture time, latitude, longitude, and UUID",
    )
    parser.add_argument(
        "--through",
        type=date.fromisoformat,
        help="Include source records through this date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--corrections",
        type=Path,
        default=DEFAULT_CORRECTIONS,
        help="JSON containing hashes of specific source records to omit",
    )
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    # Day One's export may leave a trailing comma before the closing array.
    source = re.sub(r",\s*]\s*$", "\n]", source)
    records = json.loads(source)
    if not isinstance(records, list):
        raise ValueError("Expected a top-level array of activity records")
    return records


def parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def coordinates(record: dict[str, Any]) -> tuple[float, float] | None:
    location = record.get("location")
    if not isinstance(location, dict):
        return None
    latitude = location.get("latitude")
    longitude = location.get("longitude")
    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        return None
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return None
    return (
        round(float(longitude), COORDINATE_PRECISION),
        round(float(latitude), COORDINATE_PRECISION),
    )


def source_record_hash(source: str, identifier: Any) -> str | None:
    if not isinstance(identifier, str) or not identifier.strip():
        return None
    value = f"{source}:{identifier.strip().lower()}".encode()
    return hashlib.sha256(value).hexdigest()[:20]


def load_corrections(path: Path) -> tuple[set[str], set[str]]:
    corrections = json.loads(path.read_text(encoding="utf-8"))
    if corrections.get("version") != 1:
        raise ValueError("Expected corrections schema version 1")
    day_one = corrections.get("dayOneRecordHashes")
    photos = corrections.get("photoRecordHashes")
    if not isinstance(day_one, list) or not isinstance(photos, list):
        raise ValueError("Invalid spatial-long-exposure corrections file")
    return set(day_one), set(photos)


def load_photo_points(
    path: Path | None, through: date | None, ignored_hashes: set[str]
) -> tuple[set[tuple[float, float]], int, date | None, date | None]:
    if path is None:
        return set(), 0, None, None

    points: set[tuple[float, float]] = set()
    record_count = 0
    earliest: date | None = None
    latest: date | None = None
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {
            "filename",
            "captured_at",
            "latitude",
            "longitude",
            "uuid",
        }
        if set(reader.fieldnames or ()) != expected_fields:
            raise ValueError(
                "Expected photo CSV fields: " + ", ".join(sorted(expected_fields))
            )

        for row in reader:
            if source_record_hash("photo", row["uuid"]) in ignored_hashes:
                continue
            captured = datetime.strptime(
                row["captured_at"], "%Y-%m-%d %H:%M:%S"
            ).date()
            if through is not None and captured > through:
                continue

            longitude = round(float(row["longitude"]), COORDINATE_PRECISION)
            latitude = round(float(row["latitude"]), COORDINATE_PRECISION)
            if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                raise ValueError(f"Invalid photo coordinate in {row['filename']}")
            # Exact zeroes in either EXIF coordinate are partial/missing GPS
            # values rather than useful locations in this export.
            if latitude == 0 or longitude == 0:
                continue
            point = (longitude, latitude)

            record_count += 1
            points.add(point)
            earliest = captured if earliest is None else min(earliest, captured)
            latest = captured if latest is None else max(latest, captured)

    return points, record_count, earliest, latest


def build_public_data(
    records: list[dict[str, Any]],
    photo_points: set[tuple[float, float]],
    photo_record_count: int,
    photo_earliest: date | None,
    photo_latest: date | None,
    ignored_hashes: set[str],
    through: date | None,
) -> dict[str, Any]:
    visits: list[dict[str, Any]] = []
    for record in records:
        point = coordinates(record)
        arrived = parse_date(record.get("arrivalDate") or record.get("timestamp"))
        if point is None or arrived is None:
            continue
        if through is not None and arrived.date() > through:
            continue
        visits.append(
            {
                "point": point,
                "arrived": arrived,
                "departed": parse_date(record.get("departureDate")),
                "ignored": (
                    source_record_hash("dayone", record.get("uuid"))
                    in ignored_hashes
                ),
            }
        )

    visits.sort(key=lambda visit: visit["arrived"])

    point_counts: Counter[tuple[float, float]] = Counter()
    point_sources: dict[tuple[float, float], int] = defaultdict(int)
    for visit in visits:
        if visit["ignored"]:
            continue
        point = visit["point"]
        point_counts[point] += 1
        point_sources[point] |= 1

    # A burst of photographs at one spot should add one place, not overpower
    # the map through shutter count. Visit records retain their recurrence.
    for point in photo_points:
        point_counts[point] += 1
        point_sources[point] |= 2

    segment_counts: Counter[tuple[float, float, float, float]] = Counter()
    for previous, current in zip(visits, visits[1:]):
        # Keep ignored records in the timeline so removing them cannot create
        # a new synthetic connection between their neighbours.
        if previous["ignored"] or current["ignored"]:
            continue
        previous_departure = previous["departed"] or previous["arrived"]
        gap = current["arrived"] - previous_departure
        if gap < timedelta(0) or gap > MAX_CONNECTION_GAP:
            continue

        start = previous["point"]
        end = current["point"]
        if start == end:
            continue

        # Canonicalize direction so the public data carries no arrow of time.
        if end < start:
            start, end = end, start
        segment_counts[(*start, *end)] += 1

    points = [
        [
            longitude,
            latitude,
            count,
            point_sources[(longitude, latitude)],
        ]
        for (longitude, latitude), count in sorted(point_counts.items())
    ]
    segments = [
        [*segment, count] for segment, count in sorted(segment_counts.items())
    ]
    visible_visits = [visit for visit in visits if not visit["ignored"]]
    coverage_dates = [
        candidate
        for candidate in (
            visible_visits[0]["arrived"].date() if visible_visits else None,
            visible_visits[-1]["arrived"].date() if visible_visits else None,
            photo_earliest,
            photo_latest,
        )
        if candidate is not None
    ]
    if not coverage_dates:
        raise ValueError("No usable locations were found in the source exports")
    coverage = {
        "from": min(coverage_dates).isoformat(),
        "through": max(coverage_dates).isoformat(),
    }

    return {
        "version": 4,
        "coverage": coverage,
        "activityRecordCount": len(visible_visits),
        "photoRecordCount": photo_record_count,
        "photoUniquePointCount": len(photo_points),
        "uniquePointCount": len(points),
        "segmentCount": sum(segment_counts.values()),
        "points": points,
        "segments": segments,
    }


def main() -> None:
    args = parse_args()
    ignored_day_one, ignored_photos = load_corrections(args.corrections)
    previous_point_count: int | None = None
    if args.destination.exists():
        try:
            previous_data = json.loads(args.destination.read_text(encoding="utf-8"))
            candidate = previous_data.get("uniquePointCount")
            if isinstance(candidate, int):
                previous_point_count = candidate
        except (json.JSONDecodeError, OSError):
            pass

    photo_points, photo_record_count, photo_earliest, photo_latest = (
        load_photo_points(args.photo_locations, args.through, ignored_photos)
    )
    public_data = build_public_data(
        load_records(args.source),
        photo_points,
        photo_record_count,
        photo_earliest,
        photo_latest,
        ignored_day_one,
        args.through,
    )
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(
        json.dumps(public_data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    delta = ""
    if previous_point_count is not None:
        point_change = public_data["uniquePointCount"] - previous_point_count
        delta = f"; {point_change:+,} points from previous build"
    print(
        f"Wrote {public_data['uniquePointCount']:,} combined points "
        f"({public_data['photoUniquePointCount']:,} from photographs) and "
        f"{public_data['segmentCount']:,} undated visit segments{delta} to "
        f"{args.destination}"
    )
    print(
        "Set trace_data_revision to "
        f"{public_data['coverage']['through']}-"
        f"{public_data['uniquePointCount']}"
    )


if __name__ == "__main__":
    main()

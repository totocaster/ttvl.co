# /// script
# requires-python = ">=3.11"
# dependencies = ["boto3"]
# ///
"""Publish the Instagram Stories trace's videos and picture sheets to DigitalOcean Spaces.

    uv run tools/stories-media.py            # upload what the Space lacks
    uv run tools/stories-media.py --check    # list it without uploading
    uv run tools/stories-media.py --sheets   # only the picture sheets (after a rebuild)

tools/build-stories.py names every file and writes the private manifest
(.local/stories/manifest.json) of where each one is: the sheets it rendered
into .local/stories/media, and the untouched videos in the export. They go to
the shared Space ttvl-websites (fra1) under ttvl.co/traces/stories/, beside the
walks, each named with a hash of its contents, so every file is cached for a
year as immutable. The videos are uploaded byte for byte: the export is already
H.264 and AAC with its index at the front, which every browser streams. Files
already in the Space are skipped; nothing is ever deleted from it.

The key is the Spaces key scoped to ttvl-websites, read from the macOS Keychain
(service ttvl-websites-spaces) or from SPACES_KEY and SPACES_SECRET, as
tools/walks-media.py reads it. docs/stories.md.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

ROOT = Path(__file__).resolve().parents[1]
BUCKET, REGION = "ttvl-websites", "fra1"
PREFIX = "ttvl.co/traces/stories/"
MANIFEST = ROOT / ".local/stories/manifest.json"
TYPES = {".mp4": "video/mp4", ".webp": "image/webp"}


def credentials():
    if os.environ.get("SPACES_KEY") and os.environ.get("SPACES_SECRET"):
        return os.environ["SPACES_KEY"], os.environ["SPACES_SECRET"]
    found = subprocess.run(["security", "find-generic-password", "-s", "ttvl-websites-spaces"], capture_output=True, text=True)
    account = next((line.split('"')[3] for line in found.stdout.splitlines() if '"acct"' in line), None)
    secret = subprocess.run(["security", "find-generic-password", "-s", "ttvl-websites-spaces", "-w"], capture_output=True, text=True).stdout.strip()
    if not account or not secret:
        sys.exit("No Spaces key: add one to the Keychain as ttvl-websites-spaces, or set SPACES_KEY and SPACES_SECRET.")
    return account, secret


def wanted():
    """Every file the page reads, from the manifest the builder wrote; every name must be in data/stories.json."""
    if not MANIFEST.is_file():
        sys.exit("No manifest: run uv run tools/build-stories.py first.")
    manifest = json.loads(MANIFEST.read_text())
    data = json.loads((ROOT / "data/stories.json").read_text())
    named = {s[7] for s in data["story"]} | set(data["day_sheets"].values()) | {v[0] for v in data["month_sheets"].values()}
    if named != set(manifest):
        sys.exit("The manifest and data/stories.json disagree: run uv run tools/build-stories.py again.")
    missing = [name for name, path in manifest.items() if not Path(path).is_file()]
    if missing:
        sys.exit(f"Missing on disk: {', '.join(missing[:5])}")
    return manifest


def publish(manifest, check=False, log=print):
    key, secret = credentials()
    # The Space sometimes takes a while to answer a large upload: wait longer, and retry.
    config = Config(retries={"max_attempts": 6, "mode": "standard"}, read_timeout=180, connect_timeout=20)
    space = boto3.client("s3", region_name=REGION, endpoint_url=f"https://{REGION}.digitaloceanspaces.com",
                         aws_access_key_id=key, aws_secret_access_key=secret, config=config)
    have = set()
    for page in space.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix=PREFIX):
        have.update(item["Key"] for item in page.get("Contents", []))
    todo = sorted(name for name in manifest if PREFIX + name not in have)
    size = sum(Path(manifest[name]).stat().st_size for name in todo)

    def put(name):
        """Upload one file; a file that still fails after its retries is reported, not fatal."""
        path = Path(manifest[name])
        sha = name.rsplit(".", 2)[1]
        for attempt in range(3):
            try:
                with open(path, "rb") as body:
                    space.put_object(Bucket=BUCKET, Key=PREFIX + name, Body=body, ACL="public-read",
                                     ContentType=TYPES[path.suffix], CacheControl="public, max-age=31536000, immutable",
                                     Metadata={"sha256-10": sha})
                return None
            except (ClientError, BotoCoreError) as error:
                last = error
        return f"{name}: {last}"

    failed = []
    if check:
        for name in todo[:20]:
            log(f"would upload {name}")
    else:
        # Each request waits on the Space more than on the wire: twelve at a time.
        with ThreadPoolExecutor(12) as pool:
            for n, problem in enumerate(pool.map(put, todo), 1):
                if problem:
                    failed.append(problem)
                if n % 100 == 0 or n == len(todo):
                    log(f"uploaded {n - len(failed)} of {len(todo)}", flush=True)
    log(f"{len(manifest) - len(todo)} already in the Space, {len(todo) - len(failed)} {'to upload' if check else 'uploaded'} "
        f"({size / 1e6:.0f} MB)")
    if failed:
        sys.exit(f"{len(failed)} failed (run again to retry them):\n" + "\n".join(failed[:20]))
    return len(todo)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="list what would be uploaded")
    parser.add_argument("--sheets", action="store_true", help="only the picture sheets, not the videos")
    args = parser.parse_args()
    manifest = wanted()
    if args.sheets:
        manifest = {name: path for name, path in manifest.items() if name.endswith(".webp")}
    try:
        publish(manifest, check=args.check)
    except ClientError as error:
        sys.exit(f"Spaces said: {error}")


if __name__ == "__main__":
    main()

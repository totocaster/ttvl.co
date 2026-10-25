#!/usr/bin/env python3
"""Build the Walks reading copy from the untouched vault archive.

Private input manifests stay outside the site. Only explicit public fields are
written; no source paths, journal frontmatter, or camera identifiers are emitted.
Run with --help. The editorial/photo inputs are reviewed selections, not raw dumps.
"""
import argparse
import bisect
from datetime import datetime
import hashlib
import html
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
# The rendered photographs (tools/walks-photos.py) stay private here; the site
# reads them from the shared Space, each named with a hash of its contents so
# a changed picture is a new address (tools/walks-media.py uploads them).
MEDIA = ROOT/'.local/walks/media'
MEDIA_URL = 'https://ttvl-websites.fra1.cdn.digitaloceanspaces.com/ttvl.co/traces/walks/'
EXCLUDED = {'waypoints-only', 'partial-export', 'alternative-export', 'combined-backup', 'cycling'}
# Outings left out by choice, by date: Kuala Lumpur kept eleven points and no
# photographs (removed 2026-10-24).
LEFT_OUT = {'2017-03-25'}
# Recordings that ran on into train rides: only this window of local time is
# the walk, cut at the stations. Keyed by date: (from, to, the walk's note).
WALK_WINDOWS = {
    '2019-03-08': ('11:17:24', '18:39:38', 'The train rides between Kita-Senju and Nikko are cut from the recording.'),
    '2020-10-11': ('00:00:00', '15:21:56', 'The train ride from Kita-Senju around the Yamanote line is cut from the recording.'),
}


def distance(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    d = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 6371000 * 2 * math.asin(min(1, math.sqrt(d)))


def parse_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def route_points(path, day, zone):
    root = ET.parse(path).getroot()
    ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''
    segments, omitted, gaps = [], 0, 0
    for segment in root.findall('.//' + ns + 'trkseg') + root.findall('.//' + ns + 'rte'):
        current = []
        for point in segment:
            if point.tag.split('}')[-1] not in ('trkpt', 'rtept'):
                continue
            t = parse_time(point.findtext(ns + 'time'))
            coord = [round(float(point.attrib['lon']), 6), round(float(point.attrib['lat']), 6)]
            if t and t.astimezone(zone).date().isoformat() != day:
                omitted += 1
                if current:
                    segments.append(current)
                    current = []
                continue
            if current:
                previous = current[-1]
                elapsed = (t - previous['time']).total_seconds() if t and previous['time'] else 0
                # Do not invent connecting paths across long gaps or discontinuities.
                if elapsed < 0 or elapsed > 1800 or distance(previous['coord'], coord) > 2000:
                    segments.append(current)
                    current = []
                    gaps += 1
            current.append({'coord': coord, 'time': t})
        if current:
            segments.append(current)
    return segments, omitted, gaps


def keep_window(segments, zone, start, end):
    """Keep the points whose local time falls between start and end (HH:MM:SS),
    splitting a segment wherever points are dropped."""
    kept = []
    for segment in segments:
        current = []
        for point in segment:
            clock = point['time'].astimezone(zone).strftime('%H:%M:%S') if point['time'] else None
            if clock and start <= clock <= end:
                current.append(point)
            elif current:
                kept.append(current)
                current = []
        if current:
            kept.append(current)
    return kept


def media_name(path):
    """2022-10-01-s0399-01.jpg -> 2022-10-01-s0399-01.c99e1edf2c.jpg"""
    return f'{path.stem}.{hashlib.sha256(path.read_bytes()).hexdigest()[:10]}{path.suffix}'


def media_url(src):
    path = MEDIA/Path(src).name
    if not path.is_file():
        raise SystemExit(f'Missing rendered photograph {path.relative_to(ROOT)}; render it with tools/walks-photos.py')
    return MEDIA_URL + media_name(path)


def clean_text(value):
    value = re.sub(r'\[\[([^]|]+)\|([^]]+)\]\]', r'\2', value or '')
    return re.sub(r'\[\[([^]]+)\]\]', r'\1', value).strip()


def public_photo(photo, segments, zone, sequence):
    coord, method = None, None
    gps = photo.get('gps')
    points = [p for s in segments for p in s]
    if gps and len(gps) == 2 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in gps):
        if -180 <= gps[0] <= 180 and -90 <= gps[1] <= 90 and points:
            if min(distance(gps, p['coord']) for p in points) <= 1000:
                coord, method = [round(x, 6) for x in gps], 'Photo geotag'
    captured = photo.get('capture_time_local')
    if not coord and captured:
        try:
            stamp = parse_time(captured)
            offset = photo.get('timezone_offset')
            if stamp.tzinfo is None:
                stamp = parse_time(captured + offset) if offset else stamp.replace(tzinfo=zone)
            target = stamp.timestamp()
            for segment in segments:
                timed = [p for p in segment if p['time']]
                times = [p['time'].timestamp() for p in timed]
                i = bisect.bisect_left(times, target)
                if 0 < i < len(timed) and 0 < times[i]-times[i-1] <= 300:
                    fraction = (target-times[i-1])/(times[i]-times[i-1])
                    coord = [round(timed[i-1]['coord'][j] + fraction*(timed[i]['coord'][j]-timed[i-1]['coord'][j]), 6) for j in range(2)]
                    method = 'Approximate · camera time matched to track'
                    break
                if i < len(timed) and abs(times[i]-target) <= 30:
                    coord, method = timed[i]['coord'], 'Approximate · camera time matched to track'
                    break
        except (ValueError, TypeError):
            pass
    result = {key: photo[key] for key in ('src','thumb','width','height','alt') if key in photo}
    result.update({'id':f'photo-{sequence}', 'sequence':sequence, 'captured':captured,
                   'time': captured[11:16] if captured else None, 'coordinates':coord,
                   'position_note':method or 'Position not established',
                   'camera':photo.get('model') or None})
    return result


def route_svg(coords, label):
    flat = [p for s in coords for p in s]
    if not flat:
        return ''
    mean = sum(p[1] for p in flat)/len(flat)
    scale_x = math.cos(math.radians(mean))
    xy = [[(p[0]*scale_x, -p[1]) for p in s] for s in coords]
    all_xy = [p for s in xy for p in s]
    lo = [min(p[i] for p in all_xy) for i in (0,1)]
    hi = [max(p[i] for p in all_xy) for i in (0,1)]
    factor = min(680/max(hi[0]-lo[0],.0001), 340/max(hi[1]-lo[1],.0001))
    def pair(p):
        return f'{400+(p[0]-(lo[0]+hi[0])/2)*factor:.2f},{220+(p[1]-(lo[1]+hi[1])/2)*factor:.2f}'
    lines = ''.join(f'<polyline points="{" ".join(pair(p) for p in s)}"/>' for s in xy if len(s)>1)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 440"><title>{html.escape(label)}</title><rect width="800" height="440" fill="#F7F7F7"/><g fill="none" stroke="#000000" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round">{lines}</g><circle cx="{pair(xy[0][0]).split(",")[0]}" cy="{pair(xy[0][0]).split(",")[1]}" r="5" fill="#FF4F00"/></svg>\n'


def build(args):
    manifest_path = Path(args.manifest).expanduser()
    manifest = json.loads(manifest_path.read_text())
    vault = manifest_path.parents[2]
    photos_input = json.loads(Path(args.photos).read_text()) if args.photos else {'records':[]}
    photos = {r['route_sha256']:r for r in photos_input['records']}
    editorial = json.loads(Path(args.editorial).read_text()) if args.editorial else {}
    editorial = editorial.get('walks', editorial)
    walks, features = [], []
    for record in manifest['records']:
        if EXCLUDED.intersection(record['flags']) or record['date'] in LEFT_OUT:
            continue
        day = record['date']
        slug = 's'+record['id'] if record['id'] else {'2024-04-14':'kasai','2024-07-18':'aurelian-walls','2024-07-23':'west-aurelian-walls'}[day]
        region = 'Rome' if 'Rome' in record['title'] else 'Tokyo & Kanto'
        zone = ZoneInfo({'Rome':'Europe/Rome','Tokyo & Kanto':'Asia/Tokyo'}[region])
        source = vault / record['vault_file']
        assert hashlib.sha256(source.read_bytes()).hexdigest() == record['sha256'], source
        segments, omitted, gaps = route_points(source,day,zone)
        window = WALK_WINDOWS.get(day)
        if window:
            segments = keep_window(segments, zone, window[0], window[1])
            # Breaks inside the walk, by route_points' rule; segment seams are not breaks.
            gaps = sum(1 for a, b in zip(segments, segments[1:])
                       if (a[-1]['time'] and b[0]['time'] and (b[0]['time']-a[-1]['time']).total_seconds() > 1800)
                       or distance(a[-1]['coord'], b[0]['coord']) > 2000)
        coords = [[p['coord'] for p in s] for s in segments]
        flat = [p for s in segments for p in s]
        length = sum(distance(a['coord'],b['coord']) for s in segments for a,b in zip(s,s[1:])) / 1000
        bounds = [[min(p['coord'][i] for p in flat) for i in (0,1)], [max(p['coord'][i] for p in flat) for i in (0,1)]] if flat else None
        flags = record['flags']
        sparse = any(f in flags for f in ('incomplete-sparse','incomplete-stub'))
        travel = 'travel-included' in flags and not window
        label ='Travel included' if travel else ('Sparse recording' if sparse else ('Partial recording' if 'incomplete-recording' in flags else 'Recorded route'))
        notes = []
        if omitted:
            notes.append('This view isolates the walk date from a file containing other days.')
        if sparse:
            notes.append('Only a few locations were recorded. They do not establish the full route.')
        if travel:
            notes.append('The recording includes transport as well as walking; no walking distance is inferred.')
        if window:
            notes.append(window[2])
        if 'incomplete-recording' in flags:
            notes.append('The recording ends before the photographic outing does.')
        if 'photo-date-conflict' in flags:
            notes.append('The journal and camera dates disagree; photographs await a date check.')
        if gaps:
            notes.append('Breaks in the recording are left open on the map.')
        if 'location-label-mismatch' in flags:
            notes.append('The photo session is labeled Hanno; the journal and track use Chichibu.')
        title = re.sub(r'^\d{4}\s+', '', record['title'])
        title = re.sub(r'\s+\([^)]*\)$', '', title).replace('Disnayland','Disneyland').replace('Shimo-kitasaza','Shimokitazawa')
        title = title.replace('Hanno Hike / GPX titled Chichibu','Chichibu / Hanno Hike').replace('Kawagoe / Kanagoe in Pandemic','Kawagoe in the Pandemic')
        item = editorial.get(day,{})
        # The editorial title wins: each is the route, Start to End (docs/walks.md, Titles).
        title = item.get('title') or title
        selection = photos.get(record['sha256'],{})
        if selection.get('is_film') and any('other scenes' in warning.lower() for warning in selection.get('warnings',[])):
            notes.append('The film rolls also contain other scenes; this selection keeps the walk photographs.')
        images = [public_photo(p,segments,zone,i+1) for i,p in enumerate(selection.get('images',[]))]
        for image in images:
            image['src'], image['thumb'] = media_url(image['src']), media_url(image['thumb'])
        # When the recording ran, local clock: the walk's own span.
        times = [p['time'] for p in flat if p['time']]
        started, ended = (min(times).astimezone(zone), max(times).astimezone(zone)) if times else (None, None)
        walk = {'id':slug,'title':title,'date':day,'year':day[:4],'region':region,
                'distance_km':round(length,1) if not (sparse or travel) else None,
                'recording':label,'recording_notes':notes,'bounds':bounds,
                'started':started.strftime('%H:%M') if started else None,'ended':ended.strftime('%H:%M') if ended else None,
                'minutes':round((ended-started).total_seconds()/60) if started else None,
                'weather':item.get('weather') or (item.get('journal') or {}).get('weather') or None,
                'film':bool(selection.get('is_film')),
                # A film walk's camera, which its scans cannot carry (editorial `camera`).
                'camera':item.get('camera'),
                'video':item.get('video'),
                'photos':images,'journal':item.get('journal'), 'summary':item.get('summary',''),
                'places':item.get('places',[]),'links':item.get('links',[]),
                'route_preview':f'/visuals/traces/walks/routes/{slug}.svg'}
        if walk['journal']:
            walk['journal']['paragraphs'] = [clean_text(s) for s in walk['journal']['paragraphs']]
        walks.append(walk)
        geometry = {'type':'MultiPoint','coordinates':[p['coord'] for p in flat]} if sparse else {'type':'MultiLineString','coordinates':[s for s in coords if len(s)>1]}
        features.append({'type':'Feature','id':slug,'properties':{'walk':slug,'title':title,'region':region,'year':day[:4]},'geometry':geometry})
        target = ROOT/'static'/walk['route_preview'].lstrip('/')
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(route_svg(coords,title))
    walks.sort(key=lambda w:w['date'],reverse=True)
    assert len(walks)==41 and len({w['id'] for w in walks})==41
    payload = {'default_walk':'s0399','walks':walks}
    (ROOT/'data/walks.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    target = ROOT/'static/traces/walks/routes.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n')
    print(json.dumps({'walks':len(walks),'photos':sum(len(w['photos']) for w in walks),'positioned_photos':sum(bool(p['coordinates']) for w in walks for p in w['photos']),'journals':sum(bool(w['journal']) for w in walks)},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True,help='Private vault manifest.json')
    parser.add_argument('--photos',required=True,help='Private reviewed photo export manifest')
    parser.add_argument('--editorial',default=str(ROOT/'data/walks-editorial.json'),help='Reviewed excerpts and public links, keyed by walk date')
    build(parser.parse_args())

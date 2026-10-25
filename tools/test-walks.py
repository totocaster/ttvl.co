#!/usr/bin/env python3
"""Check the archive boundaries that must survive future rebuilds."""
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location('walks', Path(__file__).with_name('build-walks.py'))
walks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(walks)


class RouteBoundaries(unittest.TestCase):
    def setUp(self):
        self.zone = ZoneInfo('Asia/Tokyo')
        self.points = [[
            {'coord': [139.0, 35.0], 'time': walks.parse_time('2022-10-01T00:00:00Z')},
            {'coord': [139.001, 35.0], 'time': walks.parse_time('2022-10-01T00:04:00Z')},
        ]]

    def test_local_day_and_gaps_are_preserved(self):
        xml = '<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>'
        for lon, time in [(139, '2022-09-30T14:59:00Z'), (139, '2022-09-30T15:01:00Z'), (139.001, '2022-09-30T15:02:00Z'), (139.002, '2022-09-30T16:02:00Z'), (140, '2022-09-30T16:03:00Z')]:
            xml += f'<trkpt lon="{lon}" lat="35"><time>{time}</time></trkpt>'
        xml += '</trkseg></trk></gpx>'
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder)/'test.gpx'
            file.write_text(xml)
            segments, omitted, gaps = walks.route_points(file, '2022-10-01', self.zone)
        self.assertEqual(omitted, 1)
        self.assertEqual(gaps, 2)
        self.assertEqual([len(segment) for segment in segments], [2, 1, 1])

    def test_walk_window_cuts_the_ride_and_splits(self):
        at = lambda clock: {'coord': [139.0, 35.0], 'time': walks.parse_time(f'2022-10-01T{clock}+09:00')}
        segments = [[at('08:00:00'), at('09:00:00'), at('09:30:00'), at('11:00:00'), at('12:00:00')]]
        kept = walks.keep_window(segments, self.zone, '08:30:00', '10:00:00')
        self.assertEqual([[p['time'].strftime('%H:%M') for p in s] for s in kept], [['09:00', '09:30']])
        segments = [[at('09:00:00'), at('11:00:00'), at('09:45:00')]]
        self.assertEqual(len(walks.keep_window(segments, self.zone, '08:30:00', '10:00:00')), 2)

    def test_camera_time_is_approximate(self):
        photo = walks.public_photo({'capture_time_local': '2022-10-01T09:02:00'}, self.points, self.zone, 1)
        self.assertEqual(photo['coordinates'], [139.0005, 35.0])
        self.assertTrue(photo['position_note'].startswith('Approximate'))

    def test_no_position_across_gap_or_outside_recording(self):
        separated = [[self.points[0][0]], [self.points[0][1]]]
        photo = {'capture_time_local': '2022-10-01T09:02:00', 'gps': [12.5, 41.9]}
        self.assertIsNone(walks.public_photo(photo, separated, self.zone, 1)['coordinates'])
        photo['capture_time_local'] = '2022-10-01T17:02:00'
        self.assertIsNone(walks.public_photo(photo, self.points, self.zone, 1)['coordinates'])

    def test_geotag_and_unlocated_film(self):
        tagged = walks.public_photo({'gps': [139.0005, 35.0]}, self.points, self.zone, 1)
        self.assertEqual(tagged['position_note'], 'Photo geotag')
        film = walks.public_photo({'source': '/private/film.tif', 'source_sha256': 'private'}, self.points, self.zone, 1)
        self.assertIsNone(film['coordinates'])
        self.assertIsNone(film['captured'])
        self.assertNotIn('source', film)
        self.assertNotIn('source_sha256', film)

    def test_reading_copy_is_complete_and_resolvable(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root/'data/walks.json').read_text())
        routes = json.loads((root/'static/traces/walks/routes.json').read_text())
        ids = [walk['id'] for walk in data['walks']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), {feature['properties']['walk'] for feature in routes['features']})
        self.assertIn(data['default_walk'], ids)
        for walk in data['walks']:
            self.assertTrue((root/'static'/walk['route_preview'].lstrip('/')).is_file())
            for photo in walk['photos']:
                for key in ('src', 'thumb'):
                    # Served from the Space under a name carrying its contents' hash.
                    self.assertRegex(photo[key], r'^' + re.escape(walks.MEDIA_URL) + r'[\w-]+\.[0-9a-f]{10}\.jpg$')
                self.assertTrue(photo['alt'])
                self.assertLessEqual(max(photo['width'], photo['height']), 1600)
            if walk['recording'] in ('Travel included', 'Sparse recording'):
                self.assertIsNone(walk['distance_km'])
        serialized = json.dumps(data)
        for private in ('/Users/', '/Volumes/', 'source_sha256', 'source_note'):
            self.assertNotIn(private, serialized)

    def test_every_recorded_walk_has_its_day(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root/'data/walks.json').read_text())
        days = json.loads((root/'static/traces/walks/days.json').read_text())['walks']
        recorded = {w['id'] for w in data['walks'] if w['recording'] != 'Sparse recording'}
        self.assertEqual(set(days), recorded)
        for walk_id, day in days.items():
            samples = day['samples']
            self.assertGreater(len(samples), 2, walk_id)
            self.assertEqual([s[2] for s in samples], sorted(s[2] for s in samples), walk_id)
            times = [s[3] for s in samples if s[3] is not None]
            self.assertEqual(times[0], 0, walk_id)
            self.assertEqual(max(times), day['T'], walk_id)
            self.assertLessEqual(day['low'], day['high'], walk_id)
            for a, b, state in day['runs']:
                self.assertLessEqual(a, b, walk_id)
                self.assertIn(state, 'wsg')
        serialized = json.dumps(days)
        for private in ('/Users/', '/Volumes/', '.DNG', 'sha256'):
            self.assertNotIn(private, serialized)


if __name__ == '__main__':
    unittest.main()

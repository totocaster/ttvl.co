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

    def test_gps_repair_keeps_time_and_requires_continuous_anchors(self):
        # The spike is within the parser's 2 km gap limit. These UTC times
        # bracket the reviewed 11:52 local spike, with a real gap afterwards.
        points = [
            (139.799, '02:50:00'), (139.8, '02:51:18'),
            (139.79, '02:51:48'), (139.80061, '02:52:19'),
            (139.801, '02:53:00'), (139.802, '03:54:00'),
        ]
        xml = '<gpx><trk><trkseg>' + ''.join(
            f'<trkpt lon="{lon}" lat="35.7"><time>2023-10-22T{t}Z</time></trkpt>'
            for lon, t in points) + '</trkseg></trk></gpx>'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'spike.gpx'
            path.write_text(xml)
            segments, omitted, gaps = walks.reading_route(path, '2023-10-22', self.zone)
            self.assertEqual(path.read_text(), xml)
            self.assertEqual((omitted, gaps), (0, 1))
            self.assertEqual([len(s) for s in segments], [5, 1])
            self.assertEqual(segments[0][2]['coord'], [139.8003, 35.7])
            self.assertEqual([p['time'].strftime('%H:%M:%S') for s in segments for p in s], [t for _, t in points])
            self.assertEqual(segments[0][0]['coord'], [139.799, 35.7])
            self.assertEqual(segments[0][-1]['coord'], [139.801, 35.7])
            # An export seam inside the repair must stay a gap, not become
            # a fabricated connecting path.
            path.write_text(xml.replace('<trkpt lon="139.80061"', '</trkseg><trkseg><trkpt lon="139.80061"'))
            with self.assertRaisesRegex(ValueError, 'anchors in one segment'):
                walks.reading_route(path, '2023-10-22', self.zone)

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
            walk = next(w for w in data['walks'] if w['id'] == walk_id)
            # The map's metadata and independently built timeline must use
            # the same local window and corrected distance after a rebuild.
            clock = lambda m: f'{int(m) // 60:02d}:{int(m) % 60:02d}'
            self.assertEqual(clock(day['t0']), walk['started'], walk_id)
            self.assertEqual(clock(day['t0'] + day['T'] / 60), walk['ended'], walk_id)
            self.assertEqual(round(day['T'] / 60), walk['minutes'], walk_id)
            if walk['distance_km'] is not None:
                self.assertAlmostEqual(day['samples'][-1][2] / 1000, walk['distance_km'], delta=0.051, msg=walk_id)
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

    def test_reviewed_cleanup_is_in_the_reading_copy(self):
        root = Path(__file__).resolve().parents[1]
        data = {w['id']: w for w in json.loads((root/'data/walks.json').read_text())['walks']}
        # Reviewed outcomes: three true endings and three GPS detours removed.
        for walk_id, ended, km in [
            ('s0273', '13:49', 9.8), ('s0313', '11:31', 2.3),
            ('s0395', '11:34', 12.5), ('s0438', '13:20', 15.7),
            ('west-aurelian-walls', '11:34', 3.7), ('s0498', '16:59', 6.4),
        ]:
            with self.subTest(walk=walk_id):
                self.assertEqual(data[walk_id]['ended'], ended)
                self.assertEqual(data[walk_id]['distance_km'], km)


if __name__ == '__main__':
    unittest.main()

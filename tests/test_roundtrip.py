import tempfile
import unittest
from datetime import date, time
from pathlib import Path

from fixtures_convert.csv_format import read_csv, write_csv
from fixtures_convert.ics_format import read_ics, write_ics
from fixtures_convert.json_format import read_json, write_json
from fixtures_convert.models import Fixture


SAMPLE_FIXTURES = [
    Fixture(
        match_date=date(2026, 8, 29),
        home="Riverside FC",
        away="Oakfield United",
        kickoff=time(15, 0),
        venue="Riverside Park",
        competition="League Division 2",
    ),
    Fixture(
        match_date=date(2026, 9, 5),
        home="Oakfield United",
        away="Riverside FC",
        kickoff=None,
        venue="",
        competition="",
    ),
    Fixture(
        match_date=date(2026, 9, 12),
        home="St. John's, Wednesday",
        away="Ashby & District",
        kickoff=time(19, 45),
        venue="Ground 2; Pitch A",
        competition="Cup Round 1 \\ Replay",
    ),
    Fixture(
        match_date=date(2026, 9, 1),
        home="Riverside FC 5s",
        away="The Anchor 5s",
        kickoff=time(20, 0),
        venue="Sports Hall",
        competition="Tuesday Night League",
        repeat="FREQ=WEEKLY;COUNT=10",
    ),
]


class CsvRoundTripTests(unittest.TestCase):
    def test_write_then_read_is_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.csv"
            write_csv(path, SAMPLE_FIXTURES)
            self.assertEqual(read_csv(path), SAMPLE_FIXTURES)


class IcsRoundTripTests(unittest.TestCase):
    def test_write_then_read_is_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.ics"
            write_ics(path, SAMPLE_FIXTURES)
            self.assertEqual(read_ics(path), SAMPLE_FIXTURES)

    def test_all_day_fixture_has_no_kickoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.ics"
            all_day = [SAMPLE_FIXTURES[1]]
            write_ics(path, all_day)
            self.assertIsNone(read_ics(path)[0].kickoff)

    def test_uids_are_stable_across_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.ics"
            second = Path(tmp) / "second.ics"
            write_ics(first, SAMPLE_FIXTURES)
            write_ics(second, SAMPLE_FIXTURES)
            uids = lambda text: [line for line in text.splitlines() if line.startswith("UID:")]
            self.assertEqual(
                uids(first.read_text(encoding="utf-8")),
                uids(second.read_text(encoding="utf-8")),
            )

    def test_repeat_becomes_an_rrule_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.ics"
            repeating = [SAMPLE_FIXTURES[3]]
            write_ics(path, repeating)
            text = path.read_text(encoding="utf-8")
            self.assertIn("RRULE:FREQ=WEEKLY;COUNT=10", text)

    def test_fixture_without_repeat_gets_no_rrule_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.ics"
            write_ics(path, [SAMPLE_FIXTURES[0]])
            self.assertNotIn("RRULE", path.read_text(encoding="utf-8"))

    def test_tz_flag_does_not_change_what_comes_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.ics"
            write_ics(path, SAMPLE_FIXTURES, tz="Europe/London")
            self.assertEqual(read_ics(path), SAMPLE_FIXTURES)


class JsonRoundTripTests(unittest.TestCase):
    def test_write_then_read_is_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.json"
            write_json(path, SAMPLE_FIXTURES)
            self.assertEqual(read_json(path), SAMPLE_FIXTURES)

    def test_missing_time_and_repeat_are_null_not_empty_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "season.json"
            write_json(path, [SAMPLE_FIXTURES[1]])
            text = path.read_text(encoding="utf-8")
            self.assertIn('"time": null', text)
            self.assertIn('"repeat": null', text)


class CrossFormatRoundTripTests(unittest.TestCase):
    def test_csv_to_ics_to_csv_preserves_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "season.csv"
            ics_path = Path(tmp) / "season.ics"
            csv_path_again = Path(tmp) / "season2.csv"

            write_csv(csv_path, SAMPLE_FIXTURES)
            fixtures = read_csv(csv_path)
            write_ics(ics_path, fixtures)
            fixtures = read_ics(ics_path)
            write_csv(csv_path_again, fixtures)

            self.assertEqual(read_csv(csv_path_again), SAMPLE_FIXTURES)

    def test_csv_to_json_to_ics_preserves_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "season.csv"
            json_path = Path(tmp) / "season.json"
            ics_path = Path(tmp) / "season.ics"

            write_csv(csv_path, SAMPLE_FIXTURES)
            fixtures = read_csv(csv_path)
            write_json(json_path, fixtures)
            fixtures = read_json(json_path)
            write_ics(ics_path, fixtures)

            self.assertEqual(read_ics(ics_path), SAMPLE_FIXTURES)


if __name__ == "__main__":
    unittest.main()

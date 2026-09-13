import unittest

from fixtures_convert.recurrence import validate_rrule


class ValidateRruleTests(unittest.TestCase):
    def test_weekly_count_is_valid(self):
        self.assertIsNone(validate_rrule("FREQ=WEEKLY;COUNT=10"))

    def test_weekly_until_date_is_valid(self):
        self.assertIsNone(validate_rrule("FREQ=WEEKLY;UNTIL=20261215"))

    def test_weekly_until_datetime_is_valid(self):
        self.assertIsNone(validate_rrule("FREQ=WEEKLY;UNTIL=20261215T200000Z"))

    def test_interval_is_allowed(self):
        self.assertIsNone(validate_rrule("FREQ=WEEKLY;INTERVAL=2;COUNT=5"))

    def test_missing_freq_is_rejected(self):
        self.assertIn("FREQ", validate_rrule("COUNT=10"))

    def test_unsupported_freq_is_rejected(self):
        self.assertIn("SECONDLY", validate_rrule("FREQ=SECONDLY"))

    def test_count_and_until_together_is_rejected(self):
        error = validate_rrule("FREQ=WEEKLY;COUNT=5;UNTIL=20261215")
        self.assertIn("COUNT", error)
        self.assertIn("UNTIL", error)

    def test_non_numeric_count_is_rejected(self):
        self.assertIn("COUNT", validate_rrule("FREQ=WEEKLY;COUNT=ten"))

    def test_non_numeric_interval_is_rejected(self):
        self.assertIn("INTERVAL", validate_rrule("FREQ=WEEKLY;INTERVAL=twice"))

    def test_malformed_until_is_rejected(self):
        self.assertIn("UNTIL", validate_rrule("FREQ=WEEKLY;UNTIL=15-12-2026"))

    def test_malformed_part_without_equals_is_rejected(self):
        self.assertIn("garbage", validate_rrule("FREQ=WEEKLY;garbage"))


if __name__ == "__main__":
    unittest.main()

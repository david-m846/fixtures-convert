import unittest
from datetime import date

from fixtures_convert.models import Fixture
from fixtures_convert.validate import validate


def fx(match_date, home, away):
    return Fixture(match_date=match_date, home=home, away=away)


class ValidateTests(unittest.TestCase):
    def test_clean_list_has_no_issues(self):
        fixtures = [
            fx(date(2026, 8, 29), "Riverside FC", "Oakfield United"),
            fx(date(2026, 9, 5), "Oakfield United", "Riverside FC"),
        ]
        self.assertEqual(validate(fixtures), [])

    def test_flags_exact_duplicate(self):
        fixtures = [
            fx(date(2026, 8, 29), "Riverside FC", "Oakfield United"),
            fx(date(2026, 8, 29), "Riverside FC", "Oakfield United"),
        ]
        issues = validate(fixtures)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].row, 2)
        self.assertIn("duplicate of fixture 1", issues[0].message)

    def test_same_teams_different_date_is_not_a_duplicate(self):
        fixtures = [
            fx(date(2026, 8, 29), "Riverside FC", "Oakfield United"),
            fx(date(2026, 9, 5), "Riverside FC", "Oakfield United"),
        ]
        self.assertEqual(validate(fixtures), [])

    def test_flags_team_playing_itself(self):
        issues = validate([fx(date(2026, 8, 29), "Riverside FC", "Riverside FC")])
        self.assertEqual(len(issues), 1)
        self.assertIn("playing itself", issues[0].message)

    def test_flags_missing_team(self):
        issues = validate([fx(date(2026, 8, 29), "Riverside FC", "")])
        self.assertEqual(len(issues), 1)
        self.assertIn("missing home or away team", issues[0].message)

    def test_row_numbers_are_one_based_positions_in_the_list(self):
        fixtures = [
            fx(date(2026, 8, 29), "Riverside FC", "Oakfield United"),
            fx(date(2026, 9, 5), "Ashby & District", "Ashby & District"),
        ]
        issues = validate(fixtures)
        self.assertEqual(issues[0].row, 2)


if __name__ == "__main__":
    unittest.main()

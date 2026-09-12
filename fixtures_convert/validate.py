from dataclasses import dataclass
from typing import List

from .models import Fixture


@dataclass
class ValidationIssue:
    # 1-based position in the fixture list, not the source file's line number -
    # csv and ics don't agree on what a "line" is, but "the third fixture" means
    # the same thing in both.
    row: int
    message: str

    def __str__(self) -> str:
        return f"fixture {self.row}: {self.message}"


def validate(fixtures: List[Fixture]) -> List[ValidationIssue]:
    issues = []
    seen = {}
    for i, fx in enumerate(fixtures, start=1):
        if not fx.home or not fx.away:
            issues.append(ValidationIssue(i, "missing home or away team"))
        elif fx.home == fx.away:
            issues.append(ValidationIssue(i, f"{fx.home} is listed playing itself"))

        key = (fx.match_date, fx.home, fx.away)
        prior = seen.get(key)
        if prior is not None:
            issues.append(ValidationIssue(
                i, f"duplicate of fixture {prior} ({fx.home} vs {fx.away} on {fx.match_date})"
            ))
        else:
            seen[key] = i
    return issues

from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class Fixture:
    """One match. Date, home and away are the only things every fixture
    list actually agrees on; kickoff time, venue and competition are
    routinely missing from one side or the other."""

    match_date: date
    home: str
    away: str
    kickoff: Optional[time] = None
    venue: str = ""
    competition: str = ""

    @property
    def summary(self) -> str:
        return f"{self.home} vs {self.away}"

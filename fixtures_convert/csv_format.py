import csv
from datetime import date, datetime
from typing import List

from .models import Fixture

FIELDNAMES = ["date", "time", "home", "away", "venue", "competition"]


def read_csv(path) -> List[Fixture]:
    fixtures = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):
            raw_date = (row.get("date") or "").strip()
            try:
                match_date = date.fromisoformat(raw_date)
            except ValueError as exc:
                raise ValueError(f"row {row_num}: bad date {raw_date!r}, want YYYY-MM-DD") from exc

            raw_time = (row.get("time") or "").strip()
            kickoff = datetime.strptime(raw_time, "%H:%M").time() if raw_time else None

            fixtures.append(Fixture(
                match_date=match_date,
                home=(row.get("home") or "").strip(),
                away=(row.get("away") or "").strip(),
                kickoff=kickoff,
                venue=(row.get("venue") or "").strip(),
                competition=(row.get("competition") or "").strip(),
            ))
    return fixtures


def write_csv(path, fixtures: List[Fixture]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for fx in fixtures:
            writer.writerow({
                "date": fx.match_date.isoformat(),
                "time": fx.kickoff.strftime("%H:%M") if fx.kickoff else "",
                "home": fx.home,
                "away": fx.away,
                "venue": fx.venue,
                "competition": fx.competition,
            })

import json
from datetime import date, datetime
from typing import List

from .models import Fixture


def _fixture_to_dict(fx: Fixture) -> dict:
    return {
        "date": fx.match_date.isoformat(),
        "time": fx.kickoff.strftime("%H:%M") if fx.kickoff else None,
        "home": fx.home,
        "away": fx.away,
        "venue": fx.venue,
        "competition": fx.competition,
        "repeat": fx.repeat,
    }


def _dict_to_fixture(obj: dict, index: int) -> Fixture:
    raw_date = obj.get("date")
    if not raw_date:
        raise ValueError(f"fixture {index}: missing date")
    try:
        match_date = date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValueError(f"fixture {index}: bad date {raw_date!r}, want YYYY-MM-DD") from exc

    raw_time = obj.get("time")
    kickoff = None
    if raw_time:
        try:
            kickoff = datetime.strptime(raw_time, "%H:%M").time()
        except ValueError as exc:
            raise ValueError(f"fixture {index}: bad time {raw_time!r}, want HH:MM") from exc

    return Fixture(
        match_date=match_date,
        home=(obj.get("home") or "").strip(),
        away=(obj.get("away") or "").strip(),
        kickoff=kickoff,
        venue=obj.get("venue") or "",
        competition=obj.get("competition") or "",
        repeat=obj.get("repeat") or None,
    )


def write_json(path, fixtures: List[Fixture]) -> None:
    data = [_fixture_to_dict(fx) for fx in fixtures]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def read_json(path) -> List[Fixture]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("top-level JSON value must be a list of fixtures")

    fixtures = []
    for i, obj in enumerate(data, start=1):
        if not isinstance(obj, dict):
            raise ValueError(f"fixture {i}: expected an object")
        fixtures.append(_dict_to_fixture(obj, i))
    return fixtures

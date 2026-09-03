import uuid
import zoneinfo
from datetime import datetime, timedelta
from typing import List, Optional

from .models import Fixture

# fixed namespace so re-converting the same fixtures produces the same UIDs
# instead of a fresh event on every run
UID_NAMESPACE = uuid.UUID("c9c8f14e-6b1d-4b3a-9b0a-3f2a7e6d1c44")

DEFAULT_DURATION = timedelta(hours=2)


def _uid_for(fx: Fixture) -> str:
    key = f"{fx.match_date}|{fx.kickoff}|{fx.home}|{fx.away}"
    return str(uuid.uuid5(UID_NAMESPACE, key))


def _fold(line: str) -> str:
    # RFC 5545: lines over 75 octets get folded, continuation starts with a space
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(" " + rest[:74])
        rest = rest[74:]
    return "\r\n".join(parts)


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")


TEXT_PROPERTIES = ("SUMMARY", "LOCATION", "DESCRIPTION")


def _unescape(text: str) -> str:
    # inverse of _escape, plus \n / \N since RFC 5545 TEXT values escape
    # embedded newlines that way
    out = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            out.append("\n" if nxt in ("n", "N") else nxt)
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def write_ics(path, fixtures: List[Fixture], tz: Optional[str] = None) -> None:
    if tz:
        # fail before writing anything rather than leave a half-written file
        # behind because of a typo in the zone name
        zoneinfo.ZoneInfo(tz)
    tzid_param = f";TZID={tz}" if tz else ""

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//fixtures-convert//EN"]
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for fx in fixtures:
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{_uid_for(fx)}")
        lines.append(f"DTSTAMP:{stamp}")
        if fx.kickoff:
            start = datetime.combine(fx.match_date, fx.kickoff)
            end = start + DEFAULT_DURATION
            lines.append(f"DTSTART{tzid_param}:{start.strftime('%Y%m%dT%H%M%S')}")
            lines.append(f"DTEND{tzid_param}:{end.strftime('%Y%m%dT%H%M%S')}")
        else:
            end_date = fx.match_date + timedelta(days=1)
            lines.append(f"DTSTART;VALUE=DATE:{fx.match_date.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{end_date.strftime('%Y%m%d')}")
        lines.append(_fold(f"SUMMARY:{_escape(fx.summary)}"))
        if fx.venue:
            lines.append(_fold(f"LOCATION:{_escape(fx.venue)}"))
        if fx.competition:
            lines.append(_fold(f"DESCRIPTION:{_escape(fx.competition)}"))
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def _unfold(raw: str) -> List[str]:
    raw = raw.replace("\r\n", "\n")
    lines = []
    for line in raw.split("\n"):
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        elif line:
            lines.append(line)
    return lines


def _parse_property(line: str):
    name_part, _, value = line.partition(":")
    return name_part.split(";")[0].upper(), value


def _parse_dt(value: str):
    value = value.strip()
    if "T" in value:
        dt = datetime.strptime(value.rstrip("Z"), "%Y%m%dT%H%M%S")
        return dt.date(), dt.time()
    return datetime.strptime(value, "%Y%m%d").date(), None


def read_ics(path) -> List[Fixture]:
    with open(path, encoding="utf-8") as f:
        lines = _unfold(f.read())

    fixtures = []
    current = None
    for line in lines:
        name, value = _parse_property(line)
        if name == "BEGIN" and value == "VEVENT":
            current = {}
        elif name == "END" and value == "VEVENT":
            if current is not None and "DTSTART" in current:
                match_date, kickoff = _parse_dt(current["DTSTART"])
                home, _, away = current.get("SUMMARY", " vs ").partition(" vs ")
                fixtures.append(Fixture(
                    match_date=match_date,
                    home=home.strip(),
                    away=away.strip(),
                    kickoff=kickoff,
                    venue=current.get("LOCATION", ""),
                    competition=current.get("DESCRIPTION", ""),
                ))
            current = None
        elif current is not None and name in TEXT_PROPERTIES:
            current[name] = _unescape(value)
        elif current is not None and name == "DTSTART":
            current[name] = value
    return fixtures

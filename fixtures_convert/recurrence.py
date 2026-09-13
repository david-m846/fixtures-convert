from datetime import datetime
from typing import Optional

# Fixtures only need a handful of RFC 5545 RRULE parts. BYDAY, BYMONTH etc.
# are legal RRULE syntax but nothing here generates or needs them, so a
# value using them is passed through untouched rather than rejected.
FREQ_VALUES = {"DAILY", "WEEKLY", "MONTHLY", "YEARLY"}


def validate_rrule(value: str) -> Optional[str]:
    """Return an error message if value isn't a usable RRULE, else None."""
    parts = {}
    for chunk in value.split(";"):
        if not chunk:
            continue
        key, sep, val = chunk.partition("=")
        if not sep:
            return f"malformed RRULE part {chunk!r}"
        parts[key.upper()] = val

    freq = parts.get("FREQ")
    if freq is None:
        return "RRULE is missing FREQ"
    if freq not in FREQ_VALUES:
        return f"unsupported FREQ {freq!r}"

    if "INTERVAL" in parts and not parts["INTERVAL"].isdigit():
        return f"INTERVAL must be a positive integer, got {parts['INTERVAL']!r}"

    if "COUNT" in parts and "UNTIL" in parts:
        return "RRULE cannot have both COUNT and UNTIL"

    if "COUNT" in parts and not parts["COUNT"].isdigit():
        return f"COUNT must be a positive integer, got {parts['COUNT']!r}"

    if "UNTIL" in parts:
        until = parts["UNTIL"]
        try:
            if "T" in until:
                datetime.strptime(until.rstrip("Z"), "%Y%m%dT%H%M%S")
            else:
                datetime.strptime(until, "%Y%m%d")
        except ValueError:
            return f"UNTIL is not a valid RRULE date(-time), got {until!r}"

    return None

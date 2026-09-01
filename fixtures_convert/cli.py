import argparse
import sys
import zoneinfo
from pathlib import Path
from typing import Optional

from .csv_format import read_csv, write_csv
from .ics_format import read_ics, write_ics

READERS = {".csv": read_csv, ".ics": read_ics}
WRITERS = {".csv": write_csv, ".ics": write_ics}


def convert(src: Path, dst: Path, tz: Optional[str] = None) -> int:
    try:
        reader = READERS[src.suffix.lower()]
    except KeyError:
        raise SystemExit(f"don't know how to read {src.suffix or '(no extension)'} files")
    dst_suffix = dst.suffix.lower()
    if dst_suffix not in WRITERS:
        raise SystemExit(f"don't know how to write {dst.suffix or '(no extension)'} files")
    if tz and dst_suffix != ".ics":
        raise SystemExit("--tz only applies when writing .ics files")

    fixtures = reader(src)
    if dst_suffix == ".ics":
        write_ics(dst, fixtures, tz=tz)
    else:
        write_csv(dst, fixtures)
    return len(fixtures)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fixtures-convert",
        description="convert sports fixtures between CSV and iCalendar (.ics)",
    )
    parser.add_argument("source", type=Path, help="input file (.csv or .ics)")
    parser.add_argument("dest", type=Path, help="output file (.csv or .ics)")
    parser.add_argument(
        "--tz",
        metavar="ZONE",
        help="IANA timezone name to write timed fixtures with (e.g. Europe/London), "
             "only valid when the destination is .ics; times are written floating, "
             "with no offset, if this is omitted",
    )
    args = parser.parse_args(argv)

    try:
        count = convert(args.source, args.dest, tz=args.tz)
    except zoneinfo.ZoneInfoNotFoundError:
        raise SystemExit(f"unknown timezone {args.tz!r}")
    print(f"wrote {count} fixture(s) to {args.dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

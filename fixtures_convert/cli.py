import argparse
import sys
from pathlib import Path

from .csv_format import read_csv, write_csv
from .ics_format import read_ics, write_ics

READERS = {".csv": read_csv, ".ics": read_ics}
WRITERS = {".csv": write_csv, ".ics": write_ics}


def convert(src: Path, dst: Path) -> int:
    try:
        reader = READERS[src.suffix.lower()]
    except KeyError:
        raise SystemExit(f"don't know how to read {src.suffix or '(no extension)'} files")
    try:
        writer = WRITERS[dst.suffix.lower()]
    except KeyError:
        raise SystemExit(f"don't know how to write {dst.suffix or '(no extension)'} files")

    fixtures = reader(src)
    writer(dst, fixtures)
    return len(fixtures)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fixtures-convert",
        description="convert sports fixtures between CSV and iCalendar (.ics)",
    )
    parser.add_argument("source", type=Path, help="input file (.csv or .ics)")
    parser.add_argument("dest", type=Path, help="output file (.csv or .ics)")
    args = parser.parse_args(argv)

    count = convert(args.source, args.dest)
    print(f"wrote {count} fixture(s) to {args.dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

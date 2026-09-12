# fixtures-convert

Most amateur leagues publish their fixture list as a spreadsheet export
(CSV), because that's what the fixtures secretary knows how to produce.
Calendar apps don't read CSV, they read iCalendar (.ics). So every season
you end up either retyping thirty match dates into your phone by hand, or
hunting for some web tool that wants to see your whole calendar to do a
five-second conversion.

This is a small command-line tool that converts fixture lists between the
two formats, in both directions, with no network access and no dependencies
beyond the Python standard library.

## Usage

```
python -m fixtures_convert.cli season.csv season.ics
python -m fixtures_convert.cli season.ics season.csv
```

Or, if installed (`pip install -e .`), the `fixtures-convert` command does
the same thing:

```
fixtures-convert season.csv season.ics
```

The format is chosen from each file's extension.

By default, kickoff times are written floating (no timezone offset), which
means the calendar app applies whatever timezone it's already set to. Pass
`--tz` with an IANA zone name to pin the fixtures to a specific zone instead:

```
fixtures-convert season.csv season.ics --tz Europe/London
```

`--tz` only makes sense when writing `.ics`; it's rejected if the destination
is `.csv`.

Every conversion is checked for duplicate fixtures (same date and teams),
teams listed playing themselves, and rows missing a team name. Problems are
printed as warnings but don't stop the conversion by default; pass `--strict`
to abort instead:

```
fixtures-convert season.csv season.ics --strict
```

## CSV format

One row per match, header required:

```csv
date,time,home,away,venue,competition
2026-08-29,15:00,Riverside FC,Oakfield United,Riverside Park,League Division 2
2026-09-05,,Oakfield United,Riverside FC,Oak Lane,League Division 2
```

- `date` — required, `YYYY-MM-DD`
- `time` — optional, 24-hour `HH:MM`; leave blank for an all-day fixture
- `home`, `away` — required team names
- `venue`, `competition` — optional, free text

## iCalendar output

Each fixture becomes one `VEVENT`. Matches with a kickoff time run for a
default two-hour block; matches without one become all-day events. Event
UIDs are derived from the fixture's date and teams, so converting the same
CSV twice produces the same UIDs instead of duplicate calendar entries.

## Known limitations

This is an early version. Notably:

- `--tz` writes a `TZID` parameter on `DTSTART`/`DTEND` but doesn't emit a
  `VTIMEZONE` block, so it relies on the calendar app already knowing the
  IANA zone by name. That's true of every mainstream calendar app (Google,
  Apple, Outlook on the web), but a strict RFC 5545 reader could reject it.
- Reading an `.ics` file ignores any `TZID` on `DTSTART` and keeps the wall-clock
  time as-is — there's nowhere to put the zone on the way back out to CSV.

## License

MIT, see [LICENSE](LICENSE).

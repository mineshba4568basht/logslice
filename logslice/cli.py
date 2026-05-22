"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime
from typing import Optional

from logslice.parser import parse_line
from logslice.filter import apply_filters
from logslice.aggregator import summarize
from logslice.exporter import export_entries


def parse_datetime(value: str) -> datetime:
    """Parse a datetime string in ISO 8601 format."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Invalid datetime format: '{value}'. Expected YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Filter, aggregate, and export structured log files.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input log file path (default: stdin)",
    )
    parser.add_argument(
        "--start", metavar="DATETIME", type=parse_datetime,
        help="Include entries at or after this datetime",
    )
    parser.add_argument(
        "--end", metavar="DATETIME", type=parse_datetime,
        help="Include entries at or before this datetime",
    )
    parser.add_argument(
        "--pattern", metavar="REGEX",
        help="Include only entries matching this regex pattern",
    )
    parser.add_argument(
        "--format", dest="output_format", choices=["jsonl", "csv", "text"],
        default="jsonl", help="Output format (default: jsonl)",
    )
    parser.add_argument(
        "--summarize", action="store_true",
        help="Print a summary instead of filtered entries",
    )
    parser.add_argument(
        "--summarize-field", metavar="FIELD", default="level",
        help="Field to group by when summarizing (default: level)",
    )
    return parser


def run(argv=None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.input == "-":
            lines = sys.stdin
        else:
            lines = open(args.input, "r", encoding="utf-8")

        entries = [e for line in lines if (e := parse_line(line)) is not None]

        if args.input != "-":
            lines.close()
    except OSError as exc:
        print(f"logslice: error opening file: {exc}", file=sys.stderr)
        return 1

    filtered = apply_filters(
        entries,
        start=args.start,
        end=args.end,
        pattern=args.pattern,
    )

    if args.summarize:
        summary = summarize(filtered, field=args.summarize_field)
        for key, count in sorted(summary.items()):
            print(f"{key}: {count}")
    else:
        output = export_entries(filtered, fmt=args.output_format)
        if output:
            print(output)

    return 0


if __name__ == "__main__":
    sys.exit(run())

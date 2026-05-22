"""Export filtered log entries to various output formats."""

import csv
import json
import sys
from typing import IO, Iterable, List, Optional


def export_as_jsonl(entries: List[dict], output: IO = sys.stdout) -> None:
    """Write each log entry as a JSON line (JSONL format)."""
    for entry in entries:
        output.write(json.dumps(entry, default=str) + "\n")


def export_as_csv(
    entries: List[dict],
    fields: Optional[List[str]] = None,
    output: IO = sys.stdout,
) -> None:
    """Write log entries as CSV rows.

    Args:
        entries: List of parsed log entry dicts.
        fields: Column names to include. If None, all keys from the first
                entry are used.
        output: Writable text stream.
    """
    if not entries:
        return

    fieldnames = fields or list(entries[0].keys())
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for entry in entries:
        writer.writerow({k: entry.get(k, "") for k in fieldnames})


def export_as_text(entries: List[dict], output: IO = sys.stdout) -> None:
    """Write log entries as human-readable plain text lines.

    Uses the original 'raw' field when present; otherwise falls back to a
    compact JSON representation.
    """
    for entry in entries:
        line = entry.get("raw") or json.dumps(entry, default=str)
        output.write(line.rstrip("\n") + "\n")


def export_entries(
    entries: List[dict],
    fmt: str = "jsonl",
    fields: Optional[List[str]] = None,
    output: IO = sys.stdout,
) -> None:
    """Dispatch to the appropriate exporter based on *fmt*.

    Args:
        entries: Log entries to export.
        fmt: One of ``'jsonl'``, ``'csv'``, or ``'text'``.
        fields: Optional list of field names (used by CSV exporter).
        output: Writable text stream.

    Raises:
        ValueError: If *fmt* is not a recognised format.
    """
    fmt = fmt.lower()
    if fmt == "jsonl":
        export_as_jsonl(entries, output=output)
    elif fmt == "csv":
        export_as_csv(entries, fields=fields, output=output)
    elif fmt == "text":
        export_as_text(entries, output=output)
    else:
        raise ValueError(f"Unknown export format: {fmt!r}. Choose jsonl, csv, or text.")

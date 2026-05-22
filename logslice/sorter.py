"""Sorting utilities for log entries."""

from typing import Iterable, Iterator, Optional
from datetime import datetime


def sort_by_timestamp(
    entries: Iterable[dict],
    reverse: bool = False,
    missing_last: bool = True,
) -> list[dict]:
    """Sort entries by their 'timestamp' field.

    Args:
        entries: Iterable of parsed log entry dicts.
        reverse: If True, sort descending (newest first).
        missing_last: If True, entries without a timestamp are placed at the
                      end regardless of sort direction.

    Returns:
        A new sorted list of entries.
    """
    def sort_key(entry: dict):
        ts = entry.get("timestamp")
        if ts is None:
            # Push missing timestamps to the end (or beginning if missing_last=False)
            return (1 if missing_last else -1, datetime.min)
        return (0, ts) if not reverse else (0, ts)

    entries_list = list(entries)

    if missing_last:
        with_ts = [e for e in entries_list if e.get("timestamp") is not None]
        without_ts = [e for e in entries_list if e.get("timestamp") is None]
        sorted_with = sorted(with_ts, key=lambda e: e["timestamp"], reverse=reverse)
        return sorted_with + without_ts
    else:
        without_ts = [e for e in entries_list if e.get("timestamp") is None]
        with_ts = [e for e in entries_list if e.get("timestamp") is not None]
        sorted_with = sorted(with_ts, key=lambda e: e["timestamp"], reverse=reverse)
        return without_ts + sorted_with


def sort_by_field(
    entries: Iterable[dict],
    field: str,
    reverse: bool = False,
) -> list[dict]:
    """Sort entries by an arbitrary string field.

    Entries missing the field are placed at the end.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field name to sort by.
        reverse: If True, sort descending.

    Returns:
        A new sorted list of entries.
    """
    entries_list = list(entries)
    with_field = [e for e in entries_list if field in e]
    without_field = [e for e in entries_list if field not in e]
    sorted_with = sorted(with_field, key=lambda e: str(e[field]), reverse=reverse)
    return sorted_with + without_field

"""Filter log entries by time range and/or pattern."""

import re
from datetime import datetime
from typing import Optional, List, Dict, Any


def filter_by_time_range(
    entries: List[Dict[str, Any]],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Return entries whose timestamp falls within [start, end].

    Args:
        entries: List of parsed log entry dicts, each may contain a 'timestamp' key.
        start: Inclusive lower bound. None means no lower bound.
        end: Inclusive upper bound. None means no upper bound.

    Returns:
        Filtered list of entries.
    """
    result = []
    for entry in entries:
        ts = entry.get("timestamp")
        if ts is None:
            continue
        if not isinstance(ts, datetime):
            continue
        if start is not None and ts < start:
            continue
        if end is not None and ts > end:
            continue
        result.append(entry)
    return result


def filter_by_pattern(
    entries: List[Dict[str, Any]],
    pattern: str,
    fields: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> List[Dict[str, Any]]:
    """Return entries where any (or specific) field matches the regex pattern.

    Args:
        entries: List of parsed log entry dicts.
        pattern: Regular expression pattern to search for.
        fields: If provided, only search within these field names.
        case_sensitive: Whether the match should be case-sensitive.

    Returns:
        Filtered list of entries.
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    compiled = re.compile(pattern, flags)

    result = []
    for entry in entries:
        search_values = (
            [str(entry[f]) for f in fields if f in entry]
            if fields
            else [str(v) for v in entry.values()]
        )
        if any(compiled.search(val) for val in search_values):
            result.append(entry)
    return result


def apply_filters(
    entries: List[Dict[str, Any]],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    fields: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> List[Dict[str, Any]]:
    """Convenience wrapper that applies time-range and pattern filters in sequence."""
    if start is not None or end is not None:
        entries = filter_by_time_range(entries, start=start, end=end)
    if pattern:
        entries = filter_by_pattern(
            entries, pattern, fields=fields, case_sensitive=case_sensitive
        )
    return entries

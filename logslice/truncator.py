"""Truncation utilities for log entries and their field values."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

Entry = Dict[str, Any]

ELLIPSIS = "..."


def truncate_string(value: str, max_length: int) -> str:
    """Truncate a string to max_length, appending ellipsis if shortened."""
    if max_length < len(ELLIPSIS):
        raise ValueError(f"max_length must be at least {len(ELLIPSIS)}")
    if len(value) <= max_length:
        return value
    return value[: max_length - len(ELLIPSIS)] + ELLIPSIS


def truncate_field(entry: Entry, field: str, max_length: int) -> Entry:
    """Return a copy of entry with the specified string field truncated."""
    if field not in entry:
        return dict(entry)
    value = entry[field]
    result = dict(entry)
    if isinstance(value, str):
        result[field] = truncate_string(value, max_length)
    return result


def truncate_fields(entry: Entry, field_limits: Dict[str, int]) -> Entry:
    """Return a copy of entry with multiple fields truncated per field_limits."""
    result = dict(entry)
    for field, max_length in field_limits.items():
        if field in result and isinstance(result[field], str):
            result[field] = truncate_string(result[field], max_length)
    return result


def truncate_entries(
    entries: Iterable[Entry],
    field_limits: Dict[str, int],
) -> Iterator[Entry]:
    """Yield entries with string fields truncated according to field_limits."""
    for entry in entries:
        yield truncate_fields(entry, field_limits)

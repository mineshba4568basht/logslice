"""Redactor module: mask or remove sensitive fields from log entries."""

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional

Entry = Dict[str, Any]

DEFAULT_MASK = "***REDACTED***"


def redact_field(entry: Entry, field: str, mask: str = DEFAULT_MASK) -> Entry:
    """Return a copy of entry with the given field replaced by mask.
    If the field is absent, the entry is returned unchanged.
    """
    if field not in entry:
        return entry
    result = dict(entry)
    result[field] = mask
    return result


def redact_fields(entry: Entry, fields: List[str], mask: str = DEFAULT_MASK) -> Entry:
    """Return a copy of entry with all listed fields replaced by mask."""
    result = dict(entry)
    for field in fields:
        if field in result:
            result[field] = mask
    return result


def redact_pattern(
    entry: Entry,
    field: str,
    pattern: str,
    mask: str = DEFAULT_MASK,
    flags: int = 0,
) -> Entry:
    """Return a copy of entry where regex matches inside a string field are masked.
    Non-string field values are left untouched.
    """
    if field not in entry:
        return entry
    value = entry[field]
    if not isinstance(value, str):
        return entry
    result = dict(entry)
    result[field] = re.sub(pattern, mask, value, flags=flags)
    return result


def redact_entries(
    entries: Iterable[Entry],
    fields: Optional[List[str]] = None,
    pattern_field: Optional[str] = None,
    pattern: Optional[str] = None,
    mask: str = DEFAULT_MASK,
) -> Iterator[Entry]:
    """Apply field and/or pattern redaction to an iterable of entries."""
    for entry in entries:
        if fields:
            entry = redact_fields(entry, fields, mask=mask)
        if pattern_field and pattern:
            entry = redact_pattern(entry, pattern_field, pattern, mask=mask)
        yield entry

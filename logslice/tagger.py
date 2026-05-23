"""Tag log entries based on field values or pattern matches."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

Entry = Dict[str, Any]


def tag_by_field(
    entry: Entry,
    field: str,
    value: Any,
    tag: str,
    tag_field: str = "tags",
) -> Entry:
    """Return a copy of *entry* with *tag* added if entry[field] == value."""
    if entry.get(field) != value:
        return entry
    result = dict(entry)
    tags: List[str] = list(result.get(tag_field) or [])
    if tag not in tags:
        tags.append(tag)
    result[tag_field] = tags
    return result


def tag_by_pattern(
    entry: Entry,
    field: str,
    pattern: str,
    tag: str,
    tag_field: str = "tags",
) -> Entry:
    """Return a copy of *entry* with *tag* added if entry[field] matches *pattern*."""
    value = entry.get(field)
    if not isinstance(value, str):
        return entry
    if not re.search(pattern, value):
        return entry
    result = dict(entry)
    tags: List[str] = list(result.get(tag_field) or [])
    if tag not in tags:
        tags.append(tag)
    result[tag_field] = tags
    return result


def tag_entries(
    entries: Iterable[Entry],
    rules: List[Dict[str, Any]],
    tag_field: str = "tags",
) -> Iterable[Entry]:
    """Apply a list of tagging rules to each entry.

    Each rule is a dict with keys:
      - ``type``: ``"field"`` or ``"pattern"``
      - ``field``: the entry field to inspect
      - ``value``: (field rules) the exact value to match
      - ``pattern``: (pattern rules) the regex to match
      - ``tag``: the tag string to add
    """
    for entry in entries:
        for rule in rules:
            kind = rule.get("type", "field")
            if kind == "field":
                entry = tag_by_field(
                    entry,
                    field=rule["field"],
                    value=rule["value"],
                    tag=rule["tag"],
                    tag_field=tag_field,
                )
            elif kind == "pattern":
                entry = tag_by_pattern(
                    entry,
                    field=rule["field"],
                    pattern=rule["pattern"],
                    tag=rule["tag"],
                    tag_field=tag_field,
                )
        yield entry

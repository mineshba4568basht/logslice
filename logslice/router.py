"""Route log entries into named buckets based on field values or patterns."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple

Entry = Dict


def route_by_field(
    entries: Iterable[Entry],
    field: str,
    routes: Dict[str, str],
    default: str = "unmatched",
) -> Dict[str, List[Entry]]:
    """Route entries into buckets based on an exact field value match.

    Args:
        entries: Iterable of log entry dicts.
        field: The field name to inspect.
        routes: Mapping of field value -> bucket name.
        default: Bucket name for entries that don't match any route.

    Returns:
        Dict mapping bucket name to list of entries.
    """
    buckets: Dict[str, List[Entry]] = {}
    for entry in entries:
        value = entry.get(field)
        bucket = routes.get(str(value), default) if value is not None else default
        buckets.setdefault(bucket, []).append(entry)
    return buckets


def route_by_pattern(
    entries: Iterable[Entry],
    field: str,
    patterns: List[Tuple[str, str]],
    default: str = "unmatched",
) -> Dict[str, List[Entry]]:
    """Route entries into buckets by matching a field value against regex patterns.

    Args:
        entries: Iterable of log entry dicts.
        field: The field name whose string value is tested.
        patterns: Ordered list of (regex_pattern, bucket_name) pairs.
                  First match wins.
        default: Bucket name when no pattern matches.

    Returns:
        Dict mapping bucket name to list of entries.
    """
    compiled = [(re.compile(pat), name) for pat, name in patterns]
    buckets: Dict[str, List[Entry]] = {}
    for entry in entries:
        value = str(entry.get(field, ""))
        bucket = default
        for regex, name in compiled:
            if regex.search(value):
                bucket = name
                break
        buckets.setdefault(bucket, []).append(entry)
    return buckets


def route_entries(
    entries: Iterable[Entry],
    field: str,
    routes: Optional[Dict[str, str]] = None,
    patterns: Optional[List[Tuple[str, str]]] = None,
    default: str = "unmatched",
) -> Dict[str, List[Entry]]:
    """Unified routing: prefer pattern routing when patterns are supplied."""
    if patterns:
        return route_by_pattern(entries, field, patterns, default=default)
    if routes:
        return route_by_field(entries, field, routes, default=default)
    return {default: list(entries)}

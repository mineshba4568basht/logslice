"""Field and pattern counting utilities for log entries."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Optional


def count_field_values(
    entries: Iterable[dict],
    field: str,
) -> Counter:
    """Count occurrences of each unique value for a given field."""
    counter: Counter = Counter()
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            counter[str(value)] += 1
    return counter


def count_pattern_matches(
    entries: Iterable[dict],
    pattern: str,
    field: str = "message",
    flags: int = re.IGNORECASE,
) -> int:
    """Count how many entries have a field matching *pattern*."""
    if not pattern:
        return 0
    compiled = re.compile(pattern, flags)
    total = 0
    for entry in entries:
        value = entry.get(field, "")
        if compiled.search(str(value)):
            total += 1
    return total


def count_entries(
    entries: Iterable[dict],
    group_by: Optional[str] = None,
) -> Counter:
    """Count total entries, optionally grouped by a field.

    If *group_by* is None the counter has a single key ``"total"``.
    """
    if group_by is None:
        total = sum(1 for _ in entries)
        return Counter({"total": total})
    return count_field_values(entries, group_by)

"""Deduplication utilities for log entries."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Iterator, List, Optional


def deduplicate_by_field(
    entries: Iterable[dict],
    field: str,
    keep: str = "first",
) -> Iterator[dict]:
    """Yield entries with unique values for *field*.

    Args:
        entries: Iterable of parsed log entry dicts.
        field: The field whose value is used as the dedup key.
        keep: ``'first'`` (default) keeps the first occurrence;
              ``'last'`` keeps the last occurrence.

    Raises:
        ValueError: If *keep* is not ``'first'`` or ``'last'``.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    if keep == "first":
        seen: set = set()
        for entry in entries:
            key = entry.get(field)
            if key is None:
                yield entry
                continue
            if key not in seen:
                seen.add(key)
                yield entry
    else:  # keep == "last"
        last: dict[object, dict] = {}
        order: List[object] = []
        no_field: List[dict] = []
        for entry in entries:
            key = entry.get(field)
            if key is None:
                no_field.append(entry)
                continue
            if key not in last:
                order.append(key)
            last[key] = entry
        for entry in no_field:
            yield entry
        for key in order:
            yield last[key]


def deduplicate_exact(
    entries: Iterable[dict],
    fields: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Yield entries that are unique across all fields (or a subset).

    Args:
        entries: Iterable of parsed log entry dicts.
        fields: If provided, only these fields are compared for equality.
                If ``None``, the entire entry is compared.
    """
    seen: set = set()
    for entry in entries:
        if fields is not None:
            key = tuple((f, entry.get(f)) for f in sorted(fields))
        else:
            key = tuple(sorted(entry.items()))
        if key not in seen:
            seen.add(key)
            yield entry

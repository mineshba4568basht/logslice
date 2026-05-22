"""Field transformation utilities for log entries."""

from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional


Entry = Dict[str, Any]
TransformFn = Callable[[Any], Any]


def transform_field(
    entry: Entry,
    field: str,
    fn: TransformFn,
    *,
    missing_ok: bool = True,
) -> Entry:
    """Return a copy of entry with fn applied to the given field.

    If the field is absent and missing_ok is True the entry is returned
    unchanged.  If missing_ok is False a KeyError is raised.
    """
    if field not in entry:
        if missing_ok:
            return dict(entry)
        raise KeyError(f"Field '{field}' not found in entry")
    result = dict(entry)
    result[field] = fn(entry[field])
    return result


def transform_fields(
    entry: Entry,
    transforms: Dict[str, TransformFn],
    *,
    missing_ok: bool = True,
) -> Entry:
    """Apply multiple field transformations to a single entry."""
    result = dict(entry)
    for field, fn in transforms.items():
        result = transform_field(result, field, fn, missing_ok=missing_ok)
    return result


def rename_field(entry: Entry, old: str, new: str) -> Entry:
    """Return a copy of entry with *old* renamed to *new*.

    If *old* is absent the entry is returned unchanged.
    """
    if old not in entry:
        return dict(entry)
    result = dict(entry)
    result[new] = result.pop(old)
    return result


def drop_fields(entry: Entry, fields: List[str]) -> Entry:
    """Return a copy of entry with the listed fields removed."""
    return {k: v for k, v in entry.items() if k not in fields}


def transform_entries(
    entries: Iterable[Entry],
    transforms: Dict[str, TransformFn],
    *,
    missing_ok: bool = True,
) -> Iterator[Entry]:
    """Lazily apply transform_fields to every entry in *entries*."""
    for entry in entries:
        yield transform_fields(entry, transforms, missing_ok=missing_ok)

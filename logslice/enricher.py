"""Enricher module: attach derived or static fields to log entries."""

from typing import Any, Callable, Dict, Iterable, Iterator, Optional

Entry = Dict[str, Any]


def enrich_with_static(
    entry: Entry, field: str, value: Any, overwrite: bool = False
) -> Entry:
    """Return a copy of entry with a static value set on field.
    If the field already exists and overwrite is False, the entry is unchanged.
    """
    if field in entry and not overwrite:
        return entry
    result = dict(entry)
    result[field] = value
    return result


def enrich_with_derived(
    entry: Entry,
    field: str,
    fn: Callable[[Entry], Any],
    overwrite: bool = False,
) -> Entry:
    """Return a copy of entry with field set to fn(entry).
    If the field already exists and overwrite is False, the entry is unchanged.
    """
    if field in entry and not overwrite:
        return entry
    result = dict(entry)
    result[field] = fn(entry)
    return result


def enrich_entries(
    entries: Iterable[Entry],
    static_fields: Optional[Dict[str, Any]] = None,
    derived_fields: Optional[Dict[str, Callable[[Entry], Any]]] = None,
    overwrite: bool = False,
) -> Iterator[Entry]:
    """Apply static and derived enrichments to every entry in the iterable."""
    for entry in entries:
        if static_fields:
            for field, value in static_fields.items():
                entry = enrich_with_static(entry, field, value, overwrite=overwrite)
        if derived_fields:
            for field, fn in derived_fields.items():
                entry = enrich_with_derived(entry, field, fn, overwrite=overwrite)
        yield entry

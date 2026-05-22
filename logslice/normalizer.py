"""Field normalisation helpers — lowercase keys, cast values, strip whitespace."""

from typing import Any, Dict, Iterable, Iterator, List, Optional


Entry = Dict[str, Any]


def lowercase_keys(entry: Entry) -> Entry:
    """Return a copy of *entry* with all keys lowercased."""
    return {k.lower(): v for k, v in entry.items()}


def strip_string_values(entry: Entry, fields: Optional[List[str]] = None) -> Entry:
    """Strip leading/trailing whitespace from string values.

    If *fields* is given only those fields are processed; otherwise every
    string value in the entry is stripped.
    """
    result = dict(entry)
    targets = fields if fields is not None else list(result.keys())
    for key in targets:
        if key in result and isinstance(result[key], str):
            result[key] = result[key].strip()
    return result


def cast_field(entry: Entry, field: str, type_: type, *, missing_ok: bool = True) -> Entry:
    """Return a copy of *entry* with *field* cast to *type_*.

    Raises ValueError if the cast fails.  If the field is absent and
    *missing_ok* is True the entry is returned unchanged.
    """
    if field not in entry:
        if missing_ok:
            return dict(entry)
        raise KeyError(f"Field '{field}' not found in entry")
    result = dict(entry)
    try:
        result[field] = type_(entry[field])
    except (ValueError, TypeError) as exc:
        raise ValueError(
            f"Cannot cast field '{field}' value {entry[field]!r} to {type_.__name__}"
        ) from exc
    return result


def normalize_entry(
    entry: Entry,
    *,
    lowercase: bool = True,
    strip: bool = True,
    fields_to_strip: Optional[List[str]] = None,
) -> Entry:
    """Apply a standard normalisation pass to *entry*."""
    result = entry
    if lowercase:
        result = lowercase_keys(result)
    if strip:
        result = strip_string_values(result, fields_to_strip)
    return result


def normalize_entries(
    entries: Iterable[Entry],
    *,
    lowercase: bool = True,
    strip: bool = True,
) -> Iterator[Entry]:
    """Lazily normalise every entry in *entries*."""
    for entry in entries:
        yield normalize_entry(entry, lowercase=lowercase, strip=strip)

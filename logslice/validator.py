"""Validator module: check log entries against required fields and value rules."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Entry = Dict[str, Any]
ValidationResult = Tuple[Entry, List[str]]  # (entry, list of error messages)


def validate_required_fields(entry: Entry, required: List[str]) -> List[str]:
    """Return a list of error messages for missing required fields."""
    return [f"missing required field: '{f}'" for f in required if f not in entry]


def validate_field_type(entry: Entry, field: str, expected_type: type) -> List[str]:
    """Return an error if the field exists but is not of the expected type."""
    if field not in entry:
        return []
    if not isinstance(entry[field], expected_type):
        actual = type(entry[field]).__name__
        return [f"field '{field}' expected {expected_type.__name__}, got {actual}"]
    return []


def validate_field_values(
    entry: Entry, field: str, allowed: List[Any]
) -> List[str]:
    """Return an error if the field exists but its value is not in the allowed list."""
    if field not in entry:
        return []
    if entry[field] not in allowed:
        return [f"field '{field}' has disallowed value: {entry[field]!r}"]
    return []


def validate_entry(
    entry: Entry,
    required: Optional[List[str]] = None,
    type_rules: Optional[Dict[str, type]] = None,
    value_rules: Optional[Dict[str, List[Any]]] = None,
) -> ValidationResult:
    """Run all configured validation rules against a single entry.

    Returns (entry, errors) where errors is an empty list on success.
    """
    errors: List[str] = []
    if required:
        errors.extend(validate_required_fields(entry, required))
    if type_rules:
        for field, expected_type in type_rules.items():
            errors.extend(validate_field_type(entry, field, expected_type))
    if value_rules:
        for field, allowed in value_rules.items():
            errors.extend(validate_field_values(entry, field, allowed))
    return entry, errors


def iter_valid(
    entries: Iterable[Entry],
    required: Optional[List[str]] = None,
    type_rules: Optional[Dict[str, type]] = None,
    value_rules: Optional[Dict[str, List[Any]]] = None,
) -> Iterator[Entry]:
    """Yield only entries that pass all validation rules."""
    for entry in entries:
        _, errors = validate_entry(
            entry,
            required=required,
            type_rules=type_rules,
            value_rules=value_rules,
        )
        if not errors:
            yield entry

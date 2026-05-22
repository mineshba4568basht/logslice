"""Tests for logslice.validator."""

import pytest
from logslice.validator import (
    validate_required_fields,
    validate_field_type,
    validate_field_values,
    validate_entry,
    iter_valid,
)


def _e(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# validate_required_fields
# ---------------------------------------------------------------------------

class TestValidateRequiredFields:
    def test_all_present_returns_empty(self):
        assert validate_required_fields(_e(a=1, b=2), ["a", "b"]) == []

    def test_missing_field_returns_error(self):
        errors = validate_required_fields(_e(a=1), ["a", "b"])
        assert len(errors) == 1
        assert "b" in errors[0]

    def test_empty_required_list_always_passes(self):
        assert validate_required_fields(_e(), []) == []

    def test_multiple_missing_fields(self):
        errors = validate_required_fields(_e(), ["x", "y", "z"])
        assert len(errors) == 3


# ---------------------------------------------------------------------------
# validate_field_type
# ---------------------------------------------------------------------------

class TestValidateFieldType:
    def test_correct_type_returns_empty(self):
        assert validate_field_type(_e(level="info"), "level", str) == []

    def test_wrong_type_returns_error(self):
        errors = validate_field_type(_e(level=42), "level", str)
        assert len(errors) == 1
        assert "level" in errors[0]

    def test_absent_field_returns_empty(self):
        assert validate_field_type(_e(), "level", str) == []

    def test_int_field_correct(self):
        assert validate_field_type(_e(code=200), "code", int) == []


# ---------------------------------------------------------------------------
# validate_field_values
# ---------------------------------------------------------------------------

class TestValidateFieldValues:
    def test_allowed_value_returns_empty(self):
        assert validate_field_values(_e(level="info"), "level", ["info", "error"]) == []

    def test_disallowed_value_returns_error(self):
        errors = validate_field_values(_e(level="trace"), "level", ["info", "error"])
        assert len(errors) == 1
        assert "trace" in errors[0]

    def test_absent_field_returns_empty(self):
        assert validate_field_values(_e(), "level", ["info"]) == []


# ---------------------------------------------------------------------------
# validate_entry
# ---------------------------------------------------------------------------

class TestValidateEntry:
    def test_valid_entry_no_errors(self):
        entry = _e(level="info", msg="hello", code=200)
        _, errors = validate_entry(
            entry,
            required=["level", "msg"],
            type_rules={"code": int},
            value_rules={"level": ["info", "error"]},
        )
        assert errors == []

    def test_multiple_violations_collected(self):
        entry = _e(code="oops")
        _, errors = validate_entry(
            entry,
            required=["level"],
            type_rules={"code": int},
        )
        assert len(errors) == 2

    def test_no_rules_always_passes(self):
        _, errors = validate_entry(_e(x=1))
        assert errors == []


# ---------------------------------------------------------------------------
# iter_valid
# ---------------------------------------------------------------------------

class TestIterValid:
    def test_filters_invalid_entries(self):
        entries = [
            _e(level="info", msg="ok"),
            _e(msg="missing level"),
            _e(level="error", msg="also ok"),
        ]
        result = list(iter_valid(entries, required=["level", "msg"]))
        assert len(result) == 2

    def test_all_valid_passes_all(self):
        entries = [_e(level="info"), _e(level="error")]
        result = list(iter_valid(entries, value_rules={"level": ["info", "error"]}))
        assert len(result) == 2

    def test_empty_input_yields_nothing(self):
        assert list(iter_valid([])) == []

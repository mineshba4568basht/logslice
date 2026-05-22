"""Tests for logslice.transformer."""

import pytest

from logslice.transformer import (
    drop_fields,
    rename_field,
    transform_entries,
    transform_field,
    transform_fields,
)


def _e(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# transform_field
# ---------------------------------------------------------------------------

class TestTransformField:
    def test_applies_function_to_field(self):
        entry = _e(level="info")
        result = transform_field(entry, "level", str.upper)
        assert result["level"] == "INFO"

    def test_other_fields_unchanged(self):
        entry = _e(level="info", msg="hello")
        result = transform_field(entry, "level", str.upper)
        assert result["msg"] == "hello"

    def test_original_entry_not_mutated(self):
        entry = _e(level="info")
        transform_field(entry, "level", str.upper)
        assert entry["level"] == "info"

    def test_missing_field_missing_ok_returns_unchanged(self):
        entry = _e(msg="hello")
        result = transform_field(entry, "level", str.upper, missing_ok=True)
        assert result == entry

    def test_missing_field_not_missing_ok_raises(self):
        entry = _e(msg="hello")
        with pytest.raises(KeyError, match="level"):
            transform_field(entry, "level", str.upper, missing_ok=False)


# ---------------------------------------------------------------------------
# transform_fields
# ---------------------------------------------------------------------------

class TestTransformFields:
    def test_multiple_transforms_applied(self):
        entry = _e(level="info", count=3)
        result = transform_fields(
            entry, {"level": str.upper, "count": lambda x: x * 2}
        )
        assert result["level"] == "INFO"
        assert result["count"] == 6

    def test_empty_transforms_returns_copy(self):
        entry = _e(level="info")
        result = transform_fields(entry, {})
        assert result == entry
        assert result is not entry


# ---------------------------------------------------------------------------
# rename_field
# ---------------------------------------------------------------------------

class TestRenameField:
    def test_renames_existing_field(self):
        entry = _e(lvl="warn", msg="oops")
        result = rename_field(entry, "lvl", "level")
        assert "level" in result
        assert "lvl" not in result
        assert result["level"] == "warn"

    def test_absent_field_returns_unchanged(self):
        entry = _e(msg="hi")
        result = rename_field(entry, "missing", "found")
        assert result == entry

    def test_other_fields_preserved(self):
        entry = _e(lvl="error", service="api")
        result = rename_field(entry, "lvl", "level")
        assert result["service"] == "api"


# ---------------------------------------------------------------------------
# drop_fields
# ---------------------------------------------------------------------------

class TestDropFields:
    def test_removes_listed_fields(self):
        entry = _e(level="info", secret="x", msg="hi")
        result = drop_fields(entry, ["secret"])
        assert "secret" not in result
        assert "level" in result

    def test_absent_fields_ignored(self):
        entry = _e(level="info")
        result = drop_fields(entry, ["nope", "also_nope"])
        assert result == entry

    def test_empty_list_returns_copy(self):
        entry = _e(level="info")
        result = drop_fields(entry, [])
        assert result == entry
        assert result is not entry


# ---------------------------------------------------------------------------
# transform_entries
# ---------------------------------------------------------------------------

class TestTransformEntries:
    def test_lazy_iterator(self):
        entries = [_e(level="info"), _e(level="warn")]
        result = transform_entries(entries, {"level": str.upper})
        assert list(result) == [{"level": "INFO"}, {"level": "WARN"}]

    def test_empty_entries_yields_nothing(self):
        result = list(transform_entries([], {"level": str.upper}))
        assert result == []

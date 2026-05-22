"""Tests for logslice.truncator."""

import pytest

from logslice.truncator import (
    truncate_entries,
    truncate_field,
    truncate_fields,
    truncate_string,
)


# ---------------------------------------------------------------------------
# truncate_string
# ---------------------------------------------------------------------------

class TestTruncateString:
    def test_short_string_unchanged(self):
        assert truncate_string("hello", 10) == "hello"

    def test_exact_length_unchanged(self):
        assert truncate_string("hello", 5) == "hello"

    def test_long_string_truncated_with_ellipsis(self):
        result = truncate_string("hello world", 8)
        assert result == "hello..."
        assert len(result) == 8

    def test_minimum_max_length(self):
        result = truncate_string("abcdef", 3)
        assert result == "..."

    def test_max_length_too_small_raises(self):
        with pytest.raises(ValueError):
            truncate_string("hello", 2)

    def test_empty_string_unchanged(self):
        assert truncate_string("", 5) == ""


# ---------------------------------------------------------------------------
# truncate_field
# ---------------------------------------------------------------------------

class TestTruncateField:
    def test_truncates_target_field(self):
        entry = {"message": "a very long message here", "level": "info"}
        result = truncate_field(entry, "message", 10)
        assert result["message"] == "a very ..."
        assert result["level"] == "info"

    def test_missing_field_returns_copy_unchanged(self):
        entry = {"level": "warn"}
        result = truncate_field(entry, "message", 10)
        assert result == {"level": "warn"}

    def test_non_string_field_left_alone(self):
        entry = {"count": 42, "level": "debug"}
        result = truncate_field(entry, "count", 5)
        assert result["count"] == 42

    def test_original_entry_not_mutated(self):
        entry = {"message": "hello world"}
        truncate_field(entry, "message", 5)
        assert entry["message"] == "hello world"


# ---------------------------------------------------------------------------
# truncate_fields
# ---------------------------------------------------------------------------

class TestTruncateFields:
    def test_multiple_fields_truncated(self):
        entry = {"msg": "hello world", "src": "some/long/path/here", "lvl": "info"}
        result = truncate_fields(entry, {"msg": 8, "src": 10})
        assert result["msg"] == "hello..."
        assert result["src"] == "some/l..."
        assert result["lvl"] == "info"

    def test_empty_limits_returns_copy(self):
        entry = {"message": "hello"}
        result = truncate_fields(entry, {})
        assert result == {"message": "hello"}


# ---------------------------------------------------------------------------
# truncate_entries
# ---------------------------------------------------------------------------

class TestTruncateEntries:
    def _entries(self):
        return [
            {"message": "short", "level": "info"},
            {"message": "this is a rather long message", "level": "error"},
            {"level": "debug"},
        ]

    def test_yields_all_entries(self):
        result = list(truncate_entries(self._entries(), {"message": 10}))
        assert len(result) == 3

    def test_long_messages_truncated(self):
        result = list(truncate_entries(self._entries(), {"message": 10}))
        assert result[1]["message"] == "this is..."

    def test_short_messages_unchanged(self):
        result = list(truncate_entries(self._entries(), {"message": 10}))
        assert result[0]["message"] == "short"

    def test_missing_field_entry_passed_through(self):
        result = list(truncate_entries(self._entries(), {"message": 10}))
        assert "message" not in result[2]

    def test_empty_entries_yields_nothing(self):
        result = list(truncate_entries([], {"message": 10}))
        assert result == []

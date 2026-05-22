"""Tests for logslice.formatter."""

from datetime import datetime, timezone

import pytest

from logslice.formatter import (
    colorize,
    format_entries,
    format_entry_text,
    format_timestamp,
)


# ---------------------------------------------------------------------------
# format_timestamp
# ---------------------------------------------------------------------------

class TestFormatTimestamp:
    def test_none_returns_dash(self):
        assert format_timestamp(None) == "-"

    def test_naive_datetime(self):
        dt = datetime(2024, 3, 15, 10, 30, 0)
        assert format_timestamp(dt) == "2024-03-15 10:30:00"

    def test_aware_datetime_converted_to_utc(self):
        from datetime import timedelta
        tz_plus2 = timezone(timedelta(hours=2))
        dt = datetime(2024, 3, 15, 12, 0, 0, tzinfo=tz_plus2)
        result = format_timestamp(dt)
        assert result == "2024-03-15 10:00:00"

    def test_custom_format(self):
        dt = datetime(2024, 1, 2, 3, 4, 5)
        assert format_timestamp(dt, fmt="%d/%m/%Y") == "02/01/2024"


# ---------------------------------------------------------------------------
# format_entry_text
# ---------------------------------------------------------------------------

class TestFormatEntryText:
    def _entry(self, **kwargs):
        return {"_timestamp": datetime(2024, 6, 1, 8, 0, 0), **kwargs}

    def test_includes_level_and_message(self):
        entry = self._entry(level="info", message="hello world")
        line = format_entry_text(entry)
        assert "INFO" in line
        assert "hello world" in line

    def test_includes_service_in_brackets(self):
        entry = self._entry(level="debug", message="ping", service="auth")
        line = format_entry_text(entry)
        assert "[auth]" in line

    def test_missing_level_shows_dash(self):
        entry = self._entry(message="bare")
        line = format_entry_text(entry)
        assert "-" in line

    def test_custom_fields_ordering(self):
        entry = {"a": "1", "b": "2", "c": "3"}
        line = format_entry_text(entry, fields=["c", "a"])
        assert line == "3 | 1"

    def test_missing_custom_field_shows_dash(self):
        entry = {"a": "x"}
        line = format_entry_text(entry, fields=["a", "z"])
        assert line == "x | -"


# ---------------------------------------------------------------------------
# colorize
# ---------------------------------------------------------------------------

class TestColorize:
    def test_color_disabled_returns_original(self):
        assert colorize("hello", "error", enabled=False) == "hello"

    def test_error_wraps_in_red(self):
        result = colorize("oops", "error", enabled=True)
        assert "\033[31m" in result
        assert "\033[0m" in result

    def test_unknown_level_no_color(self):
        result = colorize("msg", "trace", enabled=True)
        assert result == "msg"


# ---------------------------------------------------------------------------
# format_entries
# ---------------------------------------------------------------------------

class TestFormatEntries:
    def test_empty_list_returns_empty(self):
        assert format_entries([]) == []

    def test_returns_one_line_per_entry(self):
        entries = [
            {"level": "info", "message": "a"},
            {"level": "error", "message": "b"},
        ]
        lines = format_entries(entries)
        assert len(lines) == 2

    def test_color_flag_adds_ansi(self):
        entries = [{"level": "error", "message": "boom"}]
        lines = format_entries(entries, color=True)
        assert "\033[" in lines[0]

"""Tests for logslice.highlighter."""

import pytest

from logslice.highlighter import (
    ANSI_RED,
    ANSI_RESET,
    ANSI_YELLOW,
    highlight_entries,
    highlight_entry,
    highlight_pattern,
)


# ---------------------------------------------------------------------------
# highlight_pattern
# ---------------------------------------------------------------------------


class TestHighlightPattern:
    def test_empty_pattern_returns_original(self):
        assert highlight_pattern("hello world", "") == "hello world"

    def test_empty_text_returns_original(self):
        assert highlight_pattern("", "error") == ""

    def test_match_is_wrapped_in_yellow_by_default(self):
        result = highlight_pattern("an error occurred", "error")
        assert f"{ANSI_YELLOW}error{ANSI_RESET}" in result

    def test_match_is_wrapped_in_red_when_specified(self):
        result = highlight_pattern("critical failure", "critical", color="red")
        assert f"{ANSI_RED}critical{ANSI_RESET}" in result

    def test_unknown_color_falls_back_to_yellow(self):
        result = highlight_pattern("warn: low disk", "warn", color="purple")
        assert f"{ANSI_YELLOW}warn{ANSI_RESET}" in result

    def test_multiple_occurrences_all_highlighted(self):
        result = highlight_pattern("err err err", "err")
        assert result.count(f"{ANSI_YELLOW}err{ANSI_RESET}") == 3

    def test_no_match_returns_original(self):
        result = highlight_pattern("all good here", "error")
        assert result == "all good here"

    def test_ignore_case_matches_uppercase(self):
        result = highlight_pattern("ERROR happened", "error", ignore_case=True)
        assert f"{ANSI_YELLOW}ERROR{ANSI_RESET}" in result

    def test_case_sensitive_by_default_no_match(self):
        result = highlight_pattern("ERROR happened", "error")
        assert ANSI_YELLOW not in result

    def test_invalid_regex_returns_original(self):
        result = highlight_pattern("some text", "[invalid")
        assert result == "some text"

    def test_regex_group_is_highlighted(self):
        result = highlight_pattern("status=200 ok", r"\d+")
        assert f"{ANSI_YELLOW}200{ANSI_RESET}" in result


# ---------------------------------------------------------------------------
# highlight_entry
# ---------------------------------------------------------------------------


class TestHighlightEntry:
    def _entry(self):
        return {"level": "error", "message": "disk error detected", "code": 500}

    def test_string_fields_are_highlighted(self):
        result = highlight_entry(self._entry(), "error")
        assert f"{ANSI_YELLOW}error{ANSI_RESET}" in result["level"]
        assert f"{ANSI_YELLOW}error{ANSI_RESET}" in result["message"]

    def test_non_string_fields_are_unchanged(self):
        result = highlight_entry(self._entry(), "error")
        assert result["code"] == 500

    def test_original_entry_not_mutated(self):
        original = self._entry()
        highlight_entry(original, "error")
        assert original["level"] == "error"

    def test_specific_fields_only(self):
        result = highlight_entry(self._entry(), "error", fields=["level"])
        assert ANSI_YELLOW in result["level"]
        assert ANSI_YELLOW not in result["message"]

    def test_missing_field_in_list_is_ignored(self):
        result = highlight_entry(self._entry(), "error", fields=["nonexistent"])
        assert result["level"] == "error"  # unchanged


# ---------------------------------------------------------------------------
# highlight_entries
# ---------------------------------------------------------------------------


class TestHighlightEntries:
    def test_applies_to_all_entries(self):
        entries = [
            {"msg": "error one"},
            {"msg": "error two"},
            {"msg": "all fine"},
        ]
        results = highlight_entries(entries, "error")
        assert ANSI_YELLOW in results[0]["msg"]
        assert ANSI_YELLOW in results[1]["msg"]
        assert ANSI_YELLOW not in results[2]["msg"]

    def test_empty_list_returns_empty(self):
        assert highlight_entries([], "error") == []

"""Tests for logslice.counter."""

from __future__ import annotations

from collections import Counter

import pytest

from logslice.counter import (
    count_entries,
    count_field_values,
    count_pattern_matches,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _e(**kwargs) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# count_field_values
# ---------------------------------------------------------------------------

class TestCountFieldValues:
    def test_counts_distinct_values(self):
        entries = [_e(level="info"), _e(level="error"), _e(level="info")]
        result = count_field_values(entries, "level")
        assert result["info"] == 2
        assert result["error"] == 1

    def test_missing_field_excluded(self):
        entries = [_e(level="info"), _e(msg="hi")]
        result = count_field_values(entries, "level")
        assert result["info"] == 1
        assert len(result) == 1

    def test_empty_entries_returns_empty_counter(self):
        assert count_field_values([], "level") == Counter()

    def test_numeric_values_converted_to_str(self):
        entries = [_e(code=200), _e(code=200), _e(code=404)]
        result = count_field_values(entries, "code")
        assert result["200"] == 2
        assert result["404"] == 1


# ---------------------------------------------------------------------------
# count_pattern_matches
# ---------------------------------------------------------------------------

class TestCountPatternMatches:
    def test_matches_case_insensitive_by_default(self):
        entries = [_e(message="Error occurred"), _e(message="all good"), _e(message="ERROR again")]
        assert count_pattern_matches(entries, "error") == 2

    def test_no_matches_returns_zero(self):
        entries = [_e(message="hello world")]
        assert count_pattern_matches(entries, "error") == 0

    def test_empty_pattern_returns_zero(self):
        entries = [_e(message="anything")]
        assert count_pattern_matches(entries, "") == 0

    def test_custom_field(self):
        entries = [_e(body="critical failure"), _e(body="ok")]
        assert count_pattern_matches(entries, "critical", field="body") == 1

    def test_missing_field_treated_as_empty_string(self):
        entries = [_e(other="error")]
        assert count_pattern_matches(entries, "error", field="message") == 0


# ---------------------------------------------------------------------------
# count_entries
# ---------------------------------------------------------------------------

class TestCountEntries:
    def test_total_with_no_group_by(self):
        entries = [_e(level="info"), _e(level="error"), _e(level="info")]
        result = count_entries(entries)
        assert result["total"] == 3

    def test_empty_entries_total_zero(self):
        assert count_entries([]) == Counter({"total": 0})

    def test_group_by_delegates_to_count_field_values(self):
        entries = [_e(level="info"), _e(level="error"), _e(level="info")]
        result = count_entries(entries, group_by="level")
        assert result["info"] == 2
        assert result["error"] == 1

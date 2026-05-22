"""Tests for logslice.filter module."""

import pytest
from datetime import datetime
from logslice.filter import filter_by_time_range, filter_by_pattern, apply_filters


def _make_entry(ts=None, message="hello world", level="INFO"):
    entry = {"message": message, "level": level}
    if ts is not None:
        entry["timestamp"] = ts
    return entry


DT_EARLY = datetime(2024, 1, 1, 8, 0, 0)
DT_MID = datetime(2024, 1, 1, 12, 0, 0)
DT_LATE = datetime(2024, 1, 1, 18, 0, 0)

SAMPLE_ENTRIES = [
    _make_entry(DT_EARLY, "server started", "INFO"),
    _make_entry(DT_MID, "user login failed", "WARNING"),
    _make_entry(DT_LATE, "disk full error", "ERROR"),
    _make_entry(None, "no timestamp entry", "DEBUG"),
]


class TestFilterByTimeRange:
    def test_no_bounds_excludes_entries_without_timestamp(self):
        result = filter_by_time_range(SAMPLE_ENTRIES)
        assert len(result) == 3

    def test_start_bound_filters_earlier_entries(self):
        result = filter_by_time_range(SAMPLE_ENTRIES, start=DT_MID)
        assert all(e["timestamp"] >= DT_MID for e in result)
        assert len(result) == 2

    def test_end_bound_filters_later_entries(self):
        result = filter_by_time_range(SAMPLE_ENTRIES, end=DT_MID)
        assert all(e["timestamp"] <= DT_MID for e in result)
        assert len(result) == 2

    def test_both_bounds(self):
        result = filter_by_time_range(SAMPLE_ENTRIES, start=DT_MID, end=DT_MID)
        assert len(result) == 1
        assert result[0]["timestamp"] == DT_MID

    def test_empty_input(self):
        assert filter_by_time_range([], start=DT_EARLY) == []

    def test_non_datetime_timestamp_excluded(self):
        entries = [{"timestamp": "not-a-datetime", "message": "bad"}]
        assert filter_by_time_range(entries, start=DT_EARLY) == []


class TestFilterByPattern:
    def test_matches_message_field(self):
        result = filter_by_pattern(SAMPLE_ENTRIES, r"login")
        assert len(result) == 1
        assert result[0]["message"] == "user login failed"

    def test_case_insensitive_by_default(self):
        result = filter_by_pattern(SAMPLE_ENTRIES, r"ERROR")
        assert len(result) == 1

    def test_case_sensitive_flag(self):
        result = filter_by_pattern(SAMPLE_ENTRIES, r"ERROR", case_sensitive=True)
        assert len(result) == 1
        result_no_match = filter_by_pattern(
            SAMPLE_ENTRIES, r"error", case_sensitive=True
        )
        assert len(result_no_match) == 0

    def test_specific_fields_only(self):
        result = filter_by_pattern(SAMPLE_ENTRIES, r"warning", fields=["level"])
        assert len(result) == 1
        assert result[0]["level"] == "WARNING"

    def test_no_match_returns_empty(self):
        result = filter_by_pattern(SAMPLE_ENTRIES, r"xyzzy")
        assert result == []

    def test_empty_entries(self):
        assert filter_by_pattern([], r"anything") == []


class TestApplyFilters:
    def test_combined_time_and_pattern(self):
        result = apply_filters(
            SAMPLE_ENTRIES, start=DT_MID, end=DT_LATE, pattern=r"error"
        )
        assert len(result) == 1
        assert result[0]["level"] == "ERROR"

    def test_no_filters_returns_entries_with_timestamps(self):
        result = apply_filters(SAMPLE_ENTRIES)
        # No time filter: all entries returned; no pattern filter applied
        assert len(result) == len(SAMPLE_ENTRIES)

    def test_only_pattern_filter(self):
        result = apply_filters(SAMPLE_ENTRIES, pattern=r"started")
        assert len(result) == 1

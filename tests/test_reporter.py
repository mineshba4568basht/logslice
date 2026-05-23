"""Tests for logslice.reporter."""

from __future__ import annotations

import pytest

from logslice.reporter import report_field, report_pattern, report_summary


def _e(**kwargs) -> dict:
    return dict(kwargs)


_ENTRIES = [
    _e(level="info", message="started up"),
    _e(level="error", message="connection error occurred"),
    _e(level="info", message="processed request"),
    _e(level="warn", message="slow query"),
    _e(level="error", message="timeout error"),
]


class TestReportField:
    def test_contains_field_name(self):
        output = report_field(_ENTRIES, "level")
        assert "Field: level" in output

    def test_contains_all_values(self):
        output = report_field(_ENTRIES, "level")
        assert "info" in output
        assert "error" in output
        assert "warn" in output

    def test_top_limits_rows(self):
        output = report_field(_ENTRIES, "level", top=2)
        # Only top-2 values; "warn" appears once and should be omitted
        assert "warn" not in output

    def test_no_matching_field_returns_message(self):
        output = report_field(_ENTRIES, "nonexistent")
        assert "No entries" in output

    def test_bar_characters_present(self):
        output = report_field(_ENTRIES, "level")
        assert "#" in output


class TestReportPattern:
    def test_matched_count_in_output(self):
        output = report_pattern(_ENTRIES, "error")
        assert "2/5" in output

    def test_percentage_in_output(self):
        output = report_pattern(_ENTRIES, "error")
        assert "%" in output

    def test_pattern_name_in_output(self):
        output = report_pattern(_ENTRIES, "error")
        assert "error" in output

    def test_zero_matches(self):
        output = report_pattern(_ENTRIES, "zzznomatch")
        assert "0/5" in output
        assert "0.0%" in output

    def test_empty_entries(self):
        output = report_pattern([], "error")
        assert "0/0" in output


class TestReportSummary:
    def test_total_without_group_by(self):
        output = report_summary(_ENTRIES)
        assert "5" in output
        assert "Total" in output

    def test_grouped_output_contains_header(self):
        output = report_summary(_ENTRIES, group_by="level")
        assert "level" in output

    def test_grouped_output_contains_values(self):
        output = report_summary(_ENTRIES, group_by="level")
        assert "info" in output
        assert "error" in output

    def test_empty_entries_total_zero(self):
        output = report_summary([])
        assert "0" in output

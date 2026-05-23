"""Tests for logslice.router."""

import pytest
from logslice.router import route_by_field, route_by_pattern, route_entries


def _e(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# route_by_field
# ---------------------------------------------------------------------------

class TestRouteByField:
    def test_routes_matching_value(self):
        entries = [_e(level="error"), _e(level="info")]
        result = route_by_field(entries, "level", {"error": "errors", "info": "info"})
        assert [e["level"] for e in result["errors"]] == ["error"]
        assert [e["level"] for e in result["info"]] == ["info"]

    def test_unmatched_goes_to_default(self):
        entries = [_e(level="debug")]
        result = route_by_field(entries, "level", {"error": "errors"})
        assert "debug" not in result
        assert result["unmatched"][0]["level"] == "debug"

    def test_custom_default_bucket(self):
        entries = [_e(level="trace")]
        result = route_by_field(entries, "level", {}, default="other")
        assert "other" in result

    def test_missing_field_goes_to_default(self):
        entries = [_e(msg="hello")]
        result = route_by_field(entries, "level", {"error": "errors"})
        assert result["unmatched"][0]["msg"] == "hello"

    def test_multiple_entries_same_bucket(self):
        entries = [_e(level="error"), _e(level="error"), _e(level="info")]
        result = route_by_field(entries, "level", {"error": "errors", "info": "info"})
        assert len(result["errors"]) == 2

    def test_empty_entries_returns_empty(self):
        result = route_by_field([], "level", {"error": "errors"})
        assert result == {}


# ---------------------------------------------------------------------------
# route_by_pattern
# ---------------------------------------------------------------------------

class TestRouteByPattern:
    def test_first_matching_pattern_wins(self):
        entries = [_e(msg="ERROR: disk full")]
        patterns = [(r"ERROR", "errors"), (r"disk", "disk_issues")]
        result = route_by_pattern(entries, "msg", patterns)
        assert "errors" in result
        assert "disk_issues" not in result

    def test_no_match_goes_to_default(self):
        entries = [_e(msg="all good")]
        result = route_by_pattern(entries, "msg", [(r"ERROR", "errors")])
        assert result["unmatched"][0]["msg"] == "all good"

    def test_missing_field_treated_as_empty_string(self):
        entries = [_e(level="info")]
        result = route_by_pattern(entries, "msg", [(r"ERROR", "errors")])
        assert result["unmatched"][0]["level"] == "info"

    def test_case_sensitive_by_default(self):
        entries = [_e(msg="error happened")]
        result = route_by_pattern(entries, "msg", [(r"ERROR", "errors")])
        assert "unmatched" in result

    def test_empty_patterns_all_go_to_default(self):
        entries = [_e(msg="hello"), _e(msg="world")]
        result = route_by_pattern(entries, "msg", [])
        assert len(result["unmatched"]) == 2


# ---------------------------------------------------------------------------
# route_entries (unified)
# ---------------------------------------------------------------------------

class TestRouteEntries:
    def test_prefers_patterns_over_routes(self):
        entries = [_e(level="error")]
        result = route_entries(
            entries,
            "level",
            routes={"error": "exact_errors"},
            patterns=[(r"error", "pattern_errors")],
        )
        assert "pattern_errors" in result
        assert "exact_errors" not in result

    def test_falls_back_to_routes_when_no_patterns(self):
        entries = [_e(level="error")]
        result = route_entries(entries, "level", routes={"error": "errors"})
        assert "errors" in result

    def test_no_config_returns_all_in_default(self):
        entries = [_e(level="info"), _e(level="error")]
        result = route_entries(entries, "level")
        assert len(result["unmatched"]) == 2

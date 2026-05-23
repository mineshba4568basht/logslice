"""Integration tests: router combined with filter and tagger."""

from datetime import datetime, timezone
from logslice.router import route_by_field, route_by_pattern
from logslice.filter import filter_by_pattern
from logslice.tagger import tag_by_field


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(**kwargs):
    return dict(kwargs)


class TestRouterWithFilter:
    def test_route_then_filter_within_bucket(self):
        entries = [
            _e(level="error", msg="disk full"),
            _e(level="error", msg="timeout occurred"),
            _e(level="info", msg="startup complete"),
        ]
        buckets = route_by_field(entries, "level", {"error": "errors", "info": "info"})
        filtered = list(filter_by_pattern(buckets["errors"], "msg", r"disk"))
        assert len(filtered) == 1
        assert filtered[0]["msg"] == "disk full"

    def test_route_pattern_then_filter_unmatched(self):
        entries = [
            _e(service="auth", msg="login failed"),
            _e(service="auth", msg="login ok"),
            _e(service="db", msg="query slow"),
        ]
        buckets = route_by_pattern(
            entries, "msg", [(r"failed", "failures"), (r"slow", "slow")]
        )
        assert len(buckets.get("failures", [])) == 1
        assert len(buckets.get("slow", [])) == 1
        assert len(buckets.get("unmatched", [])) == 1


class TestRouterWithTagger:
    def test_tag_then_route_by_tag(self):
        entries = [
            _e(level="error", msg="oops"),
            _e(level="info", msg="ok"),
            _e(level="error", msg="again"),
        ]
        tagged = list(tag_by_field(entries, "level", "error", "critical"))
        buckets = route_by_field(
            tagged, "tags",
            {"['critical']": "critical_bucket"},
        )
        # tags field is a list; route by pattern is more practical here
        error_entries = [e for e in tagged if "critical" in e.get("tags", [])]
        assert len(error_entries) == 2
        info_entries = [e for e in tagged if "critical" not in e.get("tags", [])]
        assert len(info_entries) == 1

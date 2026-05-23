"""Integration tests: limiter used together with filter and sorter."""

from __future__ import annotations

from datetime import datetime, timezone

from logslice.filter import filter_by_pattern
from logslice.limiter import limit_entries, skip_entries, slice_entries
from logslice.sorter import sort_by_timestamp


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(msg: str, level: str = "INFO", hour: int = 0) -> dict:
    return {"message": msg, "level": level, "timestamp": _ts(hour)}


ENTRIES = [
    _e("alpha error", level="ERROR", hour=3),
    _e("beta info",  level="INFO",  hour=1),
    _e("gamma error", level="ERROR", hour=5),
    _e("delta debug", level="DEBUG", hour=2),
    _e("epsilon error", level="ERROR", hour=4),
]


class TestLimiterWithSorter:
    def test_sort_then_limit_returns_earliest(self):
        sorted_entries = sort_by_timestamp(ENTRIES)
        result = list(limit_entries(sorted_entries, 2))
        assert [e["message"] for e in result] == ["beta info", "delta debug"]

    def test_sort_then_skip_drops_earliest(self):
        sorted_entries = sort_by_timestamp(ENTRIES)
        result = list(skip_entries(sorted_entries, 3))
        assert [e["message"] for e in result] == ["alpha error", "gamma error"]

    def test_sort_then_slice_middle(self):
        sorted_entries = sort_by_timestamp(ENTRIES)
        result = list(slice_entries(sorted_entries, 1, 4))
        assert len(result) == 3
        assert result[0]["message"] == "delta debug"


class TestLimiterWithFilter:
    def test_filter_then_limit(self):
        errors = list(filter_by_pattern(ENTRIES, pattern="error", field="message"))
        result = list(limit_entries(errors, 2))
        assert len(result) == 2
        assert all("error" in e["message"] for e in result)

    def test_filter_then_skip_then_limit(self):
        errors = list(filter_by_pattern(ENTRIES, pattern="error", field="message"))
        # 3 errors total; skip 1, limit 1 → second error
        result = list(limit_entries(skip_entries(errors, 1), 1))
        assert len(result) == 1

    def test_limit_zero_after_filter_yields_nothing(self):
        errors = filter_by_pattern(ENTRIES, pattern="error", field="message")
        assert list(limit_entries(errors, 0)) == []

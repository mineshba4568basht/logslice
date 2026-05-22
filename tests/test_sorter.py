"""Tests for logslice.sorter."""

import pytest
from datetime import datetime, timezone
from logslice.sorter import sort_by_timestamp, sort_by_field


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(hour: int = None, **kwargs) -> dict:
    entry = {**kwargs}
    if hour is not None:
        entry["timestamp"] = _ts(hour)
    return entry


class TestSortByTimestamp:
    def test_ascending_order(self):
        entries = [_e(3), _e(1), _e(2)]
        result = sort_by_timestamp(entries)
        assert [e["timestamp"].hour for e in result] == [1, 2, 3]

    def test_descending_order(self):
        entries = [_e(1), _e(3), _e(2)]
        result = sort_by_timestamp(entries, reverse=True)
        assert [e["timestamp"].hour for e in result] == [3, 2, 1]

    def test_missing_timestamp_placed_last_by_default(self):
        entries = [_e(2), {"msg": "no ts"}, _e(1)]
        result = sort_by_timestamp(entries)
        assert result[-1] == {"msg": "no ts"}

    def test_missing_timestamp_placed_first_when_missing_last_false(self):
        entries = [_e(2), {"msg": "no ts"}, _e(1)]
        result = sort_by_timestamp(entries, missing_last=False)
        assert result[0] == {"msg": "no ts"}

    def test_empty_entries_returns_empty(self):
        assert sort_by_timestamp([]) == []

    def test_all_missing_timestamps(self):
        entries = [{"a": 1}, {"b": 2}]
        result = sort_by_timestamp(entries)
        assert len(result) == 2

    def test_single_entry_returned_unchanged(self):
        entries = [_e(5, msg="only")]
        result = sort_by_timestamp(entries)
        assert result == entries

    def test_returns_new_list_not_in_place(self):
        entries = [_e(2), _e(1)]
        result = sort_by_timestamp(entries)
        assert result is not entries


class TestSortByField:
    def test_sorts_string_field_ascending(self):
        entries = [{"level": "warn"}, {"level": "error"}, {"level": "info"}]
        result = sort_by_field(entries, "level")
        assert [e["level"] for e in result] == ["error", "info", "warn"]

    def test_sorts_string_field_descending(self):
        entries = [{"level": "info"}, {"level": "error"}, {"level": "warn"}]
        result = sort_by_field(entries, "level", reverse=True)
        assert [e["level"] for e in result] == ["warn", "info", "error"]

    def test_missing_field_entries_placed_last(self):
        entries = [{"level": "info"}, {"msg": "no level"}, {"level": "error"}]
        result = sort_by_field(entries, "level")
        assert result[-1] == {"msg": "no level"}

    def test_empty_entries_returns_empty(self):
        assert sort_by_field([], "level") == []

    def test_all_missing_field_returns_all(self):
        entries = [{"a": 1}, {"b": 2}]
        result = sort_by_field(entries, "level")
        assert len(result) == 2

    def test_numeric_values_sorted_as_strings(self):
        entries = [{"code": 20}, {"code": 9}, {"code": 100}]
        result = sort_by_field(entries, "code")
        # String sort: "100" < "20" < "9"
        assert [e["code"] for e in result] == [100, 20, 9]

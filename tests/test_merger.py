"""Tests for logslice.merger."""

from datetime import datetime, timezone
from logslice.merger import merge_sorted, merge_interleave, merge_unique


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(hour: Optional[int] = None, msg: str = "x", **kwargs):
    entry = {"message": msg, **kwargs}
    if hour is not None:
        entry["timestamp"] = _ts(hour)
    return entry


from typing import Optional


class TestMergeSorted:
    def test_merges_two_sorted_streams(self):
        a = [_e(1), _e(3)]
        b = [_e(2), _e(4)]
        result = merge_sorted(a, b)
        hours = [e["timestamp"].hour for e in result]
        assert hours == [1, 2, 3, 4]

    def test_reverse_order(self):
        a = [_e(1), _e(3)]
        b = [_e(2), _e(4)]
        result = merge_sorted(a, b, reverse=True)
        hours = [e["timestamp"].hour for e in result]
        assert hours == [4, 3, 2, 1]

    def test_entries_without_timestamp_go_to_end(self):
        a = [_e(1), {"message": "no-ts"}]
        b = [_e(2)]
        result = merge_sorted(a, b)
        assert result[-1]["message"] == "no-ts"

    def test_empty_streams_return_empty(self):
        assert merge_sorted([], []) == []

    def test_single_stream_returned_sorted(self):
        stream = [_e(3), _e(1), _e(2)]
        result = merge_sorted(stream)
        hours = [e["timestamp"].hour for e in result]
        assert hours == [1, 2, 3]


class TestMergeInterleave:
    def test_round_robin_order(self):
        a = [_e(msg="a1"), _e(msg="a2")]
        b = [_e(msg="b1"), _e(msg="b2")]
        result = list(merge_interleave(a, b))
        msgs = [e["message"] for e in result]
        assert msgs == ["a1", "b1", "a2", "b2"]

    def test_unequal_length_streams(self):
        a = [_e(msg="a1"), _e(msg="a2"), _e(msg="a3")]
        b = [_e(msg="b1")]
        result = list(merge_interleave(a, b))
        assert len(result) == 4

    def test_empty_streams_yield_nothing(self):
        assert list(merge_interleave([], [])) == []

    def test_single_stream_yields_all(self):
        a = [_e(msg="x"), _e(msg="y")]
        result = list(merge_interleave(a))
        assert len(result) == 2


class TestMergeUnique:
    def test_deduplicates_by_key(self):
        a = [_e(msg="first", id="1"), _e(msg="second", id="2")]
        b = [_e(msg="dup", id="1"), _e(msg="third", id="3")]
        result = merge_unique(a, b, key="id")
        ids = [e["id"] for e in result]
        assert ids == ["1", "2", "3"]

    def test_first_occurrence_wins(self):
        a = [_e(msg="original", id="1")]
        b = [_e(msg="overwrite", id="1")]
        result = merge_unique(a, b, key="id")
        assert result[0]["message"] == "original"

    def test_entries_without_key_all_included(self):
        a = [{"message": "no-id"}, {"message": "also-no-id"}]
        result = merge_unique(a, key="id")
        assert len(result) == 1  # None key deduplicates

    def test_empty_streams_return_empty(self):
        assert merge_unique([], [], key="id") == []

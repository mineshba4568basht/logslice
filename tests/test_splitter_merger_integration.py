"""Integration tests: split then merge round-trips."""

from datetime import datetime, timezone
from logslice.splitter import split_by_count, split_by_field
from logslice.merger import merge_sorted, merge_interleave


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(hour: int, level: str = "INFO"):
    return {"timestamp": _ts(hour), "level": level, "message": f"msg-{hour}"}


class TestSplitThenMerge:
    def test_split_by_count_then_merge_sorted_restores_order(self):
        entries = [_e(h) for h in [1, 2, 3, 4, 5, 6]]
        chunks = list(split_by_count(entries, 2))
        assert len(chunks) == 3
        merged = merge_sorted(*chunks)
        hours = [e["timestamp"].hour for e in merged]
        assert hours == [1, 2, 3, 4, 5, 6]

    def test_split_by_field_then_merge_interleave_contains_all(self):
        entries = [
            _e(1, "INFO"),
            _e(2, "ERROR"),
            _e(3, "INFO"),
            _e(4, "WARN"),
        ]
        buckets = [bucket for _, bucket in split_by_field(entries, "level")]
        merged = list(merge_interleave(*buckets))
        assert len(merged) == 4

    def test_split_by_count_chunks_are_independent(self):
        entries = [_e(h) for h in range(10)]
        chunks = list(split_by_count(entries, 3))
        # Mutating one chunk should not affect others
        chunks[0].append(_e(99))
        assert len(chunks[1]) <= 3

    def test_empty_pipeline(self):
        chunks = list(split_by_count([], 5))
        assert chunks == []
        merged = merge_sorted(*chunks)
        assert merged == []

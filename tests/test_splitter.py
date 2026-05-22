"""Tests for logslice.splitter."""

import pytest
from logslice.splitter import split_by_count, split_by_field, split_by_size


def _e(msg: str = "hello", level: str = "INFO", **kwargs):
    return {"message": msg, "level": level, **kwargs}


# ---------------------------------------------------------------------------
# split_by_count
# ---------------------------------------------------------------------------

class TestSplitByCount:
    def test_even_split(self):
        entries = [_e() for _ in range(6)]
        chunks = list(split_by_count(entries, 2))
        assert len(chunks) == 3
        assert all(len(c) == 2 for c in chunks)

    def test_uneven_split_last_chunk_smaller(self):
        entries = [_e() for _ in range(5)]
        chunks = list(split_by_count(entries, 2))
        assert len(chunks) == 3
        assert len(chunks[-1]) == 1

    def test_chunk_size_larger_than_entries(self):
        entries = [_e() for _ in range(3)]
        chunks = list(split_by_count(entries, 10))
        assert len(chunks) == 1
        assert len(chunks[0]) == 3

    def test_empty_entries_yields_nothing(self):
        assert list(split_by_count([], 5)) == []

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError):
            list(split_by_count([_e()], 0))

    def test_chunk_size_one(self):
        entries = [_e() for _ in range(4)]
        chunks = list(split_by_count(entries, 1))
        assert len(chunks) == 4


# ---------------------------------------------------------------------------
# split_by_field
# ---------------------------------------------------------------------------

class TestSplitByField:
    def test_splits_into_correct_groups(self):
        entries = [
            _e(level="INFO"),
            _e(level="ERROR"),
            _e(level="INFO"),
        ]
        result = dict(split_by_field(entries, "level"))
        assert len(result["INFO"]) == 2
        assert len(result["ERROR"]) == 1

    def test_preserves_insertion_order(self):
        entries = [_e(level="B"), _e(level="A"), _e(level="B")]
        keys = [k for k, _ in split_by_field(entries, "level")]
        assert keys == ["B", "A"]

    def test_missing_field_grouped_under_none(self):
        entries = [_e(), {"message": "no level"}]
        result = dict(split_by_field(entries, "level"))
        assert None in result
        assert len(result[None]) == 1

    def test_empty_entries_yields_nothing(self):
        assert list(split_by_field([], "level")) == []


# ---------------------------------------------------------------------------
# split_by_size
# ---------------------------------------------------------------------------

class TestSplitBySize:
    def test_chunks_respect_max_bytes(self):
        entries = [{"message": "x" * 10} for _ in range(5)]
        chunks = list(split_by_size(entries, max_bytes=25, field="message"))
        for chunk in chunks[:-1]:
            total = sum(len(e["message"].encode()) for e in chunk)
            assert total <= 25

    def test_single_entry_larger_than_max_still_yielded(self):
        entries = [{"message": "x" * 100}]
        chunks = list(split_by_size(entries, max_bytes=10, field="message"))
        assert len(chunks) == 1

    def test_empty_entries_yields_nothing(self):
        assert list(split_by_size([], max_bytes=100)) == []

    def test_invalid_max_bytes_raises(self):
        with pytest.raises(ValueError):
            list(split_by_size([_e()], max_bytes=0))

    def test_missing_field_treated_as_empty(self):
        entries = [{"level": "INFO"} for _ in range(10)]
        chunks = list(split_by_size(entries, max_bytes=5, field="message"))
        assert sum(len(c) for c in chunks) == 10

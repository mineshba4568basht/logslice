"""Tests for logslice.limiter."""

from __future__ import annotations

import pytest

from logslice.limiter import limit_entries, skip_entries, slice_entries


def _e(msg: str) -> dict:
    return {"message": msg}


ENTRIES = [_e(f"msg{i}") for i in range(6)]


# ---------------------------------------------------------------------------
# limit_entries
# ---------------------------------------------------------------------------

class TestLimitEntries:
    def test_returns_at_most_n(self):
        result = list(limit_entries(ENTRIES, 3))
        assert result == ENTRIES[:3]

    def test_zero_yields_nothing(self):
        assert list(limit_entries(ENTRIES, 0)) == []

    def test_n_larger_than_source_yields_all(self):
        assert list(limit_entries(ENTRIES, 100)) == ENTRIES

    def test_n_equals_length_yields_all(self):
        assert list(limit_entries(ENTRIES, len(ENTRIES))) == ENTRIES

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            list(limit_entries(ENTRIES, -1))

    def test_empty_source_yields_nothing(self):
        assert list(limit_entries([], 5)) == []

    def test_generator_source_works(self):
        gen = (_e(f"g{i}") for i in range(4))
        result = list(limit_entries(gen, 2))
        assert len(result) == 2


# ---------------------------------------------------------------------------
# skip_entries
# ---------------------------------------------------------------------------

class TestSkipEntries:
    def test_skips_first_n(self):
        result = list(skip_entries(ENTRIES, 2))
        assert result == ENTRIES[2:]

    def test_skip_zero_yields_all(self):
        assert list(skip_entries(ENTRIES, 0)) == ENTRIES

    def test_skip_all_yields_nothing(self):
        assert list(skip_entries(ENTRIES, len(ENTRIES))) == []

    def test_skip_more_than_length_yields_nothing(self):
        assert list(skip_entries(ENTRIES, 100)) == []

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match=">= 0"):
            list(skip_entries(ENTRIES, -3))

    def test_empty_source_yields_nothing(self):
        assert list(skip_entries([], 2)) == []


# ---------------------------------------------------------------------------
# slice_entries
# ---------------------------------------------------------------------------

class TestSliceEntries:
    def test_basic_slice(self):
        result = list(slice_entries(ENTRIES, 1, 4))
        assert result == ENTRIES[1:4]

    def test_start_zero(self):
        result = list(slice_entries(ENTRIES, 0, 3))
        assert result == ENTRIES[:3]

    def test_empty_range_yields_nothing(self):
        assert list(slice_entries(ENTRIES, 2, 2)) == []

    def test_full_range_yields_all(self):
        n = len(ENTRIES)
        assert list(slice_entries(ENTRIES, 0, n)) == ENTRIES

    def test_negative_start_raises(self):
        with pytest.raises(ValueError, match="start"):
            list(slice_entries(ENTRIES, -1, 3))

    def test_negative_stop_raises(self):
        with pytest.raises(ValueError, match="stop"):
            list(slice_entries(ENTRIES, 0, -1))

    def test_stop_less_than_start_raises(self):
        with pytest.raises(ValueError, match="stop.*start"):
            list(slice_entries(ENTRIES, 4, 2))

    def test_stop_beyond_length_yields_tail(self):
        result = list(slice_entries(ENTRIES, 4, 100))
        assert result == ENTRIES[4:]

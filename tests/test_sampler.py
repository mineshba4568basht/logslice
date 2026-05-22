"""Tests for logslice.sampler."""

from __future__ import annotations

import pytest

from logslice.sampler import sample_by_count, sample_by_rate, sample_every_nth


def _entries(n: int = 100) -> list[dict]:
    return [{"index": i, "message": f"log line {i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# sample_by_rate
# ---------------------------------------------------------------------------

class TestSampleByRate:
    def test_rate_zero_yields_nothing(self):
        result = list(sample_by_rate(_entries(50), rate=0.0))
        assert result == []

    def test_rate_one_yields_all(self):
        data = _entries(50)
        result = list(sample_by_rate(data, rate=1.0))
        assert result == data

    def test_invalid_rate_raises(self):
        with pytest.raises(ValueError, match="rate must be between"):
            list(sample_by_rate(_entries(10), rate=1.5))

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError):
            list(sample_by_rate(_entries(10), rate=-0.1))

    def test_partial_rate_reduces_count(self):
        # With rate=0.5 over 10 000 entries we expect roughly half; allow 30 % slack.
        data = _entries(10_000)
        result = list(sample_by_rate(data, rate=0.5))
        assert 3_000 <= len(result) <= 7_000


# ---------------------------------------------------------------------------
# sample_by_count
# ---------------------------------------------------------------------------

class TestSampleByCount:
    def test_returns_at_most_n(self):
        result = sample_by_count(_entries(200), n=10)
        assert len(result) == 10

    def test_returns_all_when_fewer_than_n(self):
        data = _entries(5)
        result = sample_by_count(data, n=20)
        assert len(result) == 5

    def test_n_zero_returns_empty(self):
        result = sample_by_count(_entries(50), n=0)
        assert result == []

    def test_negative_n_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            sample_by_count(_entries(10), n=-1)

    def test_all_results_are_original_entries(self):
        data = _entries(50)
        result = sample_by_count(data, n=20)
        for entry in result:
            assert entry in data


# ---------------------------------------------------------------------------
# sample_every_nth
# ---------------------------------------------------------------------------

class TestSampleEveryNth:
    def test_every_first_yields_all(self):
        data = _entries(10)
        result = list(sample_every_nth(data, n=1))
        assert result == data

    def test_every_second_yields_half(self):
        data = _entries(10)
        result = list(sample_every_nth(data, n=2))
        assert result == [data[i] for i in range(0, 10, 2)]

    def test_n_larger_than_entries_yields_first_only(self):
        data = _entries(5)
        result = list(sample_every_nth(data, n=10))
        assert result == [data[0]]

    def test_zero_n_raises(self):
        with pytest.raises(ValueError, match=">= 1"):
            list(sample_every_nth(_entries(5), n=0))

    def test_empty_input_yields_nothing(self):
        result = list(sample_every_nth([], n=3))
        assert result == []

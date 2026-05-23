"""Tests for logslice.pager."""

import pytest
from logslice.pager import paginate, iter_pages, page_count


def _e(n: int):
    return {"id": n, "msg": f"entry-{n}"}


ENTRIES = [_e(i) for i in range(1, 11)]  # 10 entries


# ---------------------------------------------------------------------------
# paginate
# ---------------------------------------------------------------------------

class TestPaginate:
    def test_first_page_returns_correct_slice(self):
        result = paginate(ENTRIES, page_size=3, page=1)
        assert result == [_e(1), _e(2), _e(3)]

    def test_second_page_returns_correct_slice(self):
        result = paginate(ENTRIES, page_size=3, page=2)
        assert result == [_e(4), _e(5), _e(6)]

    def test_last_partial_page(self):
        result = paginate(ENTRIES, page_size=3, page=4)
        assert result == [_e(10)]

    def test_page_beyond_total_returns_empty(self):
        result = paginate(ENTRIES, page_size=3, page=99)
        assert result == []

    def test_page_size_equals_total(self):
        result = paginate(ENTRIES, page_size=10, page=1)
        assert result == ENTRIES

    def test_page_size_larger_than_total(self):
        result = paginate(ENTRIES, page_size=50, page=1)
        assert result == ENTRIES

    def test_empty_entries_returns_empty(self):
        assert paginate([], page_size=5, page=1) == []

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            paginate(ENTRIES, page_size=0)

    def test_invalid_page_raises(self):
        with pytest.raises(ValueError):
            paginate(ENTRIES, page_size=5, page=0)


# ---------------------------------------------------------------------------
# iter_pages
# ---------------------------------------------------------------------------

class TestIterPages:
    def test_yields_all_pages(self):
        pages = list(iter_pages(ENTRIES, page_size=4))
        assert len(pages) == 3
        assert pages[0] == [_e(1), _e(2), _e(3), _e(4)]
        assert pages[1] == [_e(5), _e(6), _e(7), _e(8)]
        assert pages[2] == [_e(9), _e(10)]

    def test_single_page_when_size_covers_all(self):
        pages = list(iter_pages(ENTRIES, page_size=10))
        assert len(pages) == 1
        assert pages[0] == ENTRIES

    def test_empty_entries_yields_nothing(self):
        pages = list(iter_pages([], page_size=5))
        assert pages == []

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            list(iter_pages(ENTRIES, page_size=0))


# ---------------------------------------------------------------------------
# page_count
# ---------------------------------------------------------------------------

class TestPageCount:
    def test_exact_division(self):
        assert page_count(10, 5) == 2

    def test_partial_last_page(self):
        assert page_count(11, 5) == 3

    def test_single_entry(self):
        assert page_count(1, 5) == 1

    def test_zero_entries_returns_zero(self):
        assert page_count(0, 5) == 0

    def test_invalid_page_size_raises(self):
        with pytest.raises(ValueError):
            page_count(10, 0)

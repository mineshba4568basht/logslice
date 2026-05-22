"""Tests for logslice.deduplicator."""

import pytest

from logslice.deduplicator import deduplicate_by_field, deduplicate_exact


def _e(**kwargs) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# deduplicate_by_field
# ---------------------------------------------------------------------------

class TestDeduplicateByField:
    def test_keep_first_removes_duplicates(self):
        entries = [_e(id=1, msg="a"), _e(id=1, msg="b"), _e(id=2, msg="c")]
        result = list(deduplicate_by_field(entries, "id"))
        assert result == [_e(id=1, msg="a"), _e(id=2, msg="c")]

    def test_keep_last_keeps_final_occurrence(self):
        entries = [_e(id=1, msg="a"), _e(id=1, msg="b"), _e(id=2, msg="c")]
        result = list(deduplicate_by_field(entries, "id", keep="last"))
        assert _e(id=1, msg="b") in result
        assert _e(id=1, msg="a") not in result
        assert _e(id=2, msg="c") in result

    def test_entries_without_field_always_passed_through(self):
        entries = [_e(msg="no-id"), _e(id=1, msg="a"), _e(msg="also-no-id")]
        result = list(deduplicate_by_field(entries, "id"))
        no_id = [e for e in result if "id" not in e]
        assert len(no_id) == 2

    def test_empty_entries_yields_nothing(self):
        assert list(deduplicate_by_field([], "id")) == []

    def test_invalid_keep_raises(self):
        with pytest.raises(ValueError, match="keep must be"):
            list(deduplicate_by_field([_e(id=1)], "id", keep="middle"))

    def test_all_unique_returns_all(self):
        entries = [_e(id=i) for i in range(5)]
        assert list(deduplicate_by_field(entries, "id")) == entries

    def test_keep_last_preserves_insertion_order_of_keys(self):
        entries = [_e(id="x"), _e(id="y"), _e(id="x", extra=1)]
        result = list(deduplicate_by_field(entries, "id", keep="last"))
        ids = [e["id"] for e in result if "id" in e]
        assert ids == ["x", "y"]


# ---------------------------------------------------------------------------
# deduplicate_exact
# ---------------------------------------------------------------------------

class TestDeduplicateExact:
    def test_exact_duplicates_removed(self):
        entries = [_e(a=1, b=2), _e(a=1, b=2), _e(a=3, b=4)]
        result = list(deduplicate_exact(entries))
        assert len(result) == 2

    def test_partial_fields_comparison(self):
        entries = [_e(a=1, b=2), _e(a=1, b=99), _e(a=2, b=2)]
        result = list(deduplicate_exact(entries, fields=["a"]))
        assert len(result) == 2

    def test_empty_entries_yields_nothing(self):
        assert list(deduplicate_exact([])) == []

    def test_no_duplicates_returns_all(self):
        entries = [_e(x=i) for i in range(4)]
        assert list(deduplicate_exact(entries)) == entries

    def test_fields_none_uses_full_entry(self):
        entries = [_e(a=1), _e(a=1), _e(a=2)]
        result = list(deduplicate_exact(entries, fields=None))
        assert len(result) == 2

"""Tests for logslice.tagger."""

from __future__ import annotations

import pytest

from logslice.tagger import tag_by_field, tag_by_pattern, tag_entries


def _e(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# tag_by_field
# ---------------------------------------------------------------------------

class TestTagByField:
    def test_matching_value_adds_tag(self):
        entry = _e(level="error")
        result = tag_by_field(entry, field="level", value="error", tag="err")
        assert result["tags"] == ["err"]

    def test_non_matching_value_leaves_entry_unchanged(self):
        entry = _e(level="info")
        result = tag_by_field(entry, field="level", value="error", tag="err")
        assert "tags" not in result

    def test_missing_field_leaves_entry_unchanged(self):
        entry = _e(msg="hello")
        result = tag_by_field(entry, field="level", value="error", tag="err")
        assert "tags" not in result

    def test_existing_tags_are_preserved(self):
        entry = _e(level="error", tags=["prior"])
        result = tag_by_field(entry, field="level", value="error", tag="err")
        assert "prior" in result["tags"]
        assert "err" in result["tags"]

    def test_duplicate_tag_not_added_twice(self):
        entry = _e(level="error", tags=["err"])
        result = tag_by_field(entry, field="level", value="error", tag="err")
        assert result["tags"].count("err") == 1

    def test_original_entry_not_mutated(self):
        entry = _e(level="error")
        tag_by_field(entry, field="level", value="error", tag="err")
        assert "tags" not in entry

    def test_custom_tag_field(self):
        entry = _e(level="error")
        result = tag_by_field(entry, field="level", value="error", tag="err", tag_field="labels")
        assert result["labels"] == ["err"]


# ---------------------------------------------------------------------------
# tag_by_pattern
# ---------------------------------------------------------------------------

class TestTagByPattern:
    def test_matching_pattern_adds_tag(self):
        entry = _e(msg="connection refused")
        result = tag_by_pattern(entry, field="msg", pattern=r"refused", tag="conn-err")
        assert result["tags"] == ["conn-err"]

    def test_non_matching_pattern_leaves_entry_unchanged(self):
        entry = _e(msg="all good")
        result = tag_by_pattern(entry, field="msg", pattern=r"refused", tag="conn-err")
        assert "tags" not in result

    def test_non_string_field_leaves_entry_unchanged(self):
        entry = _e(code=404)
        result = tag_by_pattern(entry, field="code", pattern=r"4", tag="client-err")
        assert "tags" not in result

    def test_missing_field_leaves_entry_unchanged(self):
        entry = _e(level="info")
        result = tag_by_pattern(entry, field="msg", pattern=r"error", tag="err")
        assert "tags" not in result


# ---------------------------------------------------------------------------
# tag_entries
# ---------------------------------------------------------------------------

class TestTagEntries:
    def test_field_rule_applied(self):
        entries = [_e(level="error"), _e(level="info")]
        rules = [{"type": "field", "field": "level", "value": "error", "tag": "err"}]
        results = list(tag_entries(entries, rules))
        assert results[0]["tags"] == ["err"]
        assert "tags" not in results[1]

    def test_pattern_rule_applied(self):
        entries = [_e(msg="timeout reached"), _e(msg="ok")]
        rules = [{"type": "pattern", "field": "msg", "pattern": r"timeout", "tag": "slow"}]
        results = list(tag_entries(entries, rules))
        assert results[0]["tags"] == ["slow"]
        assert "tags" not in results[1]

    def test_multiple_rules_accumulate_tags(self):
        entries = [_e(level="error", msg="timeout")]
        rules = [
            {"type": "field", "field": "level", "value": "error", "tag": "err"},
            {"type": "pattern", "field": "msg", "pattern": r"timeout", "tag": "slow"},
        ]
        results = list(tag_entries(entries, rules))
        assert set(results[0]["tags"]) == {"err", "slow"}

    def test_empty_rules_leaves_entries_unchanged(self):
        entries = [_e(level="error")]
        results = list(tag_entries(entries, []))
        assert "tags" not in results[0]

    def test_empty_entries_yields_nothing(self):
        results = list(tag_entries([], [{"type": "field", "field": "x", "value": 1, "tag": "t"}]))
        assert results == []

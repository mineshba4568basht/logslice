"""Tests for logslice.redactor."""

import pytest
from logslice.redactor import (
    DEFAULT_MASK,
    redact_field,
    redact_fields,
    redact_pattern,
    redact_entries,
)


def _e(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# redact_field
# ---------------------------------------------------------------------------

class TestRedactField:
    def test_present_field_is_masked(self):
        entry = _e(user="alice", level="info")
        result = redact_field(entry, "user")
        assert result["user"] == DEFAULT_MASK

    def test_other_fields_unchanged(self):
        entry = _e(user="alice", level="info")
        result = redact_field(entry, "user")
        assert result["level"] == "info"

    def test_absent_field_returns_unchanged(self):
        entry = _e(level="info")
        result = redact_field(entry, "password")
        assert result == entry

    def test_original_entry_not_mutated(self):
        entry = _e(token="secret")
        redact_field(entry, "token")
        assert entry["token"] == "secret"

    def test_custom_mask(self):
        entry = _e(token="abc")
        result = redact_field(entry, "token", mask="[hidden]")
        assert result["token"] == "[hidden]"


# ---------------------------------------------------------------------------
# redact_fields
# ---------------------------------------------------------------------------

class TestRedactFields:
    def test_multiple_fields_masked(self):
        entry = _e(user="alice", password="s3cr3t", level="error")
        result = redact_fields(entry, ["user", "password"])
        assert result["user"] == DEFAULT_MASK
        assert result["password"] == DEFAULT_MASK
        assert result["level"] == "error"

    def test_empty_field_list_returns_copy(self):
        entry = _e(user="alice")
        result = redact_fields(entry, [])
        assert result == entry
        assert result is not entry

    def test_absent_fields_ignored(self):
        entry = _e(level="info")
        result = redact_fields(entry, ["user", "token"])
        assert "user" not in result
        assert "token" not in result


# ---------------------------------------------------------------------------
# redact_pattern
# ---------------------------------------------------------------------------

class TestRedactPattern:
    def test_pattern_replaced_in_string_field(self):
        entry = _e(message="token=abc123 received")
        result = redact_pattern(entry, "message", r"token=\w+")
        assert result["message"] == f"{DEFAULT_MASK} received"

    def test_absent_field_unchanged(self):
        entry = _e(level="info")
        result = redact_pattern(entry, "message", r"token=\w+")
        assert result == entry

    def test_non_string_field_unchanged(self):
        entry = _e(code=12345)
        result = redact_pattern(entry, "code", r"\d+")
        assert result["code"] == 12345

    def test_case_insensitive_flag(self):
        import re
        entry = _e(message="Password=Secret")
        result = redact_pattern(entry, "message", r"password=\S+", flags=re.IGNORECASE)
        assert DEFAULT_MASK in result["message"]


# ---------------------------------------------------------------------------
# redact_entries
# ---------------------------------------------------------------------------

class TestRedactEntries:
    def test_fields_redacted_across_all_entries(self):
        entries = [_e(user="alice", msg="a"), _e(user="bob", msg="b")]
        result = list(redact_entries(entries, fields=["user"]))
        assert all(e["user"] == DEFAULT_MASK for e in result)

    def test_pattern_redacted_across_all_entries(self):
        entries = [_e(msg="ip=1.2.3.4"), _e(msg="ip=5.6.7.8")]
        result = list(redact_entries(entries, pattern_field="msg", pattern=r"ip=[\d.]+"))
        assert all(DEFAULT_MASK in e["msg"] for e in result)

    def test_empty_entries_yields_nothing(self):
        result = list(redact_entries([], fields=["user"]))
        assert result == []

    def test_no_options_passes_entries_through(self):
        entries = [_e(user="alice")]
        result = list(redact_entries(entries))
        assert result[0]["user"] == "alice"

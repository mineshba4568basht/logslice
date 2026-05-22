"""Tests for logslice.normalizer."""

import pytest

from logslice.normalizer import (
    cast_field,
    lowercase_keys,
    normalize_entries,
    normalize_entry,
    strip_string_values,
)


# ---------------------------------------------------------------------------
# lowercase_keys
# ---------------------------------------------------------------------------

class TestLowercaseKeys:
    def test_mixed_case_keys_lowercased(self):
        result = lowercase_keys({"Level": "INFO", "MSG": "hi"})
        assert set(result.keys()) == {"level", "msg"}

    def test_values_unchanged(self):
        result = lowercase_keys({"Level": "INFO"})
        assert result["level"] == "INFO"

    def test_already_lowercase_unchanged(self):
        entry = {"level": "info"}
        result = lowercase_keys(entry)
        assert result == entry

    def test_empty_entry(self):
        assert lowercase_keys({}) == {}


# ---------------------------------------------------------------------------
# strip_string_values
# ---------------------------------------------------------------------------

class TestStripStringValues:
    def test_strips_all_string_values(self):
        entry = {"level": "  info  ", "msg": " hello "}
        result = strip_string_values(entry)
        assert result == {"level": "info", "msg": "hello"}

    def test_non_string_values_untouched(self):
        entry = {"count": 42, "msg": " hi "}
        result = strip_string_values(entry)
        assert result["count"] == 42

    def test_specific_fields_only(self):
        entry = {"level": "  info  ", "msg": " hello "}
        result = strip_string_values(entry, fields=["level"])
        assert result["level"] == "info"
        assert result["msg"] == " hello "

    def test_original_not_mutated(self):
        entry = {"msg": " hi "}
        strip_string_values(entry)
        assert entry["msg"] == " hi "


# ---------------------------------------------------------------------------
# cast_field
# ---------------------------------------------------------------------------

class TestCastField:
    def test_cast_string_to_int(self):
        entry = {"count": "42"}
        result = cast_field(entry, "count", int)
        assert result["count"] == 42

    def test_cast_int_to_float(self):
        entry = {"val": 3}
        result = cast_field(entry, "val", float)
        assert result["val"] == 3.0

    def test_invalid_cast_raises_value_error(self):
        entry = {"count": "not_a_number"}
        with pytest.raises(ValueError, match="count"):
            cast_field(entry, "count", int)

    def test_absent_field_missing_ok_returns_unchanged(self):
        entry = {"msg": "hi"}
        result = cast_field(entry, "count", int, missing_ok=True)
        assert result == entry

    def test_absent_field_not_missing_ok_raises(self):
        with pytest.raises(KeyError, match="count"):
            cast_field({"msg": "hi"}, "count", int, missing_ok=False)


# ---------------------------------------------------------------------------
# normalize_entry / normalize_entries
# ---------------------------------------------------------------------------

class TestNormalizeEntry:
    def test_lowercase_and_strip_by_default(self):
        entry = {"Level": "  INFO  ", "Msg": " hello "}
        result = normalize_entry(entry)
        assert result == {"level": "INFO", "msg": "hello"}

    def test_skip_lowercase(self):
        entry = {"Level": "info"}
        result = normalize_entry(entry, lowercase=False)
        assert "Level" in result

    def test_skip_strip(self):
        entry = {"level": "  info  "}
        result = normalize_entry(entry, strip=False)
        assert result["level"] == "  info  "


class TestNormalizeEntries:
    def test_lazy_iterator(self):
        entries = [{"Level": " info "}, {"Level": " warn "}]
        result = list(normalize_entries(entries))
        assert result == [{"level": "info"}, {"level": "warn"}]

    def test_empty_entries(self):
        assert list(normalize_entries([])) == []

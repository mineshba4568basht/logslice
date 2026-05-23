"""Tests for logslice.grouper."""

import pytest
from datetime import datetime, timezone
from logslice.grouper import group_by_field, group_by_time_bucket, group_entries


def _e(field_val=None, ts=None, **kwargs):
    entry = dict(kwargs)
    if field_val is not None:
        entry["level"] = field_val
    if ts is not None:
        entry["timestamp"] = ts
    return entry


def _dt(h, m=0, s=0):
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# group_by_field
# ---------------------------------------------------------------------------

class TestGroupByField:
    def test_groups_by_distinct_values(self):
        entries = [_e("info"), _e("error"), _e("info")]
        result = group_by_field(entries, "level")
        assert len(result["info"]) == 2
        assert len(result["error"]) == 1

    def test_missing_field_goes_to_missing_key(self):
        entries = [{"msg": "no level"}]
        result = group_by_field(entries, "level")
        assert "__missing__" in result
        assert result["__missing__"] == [{"msg": "no level"}]

    def test_custom_missing_key(self):
        entries = [{"msg": "x"}]
        result = group_by_field(entries, "level", missing_key="unknown")
        assert "unknown" in result

    def test_empty_entries_returns_empty_dict(self):
        assert group_by_field([], "level") == {}

    def test_keys_are_strings(self):
        entries = [{"code": 200}, {"code": 404}]
        result = group_by_field(entries, "code")
        assert "200" in result
        assert "404" in result


# ---------------------------------------------------------------------------
# group_by_time_bucket
# ---------------------------------------------------------------------------

class TestGroupByTimeBucket:
    def test_entries_in_same_minute_share_bucket(self):
        entries = [_e(ts=_dt(10, 0, 5)), _e(ts=_dt(10, 0, 45))]
        result = group_by_time_bucket(entries, bucket_seconds=60)
        assert len(result) == 1
        assert list(result.values())[0] == entries

    def test_entries_in_different_minutes_split(self):
        entries = [_e(ts=_dt(10, 0, 0)), _e(ts=_dt(10, 1, 0))]
        result = group_by_time_bucket(entries, bucket_seconds=60)
        assert len(result) == 2

    def test_missing_timestamp_goes_to_missing_key(self):
        entries = [{"msg": "no ts"}]
        result = group_by_time_bucket(entries, bucket_seconds=60)
        assert "__missing__" in result

    def test_invalid_bucket_seconds_raises(self):
        with pytest.raises(ValueError):
            group_by_time_bucket([], bucket_seconds=0)

    def test_naive_datetime_treated_as_utc(self):
        naive = datetime(2024, 1, 1, 10, 0, 0)
        entries = [{"timestamp": naive}]
        result = group_by_time_bucket(entries, bucket_seconds=60)
        assert len(result) == 1
        assert "__missing__" not in result


# ---------------------------------------------------------------------------
# group_entries wrapper
# ---------------------------------------------------------------------------

class TestGroupEntries:
    def test_delegates_to_group_by_field(self):
        entries = [_e("info"), _e("warn")]
        result = group_entries(entries, field="level")
        assert set(result.keys()) == {"info", "warn"}

    def test_delegates_to_group_by_time_bucket(self):
        entries = [_e(ts=_dt(9, 0)), _e(ts=_dt(9, 1))]
        result = group_entries(entries, bucket_seconds=60)
        assert len(result) == 2

    def test_both_args_raises(self):
        with pytest.raises(ValueError):
            group_entries([], field="level", bucket_seconds=60)

    def test_no_args_raises(self):
        with pytest.raises(ValueError):
            group_entries([])

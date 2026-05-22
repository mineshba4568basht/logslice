"""Tests for logslice.aggregator module."""

import pytest
from datetime import datetime
from logslice.aggregator import count_by_field, count_by_time_bucket, summarize


DT_BASE = datetime(2024, 3, 15, 10, 0, 0)

SAMPLE_ENTRIES = [
    {"timestamp": datetime(2024, 3, 15, 10, 5), "level": "INFO", "service": "api"},
    {"timestamp": datetime(2024, 3, 15, 10, 45), "level": "WARNING", "service": "api"},
    {"timestamp": datetime(2024, 3, 15, 11, 10), "level": "ERROR", "service": "db"},
    {"timestamp": datetime(2024, 3, 15, 11, 55), "level": "INFO", "service": "db"},
    {"timestamp": datetime(2024, 3, 15, 12, 30), "level": "INFO", "service": "api"},
]


class TestCountByField:
    def test_count_by_level(self):
        result = count_by_field(SAMPLE_ENTRIES, "level")
        assert result["INFO"] == 3
        assert result["WARNING"] == 1
        assert result["ERROR"] == 1

    def test_count_by_service(self):
        result = count_by_field(SAMPLE_ENTRIES, "service")
        assert result["api"] == 3
        assert result["db"] == 2

    def test_missing_field_excluded(self):
        entries = [{"level": "INFO"}, {"message": "no level"}]
        result = count_by_field(entries, "level")
        assert result == {"INFO": 1}

    def test_empty_entries(self):
        assert count_by_field([], "level") == {}

    def test_results_sorted_by_count_descending(self):
        result = count_by_field(SAMPLE_ENTRIES, "level")
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)


class TestCountByTimeBucket:
    def test_60_minute_buckets(self):
        result = count_by_time_bucket(SAMPLE_ENTRIES, bucket_minutes=60)
        assert result["2024-03-15T10:00:00"] == 2
        assert result["2024-03-15T11:00:00"] == 2
        assert result["2024-03-15T12:00:00"] == 1

    def test_30_minute_buckets(self):
        result = count_by_time_bucket(SAMPLE_ENTRIES, bucket_minutes=30)
        assert result.get("2024-03-15T10:00:00") == 1   # 10:05
        assert result.get("2024-03-15T10:30:00") == 1   # 10:45

    def test_entries_without_timestamp_excluded(self):
        entries = [{"level": "INFO"}, {"timestamp": "not-a-datetime"}]
        result = count_by_time_bucket(entries, bucket_minutes=60)
        assert result == {}

    def test_empty_entries(self):
        assert count_by_time_bucket([], bucket_minutes=60) == {}

    def test_keys_are_sorted(self):
        result = count_by_time_bucket(SAMPLE_ENTRIES, bucket_minutes=60)
        keys = list(result.keys())
        assert keys == sorted(keys)


class TestSummarize:
    def test_total_count(self):
        result = summarize(SAMPLE_ENTRIES)
        assert result["total"] == 5

    def test_group_by_adds_breakdown(self):
        result = summarize(SAMPLE_ENTRIES, group_by="level")
        assert "by_level" in result
        assert result["by_level"]["INFO"] == 3

    def test_bucket_minutes_adds_time_breakdown(self):
        result = summarize(SAMPLE_ENTRIES, bucket_minutes=60)
        assert "by_time_bucket" in result
        assert len(result["by_time_bucket"]) == 3

    def test_combined_group_and_bucket(self):
        result = summarize(SAMPLE_ENTRIES, group_by="service", bucket_minutes=60)
        assert "by_service" in result
        assert "by_time_bucket" in result
        assert result["total"] == 5

    def test_empty_entries(self):
        result = summarize([])
        assert result == {"total": 0}

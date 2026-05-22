"""Tests for logslice.parser module."""

import pytest
from datetime import datetime, timezone
from logslice.parser import (
    parse_json_line,
    parse_common_log_line,
    extract_timestamp,
    parse_line,
)


class TestParseJsonLine:
    def test_valid_json_object(self):
        result = parse_json_line('{"level": "info", "msg": "started"}')
        assert result == {"level": "info", "msg": "started"}

    def test_invalid_json_returns_none(self):
        assert parse_json_line("not json at all") is None

    def test_empty_line_returns_none(self):
        assert parse_json_line("") is None
        assert parse_json_line("   ") is None

    def test_json_with_timestamp_field(self):
        result = parse_json_line('{"timestamp": "2024-01-15T10:30:00Z", "level": "warn"}')
        assert result["level"] == "warn"
        assert result["timestamp"] == "2024-01-15T10:30:00Z"


class TestParseCommonLogLine:
    SAMPLE = '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326'

    def test_valid_common_log(self):
        result = parse_common_log_line(self.SAMPLE)
        assert result is not None
        assert result["host"] == "127.0.0.1"
        assert result["status"] == "200"

    def test_timestamp_parsed(self):
        result = parse_common_log_line(self.SAMPLE)
        assert isinstance(result["timestamp"], datetime)
        assert result["timestamp"].year == 2000

    def test_invalid_line_returns_none(self):
        assert parse_common_log_line("garbage line") is None


class TestExtractTimestamp:
    def test_iso_string_timestamp(self):
        record = {"timestamp": "2024-03-20T08:00:00Z"}
        ts = extract_timestamp(record)
        assert ts is not None
        assert ts.year == 2024
        assert ts.month == 3

    def test_unix_epoch_float(self):
        record = {"ts": 1700000000.0}
        ts = extract_timestamp(record)
        assert ts is not None
        assert ts.year == 2023

    def test_datetime_object_passthrough(self):
        dt = datetime(2024, 6, 1, 12, 0, 0)
        record = {"time": dt}
        assert extract_timestamp(record) == dt

    def test_no_timestamp_field_returns_none(self):
        assert extract_timestamp({"message": "hello"}) is None

    def test_alternative_field_names(self):
        for field in ("time", "ts", "@timestamp", "date"):
            record = {field: "2024-01-01T00:00:00"}
            ts = extract_timestamp(record)
            assert ts is not None, f"Failed for field: {field}"


class TestParseLine:
    def test_json_line_preferred(self):
        result = parse_line('{"level": "debug", "msg": "ok"}')
        assert result == {"level": "debug", "msg": "ok"}

    def test_falls_back_to_common_log(self):
        line = '10.0.0.1 - - [01/Jan/2024:00:00:00 +0000] "POST /api HTTP/1.1" 201 512'
        result = parse_line(line)
        assert result is not None
        assert result["status"] == "201"

    def test_unparseable_line_returns_none(self):
        assert parse_line("this is not a log line") is None

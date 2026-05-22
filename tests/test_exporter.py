"""Tests for logslice.exporter."""

import io
import json
from datetime import datetime, timezone

import pytest

from logslice.exporter import (
    export_as_csv,
    export_as_jsonl,
    export_as_text,
    export_entries,
)


def _entries():
    return [
        {"timestamp": datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc), "level": "INFO", "message": "started", "raw": "2024-01-01T10:00:00Z INFO started"},
        {"timestamp": datetime(2024, 1, 1, 10, 1, 0, tzinfo=timezone.utc), "level": "ERROR", "message": "failed", "raw": "2024-01-01T10:01:00Z ERROR failed"},
    ]


class TestExportAsJsonl:
    def test_produces_one_line_per_entry(self):
        buf = io.StringIO()
        export_as_jsonl(_entries(), output=buf)
        lines = buf.getvalue().strip().splitlines()
        assert len(lines) == 2

    def test_each_line_is_valid_json(self):
        buf = io.StringIO()
        export_as_jsonl(_entries(), output=buf)
        for line in buf.getvalue().strip().splitlines():
            obj = json.loads(line)
            assert "level" in obj

    def test_empty_entries_produces_no_output(self):
        buf = io.StringIO()
        export_as_jsonl([], output=buf)
        assert buf.getvalue() == ""


class TestExportAsCsv:
    def test_header_row_present(self):
        buf = io.StringIO()
        export_as_csv(_entries(), fields=["level", "message"], output=buf)
        lines = buf.getvalue().strip().splitlines()
        assert lines[0] == "level,message"

    def test_correct_number_of_rows(self):
        buf = io.StringIO()
        export_as_csv(_entries(), fields=["level", "message"], output=buf)
        lines = buf.getvalue().strip().splitlines()
        # header + 2 data rows
        assert len(lines) == 3

    def test_missing_field_is_empty_string(self):
        entries = [{"level": "INFO"}]
        buf = io.StringIO()
        export_as_csv(entries, fields=["level", "service"], output=buf)
        lines = buf.getvalue().strip().splitlines()
        assert lines[1] == "INFO,"

    def test_empty_entries_produces_no_output(self):
        buf = io.StringIO()
        export_as_csv([], output=buf)
        assert buf.getvalue() == ""

    def test_auto_fields_from_first_entry(self):
        buf = io.StringIO()
        export_as_csv([{"a": 1, "b": 2}], output=buf)
        header = buf.getvalue().splitlines()[0]
        assert "a" in header and "b" in header


class TestExportAsText:
    def test_uses_raw_field_when_present(self):
        buf = io.StringIO()
        export_as_text(_entries(), output=buf)
        lines = buf.getvalue().strip().splitlines()
        assert lines[0] == "2024-01-01T10:00:00Z INFO started"

    def test_falls_back_to_json_without_raw(self):
        entries = [{"level": "WARN", "message": "low disk"}]
        buf = io.StringIO()
        export_as_text(entries, output=buf)
        obj = json.loads(buf.getvalue().strip())
        assert obj["level"] == "WARN"


class TestExportEntries:
    def test_dispatches_jsonl(self):
        buf = io.StringIO()
        export_entries(_entries(), fmt="jsonl", output=buf)
        assert buf.getvalue().count("\n") == 2

    def test_dispatches_csv(self):
        buf = io.StringIO()
        export_entries(_entries(), fmt="csv", fields=["level"], output=buf)
        assert buf.getvalue().splitlines()[0] == "level"

    def test_dispatches_text(self):
        buf = io.StringIO()
        export_entries(_entries(), fmt="text", output=buf)
        assert "INFO" in buf.getvalue()

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="Unknown export format"):
            export_entries(_entries(), fmt="xml", output=io.StringIO())

"""Tests for logslice.reader."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from unittest.mock import patch
import io

import pytest

from logslice.reader import iter_lines, read_entries, read_entries_from_many


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

JSON_LINE = json.dumps({"level": "INFO", "message": "started", "timestamp": "2024-01-01T00:00:00"})
BAD_LINE = "this is not json or clf\n"


# ---------------------------------------------------------------------------
# iter_lines
# ---------------------------------------------------------------------------

class TestIterLines:
    def test_reads_file(self, tmp_path: Path):
        log = tmp_path / "app.log"
        log.write_text("line1\nline2\n")
        result = list(iter_lines(log))
        assert result == ["line1\n", "line2\n"]

    def test_reads_stdin_when_none(self):
        fake_stdin = io.StringIO("alpha\nbeta\n")
        with patch("logslice.reader.sys.stdin", fake_stdin):
            result = list(iter_lines(None))
        assert result == ["alpha\n", "beta\n"]

    def test_empty_file_yields_nothing(self, tmp_path: Path):
        log = tmp_path / "empty.log"
        log.write_text("")
        assert list(iter_lines(log)) == []


# ---------------------------------------------------------------------------
# read_entries
# ---------------------------------------------------------------------------

class TestReadEntries:
    def test_parses_valid_json_lines(self, tmp_path: Path):
        log = tmp_path / "app.log"
        log.write_text(JSON_LINE + "\n" + JSON_LINE + "\n")
        entries = list(read_entries(log))
        assert len(entries) == 2
        assert entries[0]["level"] == "INFO"

    def test_skips_bad_lines_by_default(self, tmp_path: Path):
        log = tmp_path / "mixed.log"
        log.write_text(BAD_LINE + JSON_LINE + "\n")
        entries = list(read_entries(log))
        assert len(entries) == 1

    def test_raises_on_bad_line_when_strict(self, tmp_path: Path):
        log = tmp_path / "bad.log"
        log.write_text(BAD_LINE)
        with pytest.raises(ValueError, match="Cannot parse log line"):
            list(read_entries(log, skip_unparseable=False))

    def test_reads_from_stdin_when_source_is_none(self):
        fake_stdin = io.StringIO(JSON_LINE + "\n")
        with patch("logslice.reader.sys.stdin", fake_stdin):
            entries = list(read_entries(None))
        assert len(entries) == 1


# ---------------------------------------------------------------------------
# read_entries_from_many
# ---------------------------------------------------------------------------

class TestReadEntriesFromMany:
    def test_combines_multiple_files(self, tmp_path: Path):
        a = tmp_path / "a.log"
        b = tmp_path / "b.log"
        a.write_text(JSON_LINE + "\n")
        b.write_text(JSON_LINE + "\n" + JSON_LINE + "\n")
        entries = list(read_entries_from_many([a, b]))
        assert len(entries) == 3

    def test_empty_list_yields_nothing(self):
        assert list(read_entries_from_many([])) == []

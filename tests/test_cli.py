"""Tests for the logslice CLI module."""

import json
import textwrap
from unittest.mock import patch

import pytest

from logslice.cli import build_parser, run, parse_datetime
from datetime import datetime


SAMPLE_JSONL = textwrap.dedent("""\
    {"timestamp": "2024-01-15T10:00:00", "level": "INFO", "message": "started"}
    {"timestamp": "2024-01-15T11:00:00", "level": "ERROR", "message": "failed"}
    {"timestamp": "2024-01-15T12:00:00", "level": "INFO", "message": "done"}
""").splitlines(keepends=True)


class TestParseDatetime:
    def test_iso_with_time(self):
        result = parse_datetime("2024-01-15T10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_iso_date_only(self):
        result = parse_datetime("2024-01-15")
        assert result == datetime(2024, 1, 15)

    def test_space_separated(self):
        result = parse_datetime("2024-01-15 10:30:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0)

    def test_invalid_format_raises(self):
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            parse_datetime("not-a-date")


class TestBuildParser:
    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args([])
        assert args.input == "-"
        assert args.output_format == "jsonl"
        assert args.start is None
        assert args.end is None
        assert args.pattern is None
        assert args.summarize is False

    def test_format_choices(self):
        parser = build_parser()
        for fmt in ("jsonl", "csv", "text"):
            args = parser.parse_args(["--format", fmt])
            assert args.output_format == fmt

    def test_start_end_parsed(self):
        parser = build_parser()
        args = parser.parse_args(["--start", "2024-01-01", "--end", "2024-12-31"])
        assert args.start == datetime(2024, 1, 1)
        assert args.end == datetime(2024, 12, 31)


class TestRunCLI:
    def _run_with_stdin(self, argv, lines):
        """Helper to run CLI with mocked stdin lines."""
        import io
        mock_stdin = io.StringIO("".join(lines))
        with patch("sys.stdin", mock_stdin):
            return run(argv)

    def test_run_default_jsonl_output(self, capsys):
        code = self._run_with_stdin([], SAMPLE_JSONL)
        assert code == 0
        out = capsys.readouterr().out
        lines = [l for l in out.strip().splitlines() if l]
        assert len(lines) == 3
        assert all(json.loads(l) for l in lines)

    def test_run_with_start_filter(self, capsys):
        code = self._run_with_stdin(["--start", "2024-01-15T11:00:00"], SAMPLE_JSONL)
        assert code == 0
        out = capsys.readouterr().out
        lines = [l for l in out.strip().splitlines() if l]
        assert len(lines) == 2

    def test_run_with_pattern_filter(self, capsys):
        code = self._run_with_stdin(["--pattern", "ERROR"], SAMPLE_JSONL)
        assert code == 0
        out = capsys.readouterr().out
        lines = [l for l in out.strip().splitlines() if l]
        assert len(lines) == 1
        assert "ERROR" in lines[0]

    def test_run_summarize(self, capsys):
        code = self._run_with_stdin(["--summarize", "--summarize-field", "level"], SAMPLE_JSONL)
        assert code == 0
        out = capsys.readouterr().out
        assert "ERROR: 1" in out
        assert "INFO: 2" in out

    def test_run_missing_file_returns_error(self, capsys):
        code = run(["nonexistent_file_xyz.log"])
        assert code == 1
        err = capsys.readouterr().err
        assert "error opening file" in err

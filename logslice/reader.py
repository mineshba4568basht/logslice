"""Reader module for logslice: handles reading log lines from files or stdin."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator, Iterable, Optional

from logslice.parser import parse_line


def iter_lines(source: str | Path | None) -> Generator[str, None, None]:
    """Yield raw lines from a file path or stdin if source is None."""
    if source is None:
        for line in sys.stdin:
            yield line
    else:
        path = Path(source)
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                yield line


def read_entries(
    source: str | Path | None,
    skip_unparseable: bool = True,
) -> Generator[dict, None, None]:
    """Parse log entries from *source*.

    Args:
        source: Path to a log file, or ``None`` to read from stdin.
        skip_unparseable: When *True* (default), lines that cannot be parsed
            are silently dropped.  When *False*, a ``ValueError`` is raised.

    Yields:
        Parsed log entry dicts.
    """
    for raw_line in iter_lines(source):
        entry = parse_line(raw_line)
        if entry is None:
            if not skip_unparseable:
                raise ValueError(f"Cannot parse log line: {raw_line!r}")
            continue
        yield entry


def read_entries_from_many(
    sources: Iterable[str | Path | None],
    skip_unparseable: bool = True,
) -> Generator[dict, None, None]:
    """Yield parsed entries from multiple sources in order."""
    for source in sources:
        yield from read_entries(source, skip_unparseable=skip_unparseable)

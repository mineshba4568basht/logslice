"""limiter.py — Limit the number of entries yielded from a stream."""

from __future__ import annotations

from typing import Iterable, Iterator


def limit_entries(entries: Iterable[dict], n: int) -> Iterator[dict]:
    """Yield at most *n* entries from *entries*.

    Parameters
    ----------
    entries:
        Source iterable of log entry dicts.
    n:
        Maximum number of entries to yield.  Must be >= 0.

    Raises
    ------
    ValueError
        If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n!r}")
    if n == 0:
        return
    count = 0
    for entry in entries:
        yield entry
        count += 1
        if count >= n:
            return


def skip_entries(entries: Iterable[dict], n: int) -> Iterator[dict]:
    """Skip the first *n* entries and yield the rest.

    Parameters
    ----------
    entries:
        Source iterable of log entry dicts.
    n:
        Number of leading entries to discard.  Must be >= 0.

    Raises
    ------
    ValueError
        If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n!r}")
    skipped = 0
    for entry in entries:
        if skipped < n:
            skipped += 1
            continue
        yield entry


def slice_entries(entries: Iterable[dict], start: int, stop: int) -> Iterator[dict]:
    """Yield entries at positions [start, stop) (zero-based).

    Equivalent to ``skip_entries`` followed by ``limit_entries``.

    Raises
    ------
    ValueError
        If *start* or *stop* is negative, or *stop* < *start*.
    """
    if start < 0:
        raise ValueError(f"start must be >= 0, got {start!r}")
    if stop < 0:
        raise ValueError(f"stop must be >= 0, got {stop!r}")
    if stop < start:
        raise ValueError(f"stop ({stop}) must be >= start ({start})")
    count = stop - start
    yield from limit_entries(skip_entries(entries, start), count)

"""Sampling utilities for logslice — reduce large log streams by rate or count."""

from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_by_rate(entries: Iterable[dict], rate: float) -> Iterator[dict]:
    """Yield each entry with probability *rate* (0.0 – 1.0).

    Args:
        entries: Iterable of parsed log entry dicts.
        rate: Fraction of entries to keep, e.g. 0.1 keeps ~10 %.

    Raises:
        ValueError: If *rate* is not in the range [0.0, 1.0].
    """
    if not 0.0 <= rate <= 1.0:
        raise ValueError(f"rate must be between 0.0 and 1.0, got {rate!r}")
    for entry in entries:
        if random.random() < rate:
            yield entry


def sample_by_count(entries: Iterable[dict], n: int) -> list[dict]:
    """Return a random sample of at most *n* entries using reservoir sampling.

    Args:
        entries: Iterable of parsed log entry dicts.
        n: Maximum number of entries to return.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n!r}")
    reservoir: list[dict] = []
    for i, entry in enumerate(entries):
        if i < n:
            reservoir.append(entry)
        else:
            j = random.randint(0, i)
            if j < n:
                reservoir[j] = entry
    return reservoir


def sample_every_nth(entries: Iterable[dict], n: int) -> Iterator[dict]:
    """Yield every *n*-th entry (deterministic, zero-indexed).

    Args:
        entries: Iterable of parsed log entry dicts.
        n: Step size; must be >= 1.

    Raises:
        ValueError: If *n* is less than 1.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n!r}")
    for i, entry in enumerate(entries):
        if i % n == 0:
            yield entry

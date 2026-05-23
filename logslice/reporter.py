"""High-level reporting helpers that combine counting with formatting."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Optional

from logslice.counter import count_entries, count_field_values, count_pattern_matches


def _bar(value: int, max_value: int, width: int = 20) -> str:
    """Return a simple ASCII bar proportional to *value* / *max_value*."""
    if max_value == 0:
        return ""
    filled = round(value / max_value * width)
    return "#" * filled + "-" * (width - filled)


def report_field(
    entries: Iterable[dict],
    field: str,
    top: Optional[int] = None,
    bar_width: int = 20,
) -> str:
    """Return a formatted frequency table for *field* values."""
    counts: Counter = count_field_values(list(entries), field)
    if not counts:
        return f"No entries with field '{field}'."

    ordered = counts.most_common(top)
    max_val = ordered[0][1]
    lines = [f"Field: {field}"]
    for key, val in ordered:
        bar = _bar(val, max_val, bar_width)
        lines.append(f"  {key:<20} {val:>6}  [{bar}]")
    return "\n".join(lines)


def report_pattern(
    entries: Iterable[dict],
    pattern: str,
    field: str = "message",
) -> str:
    """Return a one-line summary of how many entries match *pattern*."""
    entry_list = list(entries)
    matched = count_pattern_matches(entry_list, pattern, field=field)
    total = len(entry_list)
    pct = (matched / total * 100) if total else 0.0
    return f"Pattern '{pattern}' matched {matched}/{total} entries ({pct:.1f}%)."


def report_summary(
    entries: Iterable[dict],
    group_by: Optional[str] = None,
) -> str:
    """Return a brief summary count, optionally grouped."""
    counts = count_entries(list(entries), group_by=group_by)
    if group_by is None:
        return f"Total entries: {counts['total']}"
    lines = [f"Grouped by '{group_by}':"]
    for key, val in counts.most_common():
        lines.append(f"  {key}: {val}")
    return "\n".join(lines)

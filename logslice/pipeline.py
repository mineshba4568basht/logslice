"""End-to-end pipeline that wires reader → filter → sampler → aggregator → exporter."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from logslice.reader import read_entries_from_many
from logslice.filter import apply_filters
from logslice.sampler import sample_by_rate, sample_by_count, sample_every_nth
from logslice.aggregator import summarize
from logslice.exporter import export_entries


def run_pipeline(
    paths: list[str],
    *,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    field: Optional[str] = None,
    # sampling options — at most one should be set
    sample_rate: Optional[float] = None,
    sample_n: Optional[int] = None,
    sample_nth: Optional[int] = None,
    # output options
    output_format: str = "jsonl",
    aggregate: bool = False,
    time_bucket: Optional[str] = None,
) -> str:
    """Run the full logslice pipeline and return the output as a string.

    Args:
        paths: List of file paths to read; an empty list reads from stdin.
        start: Optional lower bound for timestamp filtering.
        end: Optional upper bound for timestamp filtering.
        pattern: Optional regex pattern to match against raw log lines.
        field: Field name used for aggregation counts.
        sample_rate: Keep each entry with this probability (0–1).
        sample_n: Keep a random reservoir of at most *n* entries.
        sample_nth: Keep every *n*-th entry deterministically.
        output_format: One of ``jsonl``, ``csv``, ``text``.
        aggregate: When *True*, run summarize() instead of exporting raw entries.
        time_bucket: Bucket size for time-based aggregation (e.g. ``hour``).

    Returns:
        Rendered output as a single string.
    """
    entries = list(read_entries_from_many(paths))
    entries = list(apply_filters(entries, start=start, end=end, pattern=pattern))

    # Apply at most one sampling strategy.
    if sample_rate is not None:
        entries = list(sample_by_rate(entries, rate=sample_rate))
    elif sample_n is not None:
        entries = sample_by_count(entries, n=sample_n)
    elif sample_nth is not None:
        entries = list(sample_every_nth(entries, n=sample_nth))

    if aggregate:
        summary = summarize(entries, field=field, time_bucket=time_bucket)
        lines = []
        if field and "by_field" in summary:
            for key, count in summary["by_field"].items():
                lines.append(f"{key}: {count}")
        if time_bucket and "by_time" in summary:
            for bucket, count in summary["by_time"].items():
                lines.append(f"{bucket}: {count}")
        lines.append(f"total: {summary.get('total', len(entries))}")
        return "\n".join(lines)

    return export_entries(entries, fmt=output_format)

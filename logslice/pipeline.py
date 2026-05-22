"""High-level pipeline that wires together reader, filter, sort, and export."""

from typing import Optional
from datetime import datetime

from logslice.reader import read_entries_from_many
from logslice.filter import apply_filters
from logslice.sorter import sort_by_timestamp
from logslice.exporter import export_entries
from logslice.aggregator import summarize
from logslice.sampler import sample_by_rate, sample_by_count
from logslice.deduplicator import deduplicate_exact


def run_pipeline(
    paths: list[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    pattern_field: str = "message",
    output_format: str = "jsonl",
    output_path: Optional[str] = None,
    sort: bool = True,
    sort_reverse: bool = False,
    deduplicate: bool = False,
    sample_rate: Optional[float] = None,
    sample_count: Optional[int] = None,
    aggregate_field: Optional[str] = None,
) -> Optional[dict]:
    """Execute the full logslice pipeline.

    Reads entries from *paths* (or stdin if empty), applies time and pattern
    filters, optionally deduplicates and samples, sorts by timestamp, then
    either exports or returns an aggregation summary.

    Returns:
        A summary dict when *aggregate_field* is set, otherwise None.
    """
    entries = list(read_entries_from_many(paths or []))

    entries = apply_filters(
        entries,
        start=start,
        end=end,
        pattern=pattern,
        pattern_field=pattern_field,
    )

    if deduplicate:
        entries = deduplicate_exact(entries)

    if sample_rate is not None:
        entries = list(sample_by_rate(entries, rate=sample_rate))
    elif sample_count is not None:
        entries = list(sample_by_count(entries, count=sample_count))

    if sort:
        entries = sort_by_timestamp(entries, reverse=sort_reverse)

    if aggregate_field:
        return summarize(entries, group_by=aggregate_field)

    export_entries(entries, fmt=output_format, path=output_path)
    return None

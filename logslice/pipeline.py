"""High-level pipeline that wires reader → filter → aggregator → exporter."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from logslice.reader import read_entries_from_many
from logslice.filter import apply_filters
from logslice.aggregator import summarize
from logslice.exporter import export_entries


def run_pipeline(
    sources: Iterable[str | Path | None],
    *,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    pattern: Optional[str] = None,
    pattern_field: str = "message",
    aggregate_by: Optional[str] = None,
    time_bucket: Optional[str] = None,
    output_format: str = "jsonl",
    output_path: Optional[str | Path] = None,
    skip_unparseable: bool = True,
) -> dict | None:
    """Execute the full logslice pipeline.

    Returns a summary dict when *aggregate_by* or *time_bucket* is set,
    otherwise returns ``None`` (output written via exporter).
    """
    entries = list(
        read_entries_from_many(sources, skip_unparseable=skip_unparseable)
    )

    filtered = list(
        apply_filters(
            entries,
            start=start,
            end=end,
            pattern=pattern,
            field=pattern_field,
        )
    )

    if aggregate_by or time_bucket:
        return summarize(
            filtered,
            group_by=aggregate_by,
            time_bucket=time_bucket,
        )

    export_entries(
        filtered,
        fmt=output_format,
        destination=str(output_path) if output_path else None,
    )
    return None

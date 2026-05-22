"""High-level pipeline that wires reader → filter → aggregate → format/export."""

from typing import Any, Dict, List, Optional

from logslice.reader import read_entries_from_many
from logslice.filter import apply_filters
from logslice.aggregator import summarize
from logslice.exporter import export_entries
from logslice.formatter import format_entries


def run_pipeline(
    paths: List[Optional[str]],
    *,
    start=None,
    end=None,
    pattern: Optional[str] = None,
    pattern_field: Optional[str] = None,
    aggregate: bool = False,
    aggregate_field: Optional[str] = None,
    bucket: Optional[str] = None,
    output_format: str = "text",
    output_fields: Optional[List[str]] = None,
    color: bool = False,
) -> str:
    """Execute the full logslice pipeline and return the result as a string.

    Parameters
    ----------
    paths:
        List of file paths to read; ``None`` entries trigger stdin reads.
    start / end:
        Optional :class:`datetime` bounds for time filtering.
    pattern:
        Optional regex pattern for message filtering.
    pattern_field:
        Field to match *pattern* against (defaults to ``message``).
    aggregate:
        When *True* run aggregation instead of raw output.
    aggregate_field:
        Field to group by when aggregating.
    bucket:
        Time-bucket granularity (``minute``, ``hour``, ``day``).
    output_format:
        One of ``"text"``, ``"jsonl"``, ``"csv"``.
    output_fields:
        Ordered list of fields to include in text / csv output.
    color:
        Emit ANSI colour codes in text output.
    """
    entries: List[Dict[str, Any]] = read_entries_from_many(paths)

    entries = apply_filters(
        entries,
        start=start,
        end=end,
        pattern=pattern,
        field=pattern_field,
    )

    if aggregate:
        summary = summarize(
            entries,
            field=aggregate_field,
            bucket=bucket,
        )
        lines = [f"{key}\t{count}" for key, count in sorted(summary.items())]
        return "\n".join(lines)

    if output_format == "text":
        lines = format_entries(entries, fields=output_fields, color=color)
        return "\n".join(lines)

    return export_entries(entries, fmt=output_format, fields=output_fields)

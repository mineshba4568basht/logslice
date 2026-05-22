"""Aggregate filtered log entries into summary statistics."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


def count_by_field(
    entries: List[Dict[str, Any]], field: str
) -> Dict[str, int]:
    """Count occurrences of each unique value for a given field.

    Args:
        entries: List of log entry dicts.
        field: The field name to group by.

    Returns:
        Dict mapping field value -> count, sorted by count descending.
    """
    counter: Counter = Counter()
    for entry in entries:
        value = entry.get(field)
        if value is not None:
            counter[str(value)] += 1
    return dict(counter.most_common())


def count_by_time_bucket(
    entries: List[Dict[str, Any]],
    bucket_minutes: int = 60,
) -> Dict[str, int]:
    """Bucket entries into fixed-width time windows and count per bucket.

    Args:
        entries: List of log entry dicts, each with a 'timestamp' datetime.
        bucket_minutes: Width of each time bucket in minutes.

    Returns:
        Dict mapping ISO-formatted bucket start time -> count.
    """
    buckets: Dict[datetime, int] = defaultdict(int)
    delta = timedelta(minutes=bucket_minutes)

    for entry in entries:
        ts = entry.get("timestamp")
        if not isinstance(ts, datetime):
            continue
        # Floor to nearest bucket
        bucket_start = ts - timedelta(
            minutes=ts.minute % bucket_minutes,
            seconds=ts.second,
            microseconds=ts.microsecond,
        )
        buckets[bucket_start] += 1

    return {
        bucket.isoformat(): count
        for bucket, count in sorted(buckets.items())
    }


def summarize(
    entries: List[Dict[str, Any]],
    group_by: Optional[str] = None,
    bucket_minutes: Optional[int] = None,
) -> Dict[str, Any]:
    """Produce a summary dict for a list of log entries.

    Args:
        entries: List of log entry dicts.
        group_by: Optional field name to count by value.
        bucket_minutes: If set, also include time-bucket counts.

    Returns:
        Summary dict with total count and optional breakdowns.
    """
    summary: Dict[str, Any] = {"total": len(entries)}

    if group_by:
        summary["by_" + group_by] = count_by_field(entries, group_by)

    if bucket_minutes is not None:
        summary["by_time_bucket"] = count_by_time_bucket(
            entries, bucket_minutes=bucket_minutes
        )

    return summary

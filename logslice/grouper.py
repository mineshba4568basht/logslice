"""Group log entries by a field value or time bucket."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


def group_by_field(
    entries: Iterable[dict],
    field: str,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Group entries into lists keyed by the value of *field*.

    Entries that lack *field* are placed under *missing_key*.
    """
    groups: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        key = str(entry[field]) if field in entry else missing_key
        groups[key].append(entry)
    return dict(groups)


def group_by_time_bucket(
    entries: Iterable[dict],
    bucket_seconds: int = 60,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Group entries into time buckets of *bucket_seconds* width.

    Each bucket key is an ISO-formatted UTC datetime string truncated to
    the start of the bucket.  Entries without a ``timestamp`` value are
    placed under *missing_key*.
    """
    if bucket_seconds <= 0:
        raise ValueError("bucket_seconds must be a positive integer")

    groups: Dict[str, List[dict]] = defaultdict(list)
    for entry in entries:
        ts: Optional[datetime] = entry.get("timestamp")
        if ts is None:
            groups[missing_key].append(entry)
            continue
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        epoch = int(ts.timestamp())
        bucket_start = epoch - (epoch % bucket_seconds)
        bucket_dt = datetime.fromtimestamp(bucket_start, tz=timezone.utc)
        key = bucket_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        groups[key].append(entry)
    return dict(groups)


def group_entries(
    entries: Iterable[dict],
    field: Optional[str] = None,
    bucket_seconds: Optional[int] = None,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Convenience wrapper: group by *field* or by time bucket.

    Exactly one of *field* or *bucket_seconds* must be provided.
    """
    if field is not None and bucket_seconds is not None:
        raise ValueError("Provide either 'field' or 'bucket_seconds', not both")
    if field is not None:
        return group_by_field(entries, field, missing_key=missing_key)
    if bucket_seconds is not None:
        return group_by_time_bucket(entries, bucket_seconds, missing_key=missing_key)
    raise ValueError("Provide at least one of 'field' or 'bucket_seconds'")

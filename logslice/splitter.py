"""Split log entries into chunks by count, size, or field value."""

from typing import Iterator, List, Dict, Any, Optional


def split_by_count(entries: List[Dict[str, Any]], chunk_size: int) -> Iterator[List[Dict[str, Any]]]:
    """Yield successive chunks of at most chunk_size entries."""
    if chunk_size < 1:
        raise ValueError(f"chunk_size must be >= 1, got {chunk_size}")
    for i in range(0, len(entries), chunk_size):
        yield entries[i : i + chunk_size]


def split_by_field(
    entries: List[Dict[str, Any]], field: str
) -> Iterator[tuple]:
    """Yield (field_value, entries_with_that_value) pairs, preserving insertion order."""
    buckets: Dict[Any, List[Dict[str, Any]]] = {}
    for entry in entries:
        key = entry.get(field)
        buckets.setdefault(key, []).append(entry)
    for key, bucket in buckets.items():
        yield key, bucket


def split_by_size(
    entries: List[Dict[str, Any]], max_bytes: int, field: str = "message"
) -> Iterator[List[Dict[str, Any]]]:
    """Yield chunks where the total byte length of *field* stays under max_bytes."""
    if max_bytes < 1:
        raise ValueError(f"max_bytes must be >= 1, got {max_bytes}")
    current: List[Dict[str, Any]] = []
    current_size = 0
    for entry in entries:
        value = entry.get(field, "")
        entry_size = len(str(value).encode("utf-8"))
        if current and current_size + entry_size > max_bytes:
            yield current
            current = []
            current_size = 0
        current.append(entry)
        current_size += entry_size
    if current:
        yield current

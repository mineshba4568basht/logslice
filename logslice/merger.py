"""Merge multiple sorted or unsorted log entry streams into one."""

import heapq
from datetime import datetime
from typing import Iterable, List, Dict, Any, Optional


def merge_sorted(
    *streams: List[Dict[str, Any]],
    key: str = "timestamp",
    reverse: bool = False,
) -> List[Dict[str, Any]]:
    """Merge pre-sorted entry lists into a single sorted list.

    Entries without *key* are appended at the end (or beginning if reverse).
    """
    def sort_key(entry: Dict[str, Any]):
        ts = entry.get(key)
        if isinstance(ts, datetime):
            return (0, ts)
        return (1, datetime.min)

    combined = [entry for stream in streams for entry in stream]
    combined.sort(key=sort_key, reverse=reverse)
    return combined


def merge_interleave(
    *streams: Iterable[Dict[str, Any]],
) -> Iterable[Dict[str, Any]]:
    """Yield entries from multiple iterables in round-robin order."""
    iterators = [iter(s) for s in streams]
    while iterators:
        exhausted = []
        for it in iterators:
            try:
                yield next(it)
            except StopIteration:
                exhausted.append(it)
        for it in exhausted:
            iterators.remove(it)


def merge_unique(
    *streams: List[Dict[str, Any]],
    key: str,
) -> List[Dict[str, Any]]:
    """Merge streams, keeping only the first occurrence of each *key* value."""
    seen = set()
    result = []
    for stream in streams:
        for entry in stream:
            val = entry.get(key)
            if val not in seen:
                seen.add(val)
                result.append(entry)
    return result

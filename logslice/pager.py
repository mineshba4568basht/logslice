"""Pager: split a stream of entries into pages for paginated output."""

from typing import Iterator, List, Dict, Any


def paginate(
    entries: List[Dict[str, Any]],
    page_size: int,
    page: int = 1,
) -> List[Dict[str, Any]]:
    """Return a single page of entries.

    Args:
        entries:   Full list of log entries.
        page_size: Number of entries per page.  Must be >= 1.
        page:      1-based page number to return.  Must be >= 1.

    Returns:
        Slice of entries for the requested page.  Returns an empty list when
        the page number exceeds the total number of pages.

    Raises:
        ValueError: If *page_size* or *page* is less than 1.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if page < 1:
        raise ValueError(f"page must be >= 1, got {page}")

    start = (page - 1) * page_size
    end = start + page_size
    return entries[start:end]


def iter_pages(
    entries: List[Dict[str, Any]],
    page_size: int,
) -> Iterator[List[Dict[str, Any]]]:
    """Yield successive pages of *page_size* entries each.

    Args:
        entries:   Full list of log entries.
        page_size: Number of entries per page.  Must be >= 1.

    Yields:
        Non-empty lists of entries, one per page.

    Raises:
        ValueError: If *page_size* is less than 1.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")

    for start in range(0, max(len(entries), 1), page_size):
        chunk = entries[start : start + page_size]
        if chunk:
            yield chunk


def page_count(total: int, page_size: int) -> int:
    """Return the total number of pages needed to display *total* entries.

    Args:
        total:     Total number of entries.
        page_size: Entries per page.  Must be >= 1.

    Returns:
        Number of pages (0 when *total* is 0).

    Raises:
        ValueError: If *page_size* is less than 1.
    """
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    if total <= 0:
        return 0
    return (total + page_size - 1) // page_size

"""Highlight matching patterns within log entry fields for display."""

import re
from typing import Any, Dict, List, Optional

ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_RESET = "\033[0m"

_COLOR_MAP = {
    "yellow": ANSI_YELLOW,
    "red": ANSI_RED,
}


def highlight_pattern(
    text: str,
    pattern: str,
    color: str = "yellow",
    ignore_case: bool = False,
) -> str:
    """Return *text* with every occurrence of *pattern* wrapped in ANSI color codes.

    Args:
        text: The source string to search.
        pattern: A regular-expression pattern to locate.
        color: One of ``'yellow'`` or ``'red'`` (default ``'yellow'``).
        ignore_case: When ``True`` the match is case-insensitive.

    Returns:
        The original string with matches colorized, or the original string
        unchanged when no matches are found or *pattern* is empty.
    """
    if not pattern or not text:
        return text

    ansi = _COLOR_MAP.get(color, ANSI_YELLOW)
    flags = re.IGNORECASE if ignore_case else 0

    try:
        compiled = re.compile(pattern, flags)
    except re.error:
        return text

    def _replace(m: re.Match) -> str:  # type: ignore[type-arg]
        return f"{ansi}{m.group(0)}{ANSI_RESET}"

    return compiled.sub(_replace, text)


def highlight_entry(
    entry: Dict[str, Any],
    pattern: str,
    fields: Optional[List[str]] = None,
    color: str = "yellow",
    ignore_case: bool = False,
) -> Dict[str, Any]:
    """Return a shallow copy of *entry* with string field values highlighted.

    Args:
        entry: A parsed log entry (dict).
        pattern: Regular-expression pattern to highlight.
        fields: Explicit list of field names to search.  When ``None`` every
                string-valued field is processed.
        color: ANSI color name passed to :func:`highlight_pattern`.
        ignore_case: Passed to :func:`highlight_pattern`.

    Returns:
        A new dict with matching text colorized in the selected fields.
    """
    result = dict(entry)
    target_fields = fields if fields is not None else list(result.keys())

    for key in target_fields:
        value = result.get(key)
        if isinstance(value, str):
            result[key] = highlight_pattern(value, pattern, color=color, ignore_case=ignore_case)

    return result


def highlight_entries(
    entries: List[Dict[str, Any]],
    pattern: str,
    fields: Optional[List[str]] = None,
    color: str = "yellow",
    ignore_case: bool = False,
) -> List[Dict[str, Any]]:
    """Apply :func:`highlight_entry` to every entry in *entries*."""
    return [
        highlight_entry(e, pattern, fields=fields, color=color, ignore_case=ignore_case)
        for e in entries
    ]

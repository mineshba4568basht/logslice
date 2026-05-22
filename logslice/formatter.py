"""Formatting utilities for log entries before display or export."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


ENTRY_COLORS = {
    "error": "\033[31m",
    "warn": "\033[33m",
    "warning": "\033[33m",
    "info": "\033[32m",
    "debug": "\033[36m",
}
RESET = "\033[0m"


def format_timestamp(ts: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object as a string, or return '-' if None."""
    if ts is None:
        return "-"
    if ts.tzinfo is not None:
        ts = ts.astimezone(timezone.utc).replace(tzinfo=None)
    return ts.strftime(fmt)


def format_entry_text(entry: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """Render a single log entry as a human-readable line.

    If *fields* is provided only those keys are included (in order).
    Falls back to a sensible default ordering when fields is None.
    """
    if fields:
        parts = [str(entry.get(f, "-")) for f in fields]
        return " | ".join(parts)

    ts = format_timestamp(entry.get("_timestamp"))
    level = str(entry.get("level", entry.get("severity", "-"))).upper()
    message = str(entry.get("message", entry.get("msg", "")))
    service = entry.get("service", entry.get("logger", ""))

    base = f"{ts}  {level:<8}  {message}"
    if service:
        base = f"{base}  [{service}]"
    return base


def colorize(line: str, level: str, enabled: bool = True) -> str:
    """Wrap *line* in ANSI colour codes based on log level."""
    if not enabled:
        return line
    color = ENTRY_COLORS.get(level.lower(), "")
    if not color:
        return line
    return f"{color}{line}{RESET}"


def format_entries(
    entries: List[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    color: bool = False,
) -> List[str]:
    """Format a list of entries into display lines."""
    lines = []
    for entry in entries:
        line = format_entry_text(entry, fields=fields)
        if color:
            level = str(entry.get("level", entry.get("severity", "")))
            line = colorize(line, level, enabled=True)
        lines.append(line)
    return lines

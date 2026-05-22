"""Log line parser for structured log files (JSON and common log formats)."""

import json
import re
from datetime import datetime
from typing import Optional

# Common log format: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /index.html HTTP/1.0" 200 2326
COMMON_LOG_PATTERN = re.compile(
    r'(?P<host>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d{3}) (?P<size>\S+)'
)
COMMON_LOG_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

# ISO 8601 timestamp pattern used in many structured logs
ISO_TIMESTAMP_PATTERN = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'
)


def parse_json_line(line: str) -> Optional[dict]:
    """Attempt to parse a line as JSON. Returns dict or None."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def parse_common_log_line(line: str) -> Optional[dict]:
    """Attempt to parse a line as Common Log Format. Returns dict or None."""
    match = COMMON_LOG_PATTERN.match(line.strip())
    if not match:
        return None
    data = match.groupdict()
    try:
        data["timestamp"] = datetime.strptime(data["time"], COMMON_LOG_TIME_FORMAT)
    except ValueError:
        data["timestamp"] = None
    return data


def extract_timestamp(record: dict) -> Optional[datetime]:
    """Extract a datetime from common timestamp field names in a parsed record."""
    for field in ("timestamp", "time", "ts", "@timestamp", "date"):
        value = record.get(field)
        if value is None:
            continue
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.utcfromtimestamp(value)
            except (OSError, OverflowError, ValueError):
                continue
        if isinstance(value, str):
            match = ISO_TIMESTAMP_PATTERN.search(value)
            if match:
                raw = match.group("timestamp").replace(" ", "T")
                for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                            "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
                    try:
                        return datetime.strptime(raw, fmt)
                    except ValueError:
                        continue
    return None


def parse_line(line: str) -> Optional[dict]:
    """Parse a single log line, trying JSON then Common Log Format."""
    record = parse_json_line(line)
    if record is not None:
        return record
    record = parse_common_log_line(line)
    if record is not None:
        return record
    return None

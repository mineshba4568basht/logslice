# logslice

A command-line utility to filter, aggregate, and export structured log files by time range or pattern.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Filter logs by time range
logslice --input app.log --start "2024-01-15 08:00:00" --end "2024-01-15 12:00:00"

# Filter by pattern and export to a file
logslice --input app.log --pattern "ERROR" --output errors.log

# Aggregate log levels and print a summary
logslice --input app.log --aggregate --format json

# Combine time range and pattern filters
logslice --input app.log --start "2024-01-15 08:00:00" --pattern "WARN" --output warnings.log
```

### Options

| Flag | Description |
|------|-------------|
| `--input` | Path to the input log file |
| `--output` | Path to the output file (default: stdout) |
| `--start` | Start of the time range (ISO format) |
| `--end` | End of the time range (ISO format) |
| `--pattern` | Regex or keyword pattern to match log lines |
| `--aggregate` | Print a summary of log levels |
| `--format` | Output format: `text`, `json`, or `csv` (default: `text`) |

---

## Requirements

- Python 3.8+
- No external dependencies required

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).
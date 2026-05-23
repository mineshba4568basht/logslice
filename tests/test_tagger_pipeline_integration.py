"""Integration tests: tagger working alongside filter and enricher."""

from __future__ import annotations

from datetime import datetime, timezone

from logslice.tagger import tag_entries
from logslice.filter import filter_by_pattern, apply_filters
from logslice.enricher import enrich_with_static, enrich_with_derived


def _ts(hour: int) -> datetime:
    return datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)


def _e(**kwargs):
    return dict(kwargs)


class TestTaggerWithFilter:
    """Tag entries then filter by the resulting tag field."""

    def test_tag_then_filter_by_tag_value(self):
        entries = [
            _e(level="error", msg="boom"),
            _e(level="info", msg="ok"),
            _e(level="error", msg="crash"),
        ]
        rules = [{"type": "field", "field": "level", "value": "error", "tag": "err"}]
        tagged = list(tag_entries(entries, rules))
        # filter_by_pattern on the tags list converted to string
        filtered = [
            e for e in tagged
            if "err" in (e.get("tags") or [])
        ]
        assert len(filtered) == 2
        assert all(e["level"] == "error" for e in filtered)

    def test_pattern_tag_then_apply_filters(self):
        entries = [
            _e(msg="NullPointerException in handler"),
            _e(msg="everything is fine"),
        ]
        rules = [{"type": "pattern", "field": "msg", "pattern": r"Exception", "tag": "exception"}]
        tagged = list(tag_entries(entries, rules))
        # Use filter_by_pattern to keep only entries whose msg contains 'Exception'
        filtered = list(filter_by_pattern(tagged, field="msg", pattern=r"Exception"))
        assert len(filtered) == 1
        assert filtered[0]["tags"] == ["exception"]


class TestTaggerWithEnricher:
    """Enrich entries first, then apply tagging rules on enriched fields."""

    def test_enrich_then_tag_on_derived_field(self):
        entries = [_e(status=500), _e(status=200)]
        enriched = list(enrich_with_derived(
            entries,
            derivations={"is_error": lambda e: e.get("status", 0) >= 500},
        ))
        rules = [{"type": "field", "field": "is_error", "value": True, "tag": "server-error"}]
        tagged = list(tag_entries(enriched, rules))
        assert tagged[0]["tags"] == ["server-error"]
        assert "tags" not in tagged[1]

    def test_static_enrich_then_tag(self):
        entries = [_e(level="warn"), _e(level="debug")]
        enriched = list(enrich_with_static(entries, fields={"env": "production"}))
        rules = [{"type": "field", "field": "env", "value": "production", "tag": "prod"}]
        tagged = list(tag_entries(enriched, rules))
        assert all(e["tags"] == ["prod"] for e in tagged)

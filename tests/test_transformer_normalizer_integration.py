"""Integration tests combining transformer and normalizer."""

from logslice.normalizer import normalize_entries
from logslice.transformer import drop_fields, rename_field, transform_entries


def _e(**kwargs):
    return dict(kwargs)


class TestTransformerNormalizerIntegration:
    def test_normalize_then_transform(self):
        """Normalise keys to lowercase, then uppercase the level value."""
        raw = [{"Level": "  warn  ", "Msg": " disk full "}]
        normalised = list(normalize_entries(raw))
        transformed = list(
            transform_entries(normalised, {"level": str.upper})
        )
        assert transformed[0]["level"] == "WARN"
        assert transformed[0]["msg"] == "disk full"

    def test_rename_then_normalize(self):
        """Rename a field and then normalise the resulting entries."""
        entries = [_e(lvl="  ERROR  ", service="api")]
        renamed = [rename_field(e, "lvl", "level") for e in entries]
        normalised = list(normalize_entries(renamed))
        assert normalised[0]["level"] == "ERROR"
        assert normalised[0]["service"] == "api"

    def test_drop_fields_after_normalize(self):
        """Sensitive fields are dropped after normalisation."""
        raw = [{"Level": "info", "Password": "s3cr3t", "User": "alice"}]
        normalised = list(normalize_entries(raw))
        cleaned = [drop_fields(e, ["password"]) for e in normalised]
        assert "password" not in cleaned[0]
        assert cleaned[0]["user"] == "alice"

    def test_pipeline_preserves_entry_count(self):
        raw = [
            {"Level": "info", "Msg": " a "},
            {"Level": "warn", "Msg": " b "},
            {"Level": "error", "Msg": " c "},
        ]
        normalised = list(normalize_entries(raw))
        transformed = list(
            transform_entries(normalised, {"level": str.upper})
        )
        assert len(transformed) == 3

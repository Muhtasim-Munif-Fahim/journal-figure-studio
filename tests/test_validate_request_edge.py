from __future__ import annotations

from pathlib import Path

import yaml

from scripts.validate_request import (
    VALID_FIGURE_TYPES,
    _is_named_profile,
    validate_request,
)


class TestValidateRequestEdge:
    def test_missing_both_figure_and_figures(self, tmp_path: Path):
        req = {"profile": "universal", "layout": "single", "output_dir": "/tmp"}
        p = tmp_path / "req.yaml"
        p.write_text(yaml.safe_dump(req))
        errors = validate_request(p)
        assert any("figure" in e for e in errors)

    def test_supported_types_listed(self):
        assert "bar" in VALID_FIGURE_TYPES
        assert "line" in VALID_FIGURE_TYPES
        assert "calibration" in VALID_FIGURE_TYPES

    def test_named_profile_check(self):
        assert _is_named_profile({"source_url": "https://example.com"}) is True
        assert _is_named_profile({}) is False
        assert _is_named_profile({"source_url": ""}) is False

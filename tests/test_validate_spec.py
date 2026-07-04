from __future__ import annotations

from pathlib import Path

from scripts.validate_request import _validate_figure_spec


class TestValidateSpec:
    def test_missing_source(self, tmp_path: Path):
        errors: list[str] = []
        spec = {"type": "bar", "x": "a", "y": "b", "xlabel": "A", "ylabel": "B"}
        _validate_figure_spec(errors, spec, 0, tmp_path)
        assert errors

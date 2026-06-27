from __future__ import annotations

from pathlib import Path

from scripts.validate_request import _validate_figure_spec


class TestValidateSpecEdge:
    def test_empty_source_string(self, tmp_path: Path):
        errors: list[str] = []
        spec = {"type": "bar", "source": "", "x": "a", "y": "b", "xlabel": "X", "ylabel": "Y"}
        _validate_figure_spec(errors, spec, 0, tmp_path)
        assert errors

    def test_none_type(self, tmp_path: Path):
        errors: list[str] = []
        spec = {"type": None, "source": str(tmp_path / "data.csv"), "x": "a", "y": "b", "xlabel": "X", "ylabel": "Y"}
        _validate_figure_spec(errors, spec, 0, tmp_path)
        assert errors

from __future__ import annotations

from pathlib import Path

from scripts.validate_request import validate_request


class TestValidateLength:
    def test_long_caption_takeaway(self, tmp_path: Path):
        import yaml
        req = {
            "figure_id": "x", "research_field": "cs", "profile": "universal",
            "layout": "single", "data_paths": [],
            "analysis_script": str(tmp_path / "dummy.py"),
            "claim": "Test.", "caption_takeaway": "x" * 201,
            "figure": {"type": "bar", "source": str(tmp_path / "d.csv"), "x": "a", "y": "b", "xlabel": "X", "ylabel": "Y"},
            "output_dir": str(tmp_path / "out"),
        }
        (tmp_path / "dummy.py").write_text("#")
        (tmp_path / "d.csv").write_text("a,b\n1,2\n")
        p = tmp_path / "req.yaml"
        p.write_text(yaml.safe_dump(req))
        errors = validate_request(p)
        assert any("caption_takeaway" in e for e in errors)

    def test_long_claim(self, tmp_path: Path):
        import yaml
        req = {
            "figure_id": "x", "research_field": "cs", "profile": "universal",
            "layout": "single", "data_paths": [],
            "analysis_script": str(tmp_path / "dummy.py"),
            "claim": "x" * 1001, "caption_takeaway": "Short.",
            "figure": {"type": "bar", "source": str(tmp_path / "d.csv"), "x": "a", "y": "b", "xlabel": "X", "ylabel": "Y"},
            "output_dir": str(tmp_path / "out"),
        }
        (tmp_path / "dummy.py").write_text("#")
        (tmp_path / "d.csv").write_text("a,b\n1,2\n")
        p = tmp_path / "req.yaml"
        p.write_text(yaml.safe_dump(req))
        errors = validate_request(p)
        assert any("claim" in e for e in errors)

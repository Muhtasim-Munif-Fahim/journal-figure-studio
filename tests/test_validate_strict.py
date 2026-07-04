from __future__ import annotations

from pathlib import Path

from scripts.validate_request import validate_request


class TestValidateStrictMode:
    def test_strict_flags_warnings(self, tmp_path: Path):
        import yaml

        req = {
            "figure_id": "x",
            "research_field": "cs",
            "profile": "universal",
            "layout": "single",
            "data_paths": [],
            "analysis_script": str(tmp_path / "dummy.py"),
            "claim": "Test.",
            "caption_takeaway": "x" * 201,
            "figure": {
                "type": "bar",
                "source": str(tmp_path / "d.csv"),
                "x": "a",
                "y": "b",
                "xlabel": "X",
                "ylabel": "Y",
            },
            "output_dir": str(tmp_path / "out"),
        }
        (tmp_path / "dummy.py").write_text("#")
        (tmp_path / "d.csv").write_text("a,b\n1,2\n")
        p = tmp_path / "req.yaml"
        p.write_text(yaml.safe_dump(req))
        errors_non_strict = validate_request(p, strict=False)
        errors_strict = validate_request(p, strict=True)
        assert any("[warn]" in e for e in errors_non_strict)
        assert any("exceeds" in e for e in errors_strict)

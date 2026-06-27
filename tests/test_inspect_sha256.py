from __future__ import annotations

from pathlib import Path

from scripts.inspect_results import inspect


class TestInspectSha256Consistency:
    def test_same_file_same_sha(self, tmp_path: Path):
        p = tmp_path / "d.csv"
        p.write_text("x\n1\n2\n3\n")
        r1 = inspect(p)
        r2 = inspect(p)
        assert r1["sha256"] == r2["sha256"]

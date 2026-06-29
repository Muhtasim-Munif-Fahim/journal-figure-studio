from __future__ import annotations

from pathlib import Path

from scripts.common import write_json


class TestWriteJsonPathEdge:
    def test_relative_path(self, tmp_path: Path):
        import os
        cwd = Path.cwd()
        os.chdir(str(tmp_path))
        try:
            write_json({"a": 1}, "output.json")
            assert (tmp_path / "output.json").exists()
        finally:
            os.chdir(str(cwd))

    def test_path_with_parent_dirs(self, tmp_path: Path):
        p = tmp_path / "a" / "b" / "c" / "out.json"
        write_json({"x": 1}, p)
        assert p.exists()

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.common import SKILL_ROOT, read_table


def _profile() -> dict:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())


class TestEdgeCases:
    def test_empty_csv(self, tmp_path: Path):
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("a,b\n")
        df = read_table(csv_path)
        assert len(df) == 0

    def test_single_column_csv(self, tmp_path: Path):
        csv_path = tmp_path / "single.csv"
        csv_path.write_text("val\n1\n2\n3\n")
        df = read_table(csv_path)
        assert list(df.columns) == ["val"]

    def test_csv_with_nan_values(self, tmp_path: Path):
        csv_path = tmp_path / "nan.csv"
        csv_path.write_text("a,b\n1,2\n,4\n3,\n")
        df = read_table(csv_path)
        assert df["a"].isna().sum() == 1
        assert df["b"].isna().sum() == 1

    def test_csv_with_special_chars_in_headers(self, tmp_path: Path):
        csv_path = tmp_path / "special.csv"
        csv_path.write_text("col 1,col-2,col.3\n1,2,3\n")
        df = read_table(csv_path)
        assert list(df.columns) == ["col 1", "col-2", "col.3"]

    def test_tab_separated_csv(self, tmp_path: Path):
        csv_path = tmp_path / "tsv.csv"
        csv_path.write_text("a\tb\n1\t2\n3\t4\n")
        df = read_table(csv_path)
        assert len(df) == 2

    def test_duplicate_column_names(self, tmp_path: Path):
        csv_path = tmp_path / "dup.csv"
        csv_path.write_text("a,a\n1,2\n3,4\n")
        df = read_table(csv_path)
        assert len(df.columns) == 2

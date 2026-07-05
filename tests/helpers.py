from __future__ import annotations

import csv
from pathlib import Path


def make_csv(tmp_path: Path, data: list[list], header: list[str] | None = None) -> Path:
    p = tmp_path / "test.csv"
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        if header:
            w.writerow(header)
        for row in data:
            w.writerow(row)
    return p

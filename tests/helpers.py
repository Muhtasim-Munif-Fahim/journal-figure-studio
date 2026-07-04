from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path


def make_csv(
    tmp_path: Path,
    rows: Iterable[Iterable[object]],
    *,
    header: Iterable[object] | None = None,
) -> Path:
    path = tmp_path / "data.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if header is not None:
            writer.writerow(header)
        writer.writerows(rows)
    return path

from __future__ import annotations

import csv
from pathlib import Path

import pytest
import yaml


SKILL_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "test_data.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "value", "group", "p_value"])
        writer.writerow(["A", 10.5, "control", 0.01])
        writer.writerow(["B", 20.3, "treatment", 0.03])
        writer.writerow(["C", 15.7, "control", 0.05])
        writer.writerow(["D", 25.1, "treatment", 0.001])
        writer.writerow(["E", 30.2, "control", 0.02])
    return path


@pytest.fixture
def sample_csv_missing(tmp_path: Path) -> Path:
    path = tmp_path / "test_missing.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "value", "group"])
        writer.writerow(["A", 10.5, "control"])
        writer.writerow(["B", "", "treatment"])
        writer.writerow(["C", 15.7, ""])
        writer.writerow(["D", 25.1, "treatment"])
    return path


@pytest.fixture
def training_csv(tmp_path: Path) -> Path:
    path = tmp_path / "training.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "train_loss", "val_loss", "accuracy"])
        for i in range(1, 21):
            writer.writerow([i, 1.0 / i, 0.8 / i, min(0.95, i * 0.05)])
    return path


@pytest.fixture
def heatmap_csv(tmp_path: Path) -> Path:
    path = tmp_path / "heatmap.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["row", "col", "value"])
        for r in range(3):
            for c in range(4):
                writer.writerow([f"R{r}", f"C{c}", r * c])
    return path


@pytest.fixture
def universal_profile() -> dict:
    path = SKILL_ROOT / "assets" / "profiles" / "universal.yaml"
    return yaml.safe_load(path.read_text())

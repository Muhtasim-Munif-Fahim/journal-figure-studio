"""Shared helpers for Journal Figure Studio scripts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return payload


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_table(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(source)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(source)
    if suffix == ".json":
        return pd.read_json(source)
    if suffix == ".jsonl":
        return pd.read_json(source, lines=True)
    raise ValueError(f"Unsupported tabular format: {source.suffix}")


def resolve_request_path(request_path: str | Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else Path(request_path).resolve().parent / path


def profile_path(profile_id: str, profiles_dir: str | Path | None = None) -> Path:
    root = Path(profiles_dir) if profiles_dir else SKILL_ROOT / "assets" / "profiles"
    return root / f"{profile_id}.yaml"

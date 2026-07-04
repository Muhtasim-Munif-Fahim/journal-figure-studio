"""Shared helpers for Journal Figure Studio scripts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pandas as pd
import yaml

SKILL_ROOT: Path = Path(__file__).resolve().parents[1]
"""Root directory of the project (parent of scripts/)."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file does not contain a YAML mapping.
    """
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(
            f"YAML file not found: {resolved}. "
            f"Check that the path is correct and the file exists."
        )
    if resolved.stat().st_size == 0:
        raise ValueError(f"YAML file is empty: {resolved}")
    with resolved.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(
            f"{path} must contain a YAML mapping (got {type(payload).__name__})"
        )
    return payload


def write_json(first: str | Path | Any, second: str | Path | Any) -> None:
    """Write a JSON-serialisable object to a file with sorted keys and indentation.

    Accepts both ``write_json(path, payload)`` and the older
    ``write_json(payload, path)`` calling convention.
    """
    if isinstance(first, (str, Path)):
        path, payload = first, second
    else:
        payload, path = first, second
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sha256(file_path: str | Path) -> str:
    """Compute the SHA-256 hex digest of a file.

    Args:
        file_path: Path to the file.

    Returns:
        Lowercase hex string (64 characters).
    """
    digest = hashlib.sha256()
    resolved = Path(file_path)
    with resolved.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


VALID_NUMERIC_KINDS: set[str] = {"i", "u", "f", "c"}

TABLE_FORMAT_READERS: dict[str, Any] = {
    ".csv": None,
    ".parquet": pd.read_parquet,
    ".pq": pd.read_parquet,
    ".json": pd.read_json,
    ".jsonl": lambda p, **kw: pd.read_json(p, lines=True, **kw),
    ".feather": pd.read_feather,
}


def _read_csv_preserving_text(file_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(file_path, dtype=str, keep_default_na=True)
    for column in frame.columns:
        values = frame[column]
        if values.astype(str).str.match(r"^\s|\s$").any():
            continue
        numeric = pd.to_numeric(values, errors="coerce")
        if numeric.notna().all():
            frame[column] = numeric
    return frame


def read_table(file_path: str | Path) -> pd.DataFrame:
    """Read tabular data from a file into a pandas DataFrame.

    Supported formats: CSV, Parquet, JSON, JSONL, Excel (.xls/.xlsx), Feather.

    Args:
        file_path: Path to the data file.

    Returns:
        Parsed DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported.
    """
    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(f"Data file not found: {source}")
    suffix = source.suffix.lower()
    if suffix == ".csv":
        return _read_csv_preserving_text(source)
    reader = TABLE_FORMAT_READERS.get(suffix)
    if reader is None:
        raise ValueError(
            f"Unsupported file format: {suffix}. "
            f"Supported: {', '.join(sorted(TABLE_FORMAT_READERS))}"
        )
    return cast(pd.DataFrame, reader(source))


def resolve_request_path(
    value: str | Path,
    request_path: str | Path,
) -> Path:
    """Resolve a path relative to the request file's directory.

    Absolute paths are returned unchanged.
    Relative paths are resolved against the request file's parent.

    Args:
        request_path: Path to the request YAML file.
        value: Path value from the request (may be relative or absolute).

    Returns:
        Resolved absolute Path.
    """
    first = Path(value)
    second = Path(request_path)
    if first.suffix.lower() in {".yaml", ".yml"}:
        first, second = second, first
    path = first
    if path.is_absolute() or str(path).startswith(("/", "\\")):
        return path
    base = second.parent if second.suffix else second
    result = base / path
    return result.resolve() if second.suffix else result


def profile_path(
    profile_id: str,
    profiles_dir: str | Path | None = None,
) -> Path:
    """Resolve the path to a profile YAML file.

    Args:
        profile_id: Profile name (without .yaml extension).
        profiles_dir: Custom profiles directory. Falls back to bundled profiles.

    Returns:
        Path to the profile YAML file.
    """
    root = Path(profiles_dir) if profiles_dir else SKILL_ROOT / "assets" / "profiles"
    path = root / f"{profile_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    return path

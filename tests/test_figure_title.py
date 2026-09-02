"""Tests for the figure title and subtitle feature."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import yaml

from scripts.render_recipe import _apply_figure_title
from scripts.validate_request import validate_request


def _make_request_yaml(tmp_path: Path, *, figure_overrides: dict | None = None) -> Path:
    request = {
        "figure_id": "title-fig",
        "research_field": "computer_science",
        "profile": "universal",
        "layout": "single",
        "data_paths": [],
        "analysis_script": str(tmp_path / "dummy_script.py"),
        "claim": "Our method improves accuracy.",
        "caption_takeaway": "Main result shows improvement",
        "figure": {
            "type": "bar",
            "source": str(tmp_path / "data.csv"),
            "x": "category",
            "y": "value",
            "xlabel": "Category",
            "ylabel": "Value",
        },
        "output_dir": str(tmp_path / "output"),
    }
    if figure_overrides:
        request["figure"].update(figure_overrides)
    path = tmp_path / "request.yaml"
    (tmp_path / "dummy_script.py").write_text("# dummy")
    (tmp_path / "data.csv").write_text("category,value\nA,1\nB,2\n", encoding="utf-8")
    path.write_text(yaml.safe_dump(request, sort_keys=False), encoding="utf-8")
    return path


def test_apply_figure_title_adds_suptitle_when_present() -> None:
    fig, ax = plt.subplots()
    _apply_figure_title(fig, {"title": "Accuracy across models"})
    text = "".join(child.get_text() for child in fig.texts)
    assert "Accuracy across models" in text
    plt.close(fig)


def test_apply_figure_title_with_subtitle_adds_both_lines() -> None:
    fig, ax = plt.subplots()
    _apply_figure_title(fig, {"title": "Accuracy", "subtitle": "on the held-out test set"})
    all_text = "".join(child.get_text() for child in fig.texts)
    assert "Accuracy" in all_text
    assert "held-out test set" in all_text
    plt.close(fig)


def test_apply_figure_title_omits_when_absent() -> None:
    fig, ax = plt.subplots()
    _apply_figure_title(fig, {})
    assert len(fig.texts) == 0
    plt.close(fig)


def test_apply_figure_title_ignores_blank_string() -> None:
    fig, ax = plt.subplots()
    _apply_figure_title(fig, {"title": "   ", "subtitle": ""})
    assert len(fig.texts) == 0
    plt.close(fig)


def test_apply_figure_title_respects_fontsize_overrides() -> None:
    fig, ax = plt.subplots()
    _apply_figure_title(fig, {"title": "Big", "title_fontsize": 16, "subtitle": "Small", "subtitle_fontsize": 8})
    text_pieces = list(fig.texts)
    assert len(text_pieces) >= 2
    sizes = [t.get_fontsize() for t in text_pieces]
    assert 16 in sizes
    assert 8 in sizes
    plt.close(fig)


def test_request_with_title_validates(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"title": "Model comparison"},
    )
    assert validate_request(path) == []


def test_request_with_title_and_subtitle_validates(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"title": "Model comparison", "subtitle": "after fine-tuning"},
    )
    assert validate_request(path) == []


def test_request_with_oversized_title_warns(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"title": "X" * 300},
    )
    errors = validate_request(path)
    assert any("figure.title exceeds" in e for e in errors)


def test_request_with_oversized_subtitle_warns(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"title": "Ok", "subtitle": "Y" * 400},
    )
    errors = validate_request(path)
    assert any("figure.subtitle exceeds" in e for e in errors)


def test_request_with_non_string_title_warns(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"title": 42},
    )
    errors = validate_request(path)
    assert any("figure.title must be a string" in e for e in errors)


def test_request_with_non_string_subtitle_warns(tmp_path: Path) -> None:
    path = _make_request_yaml(
        tmp_path,
        figure_overrides={"subtitle": ["list", "not", "allowed"]},
    )
    errors = validate_request(path)
    assert any("figure.subtitle must be a string" in e for e in errors)
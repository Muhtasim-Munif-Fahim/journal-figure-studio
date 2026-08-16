from __future__ import annotations

import json

from scripts.compare_packages import compare_metadata, main


def _metadata(**overrides):
    value = {
        "figure_id": "figure-1",
        "profile": {"id": "universal", "version": 1},
        "layout": "single",
        "dimensions_inches": {"width": 3.35, "height": 2.28},
        "inputs": {"data.csv": "aaa"},
        "outputs": {"figure-1.pdf": "bbb"},
        "studio_version": "0.2.0",
        "python": "3.12.0",
    }
    value.update(overrides)
    return value


def test_identical_metadata_reports_no_change() -> None:
    metadata = _metadata()
    report = compare_metadata(metadata, dict(metadata))
    assert report["status"] == "identical"


def test_hash_and_environment_changes_are_classified() -> None:
    baseline = _metadata()
    current = _metadata(
        inputs={"data.csv": "new", "covariates.csv": "ccc"},
        outputs={},
        python="3.13.0",
    )
    report = compare_metadata(baseline, current)
    assert report["inputs"]["changed"] == ["data.csv"]
    assert report["inputs"]["added"] == ["covariates.csv"]
    assert report["outputs"]["removed"] == ["figure-1.pdf"]
    assert report["environment"]["python"]["current"] == "3.13.0"
    assert report["status"] == "changed"


def test_cli_accepts_package_directories_and_can_fail_on_change(
    tmp_path, capsys
) -> None:
    baseline = tmp_path / "baseline"
    current = tmp_path / "current"
    baseline.mkdir()
    current.mkdir()
    (baseline / "figure_metadata.json").write_text(
        json.dumps(_metadata()), encoding="utf-8"
    )
    (current / "figure_metadata.json").write_text(
        json.dumps(_metadata(layout="double")), encoding="utf-8"
    )
    code = main([str(baseline), str(current), "--json", "--fail-on-change"])
    assert code == 1
    assert json.loads(capsys.readouterr().out)["layout_changed"] is True

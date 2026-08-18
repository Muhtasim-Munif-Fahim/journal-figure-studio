from __future__ import annotations

import json
from pathlib import Path

from scripts import render_batch as batch_module


def test_render_batch_processes_independent_requests(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_render(argv):
        calls.append(list(argv))
        return 2 if "bad.yaml" in argv else 0

    monkeypatch.setattr(batch_module, "render_one", fake_render)
    summary = batch_module.render_batch(
        ["good.yaml", "bad.yaml", "next.yaml"], validate_only=True
    )
    assert summary["processed"] == 3
    assert summary["succeeded"] == 2
    assert summary["failed"] == 1
    assert all("--validate-only" in call for call in calls)


def test_render_batch_can_stop_and_write_report(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(batch_module, "render_one", lambda argv: 1)
    report = tmp_path / "reports" / "batch.json"
    exit_code = batch_module.main(
        ["bad.yaml", "never.yaml", "--stop-on-error", "--report", str(report)]
    )
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert exit_code == 1
    assert payload["requested"] == 2
    assert payload["processed"] == 1

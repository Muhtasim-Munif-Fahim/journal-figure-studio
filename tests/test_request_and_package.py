import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_render_and_check_complete_publication_package(tmp_path: Path) -> None:
    data = tmp_path / "results.csv"
    pd.DataFrame({"method": ["Baseline", "Method"], "score": [0.72, 0.81], "ci_low": [0.69, 0.78], "ci_high": [0.75, 0.84]}).to_csv(data, index=False)
    analysis = tmp_path / "analysis.py"
    analysis.write_text("# Source analysis recorded for test fixture.\n", encoding="utf-8")
    request = {
        "figure_id": "comparison",
        "research_field": "computer_science_ml",
        "profile": "computer_science_ml",
        "layout": "single",
        "data_paths": [str(data)],
        "analysis_script": str(analysis),
        "claim": "Method exceeds the baseline on the supplied metric.",
        "caption_takeaway": "Method has the highest reported mean score; error bars show 95% confidence intervals.",
        "figure": {"type": "bar", "source": str(data), "x": "method", "y": "score", "lower": "ci_low", "upper": "ci_high", "xlabel": "Method", "ylabel": "Score"},
        "output_dir": str(tmp_path / "package"),
        "export_tiff": False,
    }
    request_path = tmp_path / "figure_request.yaml"
    request_path.write_text(yaml.safe_dump(request), encoding="utf-8")
    subprocess.run([sys.executable, str(SCRIPTS / "validate_request.py"), str(request_path)], check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "render_recipe.py"), "--request", str(request_path)], check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "check_package.py"), "--package", str(tmp_path / "package")], check=True)
    assert (tmp_path / "package" / "figure_audit.json").exists()
    subprocess.run([sys.executable, "figure.py", "--request", "figure_request.yaml", "--profiles-dir", "profiles"], cwd=tmp_path / "package", check=True)

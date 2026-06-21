"""Check output formats, dimensions, profile settings, and provenance metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.image as mpimg

from common import load_yaml, write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    args = parser.parse_args()
    package = Path(args.package)
    metadata = json.loads((package / "figure_metadata.json").read_text(encoding="utf-8"))
    profile_id = metadata["profile"]["id"]
    profile_path = package / "profiles" / f"{profile_id}.yaml"
    if not profile_path.exists():
        # Support publication packages created before profiles were namespaced.
        profile_path = package / "profile.yaml"
    profile = load_yaml(profile_path)
    figure_id = metadata["figure_id"]
    errors: list[str] = []
    required = [
        package / "figure.py",
        package / "common.py",
        package / "figure_request.yaml",
        profile_path,
        package / "caption.md",
        package / "latex_include.tex",
        package / "word_insertion.txt",
    ]
    required.extend(package / f"{figure_id}.{extension}" for extension in profile["formats"])
    errors.extend(f"missing output: {path.name}" for path in required if not path.exists())
    pdf_path = package / f"{figure_id}.pdf"
    if pdf_path.exists() and not pdf_path.read_bytes().startswith(b"%PDF"):
        errors.append("PDF output is invalid")
    png_path = package / f"{figure_id}.png"
    if png_path.exists():
        image = mpimg.imread(png_path)
        width_inches = metadata["dimensions_inches"][0]
        min_pixels = int(width_inches * int(profile["raster_dpi"]) * 0.95)
        if image.shape[1] < min_pixels:
            errors.append(f"PNG width {image.shape[1]} is below expected {min_pixels} pixels")
    if int(profile["fonts"]["minimum_pt"]) < 7:
        errors.append("profile minimum font size is below 7pt")
    status = "pass" if not errors else "block"
    report = {"status": status, "profile": profile["id"], "errors": errors, "metadata": metadata}
    write_json(package / "figure_audit.json", report)
    print(json.dumps(report, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

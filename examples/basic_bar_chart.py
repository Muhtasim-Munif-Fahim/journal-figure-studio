#!/usr/bin/env python3
"""End-to-end example: render a bar chart from the bundled example data.

Usage:
    python examples/basic_bar_chart.py

This script demonstrates the full figure-studio pipeline:
1. Load and inspect data
2. Validate the figure request
3. Render the figure with bundled profile
4. Audit the output package
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.render_recipe import main as render


def run_example() -> int:
    print("=" * 60)
    print("journal-figure-studio: Basic Bar Chart Example")
    print("=" * 60)

    example_request = Path("assets/figure_request.example.yaml")
    if not example_request.exists():
        print(f"ERROR: Example request not found at {example_request}")
        return 1

    print(f"\n1. Rendering figure from: {example_request}")
    print(f"   (uses example_data.csv with 3 rows x 4 columns)\n")

    sys.argv = ["render_recipe.py", "--request", str(example_request), "--verbose"]
    return render()


if __name__ == "__main__":
    sys.exit(run_example())

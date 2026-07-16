#!/usr/bin/env python3
"""Verify that the package imports and basic functionality works.

Usage:
    python scripts/verify_package.py

Exits with code 0 if all checks pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

CHECKS: list[tuple[str, callable]] = []


def check(name: str, fn: callable) -> None:
    CHECKS.append((name, fn))


def run_all() -> int:
    passed = 0
    failed = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"  [OK] {name}")
            passed += 1
        except Exception as exc:
            print(f"  [FAIL] {name}: {exc}")
            failed += 1
    print(f"\n{passed}/{passed + failed} checks passed")
    return 0 if failed == 0 else 1


check("version import", lambda: __import__("scripts.version").version.__version__)
check("common import", lambda: __import__("scripts.common"))
check("validate_profile import", lambda: __import__("scripts.validate_profile"))
check("validate_request import", lambda: __import__("scripts.validate_request"))
check("render_recipe import", lambda: __import__("scripts.render_recipe"))
check("check_package import", lambda: __import__("scripts.check_package"))
check("inspect_results import", lambda: __import__("scripts.inspect_results"))
check("create_venue_profile import", lambda: __import__("scripts.create_venue_profile"))
check("logging_config import", lambda: __import__("scripts.logging_config"))
check("constants import", lambda: __import__("scripts.constants"))
check("exit_codes import", lambda: __import__("scripts.exit_codes"))

check("profile loads", lambda: __import__("scripts.common", fromlist=["load_yaml"]).load_yaml(
    Path(__file__).resolve().parent.parent / "assets" / "profiles" / "universal.yaml"
))

if __name__ == "__main__":
    sys.exit(run_all())

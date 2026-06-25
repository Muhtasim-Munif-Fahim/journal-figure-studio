from __future__ import annotations

import importlib
import pkgutil

import scripts


def test_all_scripts_modules_importable():
    for importer, name, ispkg in pkgutil.walk_packages(scripts.__path__, prefix="scripts."):
        if ispkg:
            continue
        module = importlib.import_module(name)
        assert module is not None, f"Failed to import {name}"

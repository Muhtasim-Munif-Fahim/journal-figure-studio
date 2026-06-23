"""Package entry point for `python -m scripts`."""
from __future__ import annotations

from scripts.render_recipe import main

if __name__ == "__main__":
    raise SystemExit(main())

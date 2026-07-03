from __future__ import annotations

from pathlib import Path

from scripts.logging_config import setup_logger, enable_debug


class TestLogging:
    def test_create(self):
        logger = setup_logger("test")
        assert logger is not None

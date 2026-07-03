from __future__ import annotations

from pathlib import Path

from scripts.logging_config import setup_logger, enable_debug


class TestLog:
    def test_setup(self):
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"

    def test_enable_debug(self):
        logger = setup_logger("test_debug", level=30)
        enable_debug(logger)
        assert logger.level == 10

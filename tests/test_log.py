from __future__ import annotations

from scripts.logging_config import enable_debug, setup_logger


class TestLog:
    def test_setup(self):
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"

    def test_enable_debug(self):
        logger = setup_logger("test_debug", level=30)
        enable_debug(logger)
        assert logger.level == 10

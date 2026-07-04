from __future__ import annotations

from scripts.logging_config import enable_debug, setup_logger


class TestLoggingConfig:
    def test_setup_returns_logger(self):
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"

    def test_enable_debug_changes_level(self):
        logger = setup_logger("test_debug", level=30)
        assert logger.level == 30
        enable_debug(logger)
        assert logger.level == 10

    def test_multiple_calls_same_logger(self):
        l1 = setup_logger("test_multi")
        l2 = setup_logger("test_multi")
        assert l1 is l2

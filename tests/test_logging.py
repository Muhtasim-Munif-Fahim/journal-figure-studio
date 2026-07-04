from __future__ import annotations

from scripts.logging_config import setup_logger


class TestLogging:
    def test_create(self):
        logger = setup_logger("test")
        assert logger is not None

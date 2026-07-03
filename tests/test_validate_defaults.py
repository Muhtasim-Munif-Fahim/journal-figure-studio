from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validate_request import validate_request, DEFAULT_MAX_CAPTION_LENGTH, DEFAULT_MAX_CLAIM_LENGTH


class TestValidateDefaults:
    def test_caption_length_default(self):
        assert DEFAULT_MAX_CAPTION_LENGTH == 200

    def test_claim_length_default(self):
        assert DEFAULT_MAX_CLAIM_LENGTH == 1000

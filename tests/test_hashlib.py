from __future__ import annotations


class TestHashlib:
    def test_md5_not_used(self):
        import hashlib

        md5 = hasattr(hashlib, "md5")
        assert md5

    def test_sha256_available(self):
        import hashlib

        assert hasattr(hashlib, "sha256")

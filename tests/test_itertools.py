from __future__ import annotations

import itertools


class TestIterTools:
    def test_product(self):
        result = list(itertools.product([1, 2], ["a", "b"]))
        assert len(result) == 4

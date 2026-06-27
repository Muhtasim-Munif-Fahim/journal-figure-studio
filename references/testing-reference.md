# Testing Guide

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_common.py -v
```

Run with coverage:
```bash
pytest --cov=scripts --cov-report=term-missing
```

Our tests cover:
- Unit tests for each script module
- Parameterized tests for all 10 figure types
- Edge cases (empty data, missing columns, corrupt files)
- Integration tests for full pipeline (TIFF, SVG export)
- CLI tests (--help, --version)
- Profile validation tests

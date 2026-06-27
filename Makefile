.PHONY: install test test-cov lint format typecheck security clean all

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ --cov=scripts --cov-report=term-missing -v

test-slow:
	python -m pytest tests/ -m slow -v

test-quick:
	python -m pytest tests/ -m "not slow" -v

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .

typecheck:
	mypy scripts/

security:
	bandit -r scripts/ -ll

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true

all: lint typecheck test

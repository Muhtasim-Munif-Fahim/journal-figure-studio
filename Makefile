.PHONY: test lint typecheck clean install

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ --cov=scripts --cov-report=term-missing -v

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .

typecheck:
	mypy scripts/

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true

all: lint typecheck test

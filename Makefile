.PHONY: all format install lint bandit test test-unit test-integration ty

all: bandit format lint test

format:
	uv run ruff format app/ tests/

install:
	uv sync

lint:
	uv run ruff check app/ tests/ --fix

bandit:
	uv run -m bandit --severity-level medium --confidence-level high -r app/ -vvv

test:
	uv run pytest tests/ --cov=app --cov-report=term-missing --cov-branch

ty:
	uv run ty check

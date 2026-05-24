.PHONY: setup test lint typecheck format run cli docker-build docker-run

export UV_CACHE_DIR ?= .uv-cache

setup:
	uv sync --all-groups

test:
	uv run pytest

lint:
	uv run python -m black --check src tests main.py
	uv run python -m ruff check src tests main.py

typecheck:
	uv run python -m mypy

format:
	uv run python -m black src tests main.py
	uv run python -m ruff check --fix src tests main.py

run:
	uv run python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html

cli:
	uv run ran-kpi-analyzer --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html

docker-build:
	docker build -t ran-kpi-analyzer .

docker-run:
	docker run --rm ran-kpi-analyzer

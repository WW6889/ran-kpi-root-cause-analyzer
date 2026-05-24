.PHONY: test lint format run

export UV_CACHE_DIR ?= .uv-cache

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

run:
	uv run python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html

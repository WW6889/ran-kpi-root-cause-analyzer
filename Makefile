.PHONY: setup test lint typecheck format run docker-build docker-run

setup:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -r requirements-dev.txt

test:
	.venv/bin/python -m pytest

lint:
	.venv/bin/black --check src tests main.py
	.venv/bin/flake8 src tests main.py

typecheck:
	.venv/bin/mypy

format:
	.venv/bin/black src tests main.py

run:
	.venv/bin/python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html

docker-build:
	docker build -t ran-kpi-analyzer .

docker-run:
	docker run --rm ran-kpi-analyzer


# Final Test Summary

Verification is run with `uv` from the repository root.

## Commands

```bash
uv sync
uv lock --check
uv run pytest -v
uv run pytest --cov=src --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html
uv run ran-kpi-analyzer --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html
docker build -t ran-kpi-analyzer .
docker run --rm ran-kpi-analyzer
```

## Expected Results

| Check | Expected result |
| --- | --- |
| `uv sync` | Environment created from `uv.lock` |
| Ruff linting | Pass |
| Ruff formatting | Pass |
| Mypy type checking | Pass |
| Pytest | Pass |
| Coverage | Reported in terminal |
| CLI report generation | Pass |
| Docker build/run | Pass when Docker is available |

The project intentionally does not chase artificial 100% coverage. The uncovered lines are mostly defensive fallback paths and command-entry wrappers.

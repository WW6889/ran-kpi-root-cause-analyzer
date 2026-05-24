# Final Test Summary

Verification is run with `uv` from the repository root.

## Commands

```bash
uv sync
uv run python -m black --check src tests main.py
uv run python -m ruff check src tests main.py
uv run python -m mypy
MPLCONFIGDIR=/tmp/matplotlib uv run pytest -vv
MPLCONFIGDIR=/tmp/matplotlib uv run python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html
docker build -t ran-kpi-analyzer .
docker run --rm ran-kpi-analyzer
```

## Expected Results

| Check | Expected result |
| --- | --- |
| `uv sync` | Environment created from `uv.lock` |
| Black formatting | Pass |
| Ruff linting | Pass |
| Mypy type checking | Pass |
| Pytest | 19 tests pass |
| Coverage | Approximately 95% total line coverage |
| CLI report generation | Pass |
| Docker build/run | Verified by GitHub Actions on Ubuntu; local verification requires Docker |

The project intentionally does not chase artificial 100% coverage. The uncovered lines are mostly defensive fallback paths and command-entry wrappers.

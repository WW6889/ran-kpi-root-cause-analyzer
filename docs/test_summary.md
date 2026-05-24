# Final Test Summary

Verification was run locally in the project virtual environment on macOS with Python 3.12.10.

## Commands

```bash
.venv/bin/black --check src tests main.py
.venv/bin/flake8 src tests main.py
.venv/bin/mypy
MPLCONFIGDIR=/private/tmp/mplconfig .venv/bin/python -m pytest
MPLCONFIGDIR=/private/tmp/mplconfig .venv/bin/python main.py --input data/raw/sample_ran_kpi_data.csv --output reports/example_report.html
docker build -t ran-kpi-analyzer .
```

## Results

| Check | Result |
| --- | --- |
| Black formatting | Passed |
| Flake8 linting | Passed |
| Mypy type checking | Passed |
| Pytest | 19 passed |
| Coverage | 96% total line coverage |
| CLI report generation | Passed |
| Docker build | Not executed locally: Docker command is not installed on this host |

## Coverage Report

```text
Name                                        Stmts   Miss  Cover
-------------------------------------------------------------------------
main.py                                        48      3    94%
src/ran_kpi_analyzer/__init__.py                1      0   100%
src/ran_kpi_analyzer/anomaly_detection.py      32      0   100%
src/ran_kpi_analyzer/config.py                 26      0   100%
src/ran_kpi_analyzer/data_loader.py            32      6    81%
src/ran_kpi_analyzer/exceptions.py              1      0   100%
src/ran_kpi_analyzer/modeling.py               50      2    96%
src/ran_kpi_analyzer/preprocessing.py          40      0   100%
src/ran_kpi_analyzer/report_generator.py       19      0   100%
src/ran_kpi_analyzer/root_cause.py             91      2    98%
src/ran_kpi_analyzer/synthetic_data.py         55      2    96%
src/ran_kpi_analyzer/visualization.py          65      2    97%
-------------------------------------------------------------------------
TOTAL                                         460     17    96%
```

The uncovered lines are mostly defensive fallback paths, command-entry wrappers, and `__main__` execution guards. The project intentionally does not chase artificial 100% coverage.


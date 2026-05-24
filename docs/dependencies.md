# Dependency List

Runtime dependencies are pinned in `requirements.txt`:

- `pandas==3.0.3`
- `numpy==2.4.6`
- `matplotlib==3.10.9`
- `jinja2==3.1.6`
- `scikit-learn==1.8.0`
- `xgboost==3.2.0`
- `shap==0.51.0`

Development and QA dependencies are pinned in `requirements-dev.txt`:

- `black==25.1.0`
- `flake8==7.1.2`
- `mypy==1.14.1`
- `pytest==9.0.3`
- `pytest-cov==6.0.0`
- `pre-commit==4.0.1`

The repository uses pinned dependencies to make local results and GitHub Actions behavior reproducible.


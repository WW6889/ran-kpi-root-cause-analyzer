# Dependency List

Runtime and development dependencies are declared in `pyproject.toml` and resolved in `uv.lock`.

## Runtime Dependencies

- `jinja2>=3.1,<4`
- `matplotlib>=3.10,<4`
- `numpy>=2.2,<3`
- `pandas>=2.2,<4`
- `scikit-learn>=1.6,<2`
- `shap>=0.48,<0.52`
- `xgboost>=3.0,<4`

## Development Dependencies

The `dev` dependency group contains:

- `black==25.1.0`
- `mypy==1.14.1`
- `pre-commit==4.0.1`
- `pytest==9.0.3`
- `pytest-cov==6.0.0`
- `ruff==0.8.6`

Use `uv sync --all-groups` for a full local development environment. CI uses `uv sync --frozen --all-groups` to ensure the lockfile is honored.

# Contributing

This repository is maintained as an engineering portfolio project. Contributions should keep the project practical, reproducible, and technically conservative.

## Development Setup

Install `uv`, then run:

```bash
uv sync
make test
make lint
```

## Contribution Rules

- Keep root-cause logic explainable and tied to documented KPI assumptions.
- Do not add dashboard or web UI complexity unless there is a clear validation use case.
- Do not claim field accuracy from synthetic data.
- Add tests for new validation rules, edge cases, and report outputs.
- Update `docs/engineering_assumptions.md` whenever threshold logic changes.

## Quality Gates

Before opening a pull request:

```bash
make format
make lint
make test
make run
```

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY data ./data
COPY main.py ./

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-sync", "ran-kpi-analyzer", "--input", "data/raw/sample_ran_kpi_data.csv", "--output", "reports/example_report.html"]

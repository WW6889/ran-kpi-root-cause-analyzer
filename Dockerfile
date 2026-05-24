FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /bin/

ENV MPLCONFIGDIR=/tmp/matplotlib \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY data ./data
COPY main.py ./

RUN uv sync --frozen --no-dev

CMD [".venv/bin/ran-kpi-analyzer", "--input", "data/raw/sample_ran_kpi_data.csv", "--output", "reports/example_report.html"]

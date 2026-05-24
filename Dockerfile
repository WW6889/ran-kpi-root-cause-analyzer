FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY main.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py", "--input", "data/raw/sample_ran_kpi_data.csv", "--output", "reports/example_report.html"]

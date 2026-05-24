from __future__ import annotations

import pandas as pd

from main import main, run_analysis
from ran_kpi_analyzer.synthetic_data import generate_synthetic_dataset


def test_run_analysis_generates_report_and_figures(tmp_path):
    input_path = tmp_path / "sample.csv"
    output_path = tmp_path / "report.html"
    generate_synthetic_dataset(input_path, periods=96, seed=7)

    report_path = run_analysis(input_path, output_path)

    assert report_path.exists()
    html = report_path.read_text(encoding="utf-8")
    assert "Model Diagnostics" in html
    assert "Root-Cause Analysis Report" in html
    assert len(list((tmp_path / "figures").glob("*.png"))) == 5


def test_cli_returns_nonzero_for_invalid_input(tmp_path, monkeypatch):
    bad_path = tmp_path / "bad.csv"
    pd.DataFrame([{"timestamp": "bad"}]).to_csv(bad_path, index=False)
    monkeypatch.setattr(
        "sys.argv",
        ["main.py", "--input", str(bad_path), "--output", str(tmp_path / "out.html")],
    )

    assert main() == 2

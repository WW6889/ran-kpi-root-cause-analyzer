"""Command-line entry point for the RAN KPI Root-Cause Analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path

from ran_kpi_analyzer.anomaly_detection import detect_anomalies
from ran_kpi_analyzer.data_loader import load_kpi_data
from ran_kpi_analyzer.preprocessing import aggregate_cell_kpis, prepare_kpi_data
from ran_kpi_analyzer.report_generator import generate_html_report
from ran_kpi_analyzer.root_cause import (
    add_root_cause_labels,
    rank_kpi_contributors,
    summarize_root_causes,
)
from ran_kpi_analyzer.visualization import generate_all_plots


def run_analysis(input_path: str | Path, output_path: str | Path) -> Path:
    """Run the complete analysis workflow and return the report path."""
    output = Path(output_path)
    figures_dir = output.parent / "figures"

    loaded = load_kpi_data(input_path)
    prepared = prepare_kpi_data(loaded)
    anomalous = detect_anomalies(prepared)
    analyzed = add_root_cause_labels(anomalous)
    cell_summary = aggregate_cell_kpis(analyzed)
    root_cause_summary = summarize_root_causes(analyzed)
    contributors = rank_kpi_contributors(analyzed)
    figure_paths = generate_all_plots(analyzed, contributors, figures_dir)

    return generate_html_report(
        analyzed=analyzed,
        cell_summary=cell_summary,
        root_cause_summary=root_cause_summary,
        contributors=contributors,
        figure_paths=figure_paths,
        output_path=output,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze RAN KPI degradation and root causes.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output HTML report path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_analysis(args.input, args.output)
    print(f"Report generated: {report}")


if __name__ == "__main__":
    main()


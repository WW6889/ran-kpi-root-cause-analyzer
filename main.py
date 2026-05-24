"""Command-line entry point for the RAN KPI Root-Cause Analyzer."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ran_kpi_analyzer.anomaly_detection import detect_anomalies
from ran_kpi_analyzer.config import DEFAULT_CONFIG, AnalyzerConfig
from ran_kpi_analyzer.data_loader import load_kpi_data
from ran_kpi_analyzer.exceptions import DataValidationError
from ran_kpi_analyzer.modeling import train_degradation_model
from ran_kpi_analyzer.preprocessing import aggregate_cell_kpis, prepare_kpi_data
from ran_kpi_analyzer.report_generator import generate_html_report
from ran_kpi_analyzer.root_cause import (
    add_root_cause_labels,
    rank_kpi_contributors,
    summarize_root_causes,
)
from ran_kpi_analyzer.visualization import generate_all_plots

LOGGER = logging.getLogger(__name__)


def run_analysis(
    input_path: str | Path,
    output_path: str | Path,
    config: AnalyzerConfig = DEFAULT_CONFIG,
) -> Path:
    """Run the complete analysis workflow and return the report path."""
    output = Path(output_path)
    figures_dir = output.parent / "figures"

    LOGGER.info("Loading KPI data from %s", input_path)
    loaded = load_kpi_data(input_path)
    prepared = prepare_kpi_data(loaded, config)
    anomalous = detect_anomalies(prepared, config)
    analyzed = add_root_cause_labels(anomalous, config)
    cell_summary = aggregate_cell_kpis(analyzed)
    root_cause_summary = summarize_root_causes(analyzed)
    contributors = rank_kpi_contributors(analyzed)
    model_diagnostics, model_importance = train_degradation_model(analyzed, config)
    figure_paths = generate_all_plots(analyzed, model_importance, figures_dir)

    LOGGER.info("Writing HTML report to %s", output)
    return generate_html_report(
        analyzed=analyzed,
        cell_summary=cell_summary,
        root_cause_summary=root_cause_summary,
        contributors=contributors,
        model_diagnostics=model_diagnostics,
        model_importance=model_importance,
        figure_paths=figure_paths,
        output_path=output,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze RAN KPI degradation and root causes.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output HTML report path")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Console logging level",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        report = run_analysis(args.input, args.output)
    except (DataValidationError, FileNotFoundError, ValueError) as exc:
        LOGGER.error("%s", exc)
        return 2
    print(f"Report generated: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

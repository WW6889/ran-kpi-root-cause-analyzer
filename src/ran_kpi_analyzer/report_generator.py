"""HTML report generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .modeling import ModelDiagnostics
from .root_cause import ROOT_CAUSE_ACTIONS


def _table(frame: pd.DataFrame, columns: list[str], limit: int | None = None) -> str:
    data = frame[columns].head(limit) if limit else frame[columns]
    return data.to_html(
        index=False, classes="data-table", float_format=lambda value: f"{value:.3f}"
    )


def generate_html_report(
    analyzed: pd.DataFrame,
    cell_summary: pd.DataFrame,
    root_cause_summary: pd.DataFrame,
    contributors: pd.DataFrame,
    model_diagnostics: ModelDiagnostics,
    model_importance: pd.DataFrame,
    figure_paths: list[str],
    output_path: str | Path,
) -> Path:
    """Create a self-contained engineering report with linked local figures."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    degraded = analyzed[analyzed["root_cause"] != "healthy_baseline"]
    top_cell = root_cause_summary.iloc[0].to_dict() if not root_cause_summary.empty else {}
    dominant_cause = str(top_cell.get("dominant_root_cause", "healthy_baseline"))
    recommendations = ROOT_CAUSE_ACTIONS.get(dominant_cause, [])
    relative_figures = [Path(path).relative_to(output.parent).as_posix() for path in figure_paths]

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>RAN KPI Root-Cause Analysis Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; color: #1f2933; line-height: 1.45; }}
    h1, h2 {{ color: #183b56; }}
    .summary {{ background: #eef6f6; border-left: 5px solid #2f6f73; padding: 16px 20px; margin: 20px 0; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }}
    .metric {{ border: 1px solid #d9e2ec; padding: 14px; border-radius: 6px; background: #fff; }}
    .metric strong {{ display: block; font-size: 24px; color: #0b7285; }}
    .data-table {{ border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 14px; }}
    .data-table th {{ background: #183b56; color: white; text-align: left; }}
    .data-table th, .data-table td {{ border: 1px solid #d9e2ec; padding: 8px 10px; }}
    img {{ max-width: 100%; border: 1px solid #d9e2ec; margin: 10px 0 26px; }}
    code {{ background: #f1f5f8; padding: 2px 5px; }}
  </style>
</head>
<body>
  <h1>RAN KPI Root-Cause Analysis Report</h1>
  <div class="summary">
    <strong>Executive summary.</strong>
    Analyzed {len(analyzed):,} KPI samples from {analyzed["cell_id"].nunique()} cells.
    {len(degraded):,} samples were classified as degraded. The most affected cell is
    <code>{top_cell.get("cell_id", "n/a")}</code> with dominant root cause
    <code>{top_cell.get("dominant_root_cause", "n/a")}</code>.
  </div>
  <div class="grid">
    <div class="metric"><strong>{analyzed["cell_id"].nunique()}</strong>Cells analyzed</div>
    <div class="metric"><strong>{len(degraded)}</strong>Degraded samples</div>
    <div class="metric"><strong>{int(analyzed["anomaly_flag"].sum())}</strong>Anomaly flags</div>
    <div class="metric"><strong>{analyzed["timestamp"].min()}</strong>Start time</div>
  </div>

  <h2>Dataset Overview</h2>
  {_table(cell_summary, ["cell_id", "rsrp_dbm", "sinr_db", "prb_utilization_dl", "throughput_dl_mbps", "latency_ms", "degraded_ratio"], 12)}

  <h2>Degraded Cells and Root Causes</h2>
  {_table(root_cause_summary, ["cell_id", "dominant_root_cause", "samples", "degraded_samples", "dominant_share", "mean_confidence"], 12)}

  <h2>Rule-Based KPI Contributors</h2>
  {_table(contributors, ["kpi", "importance", "direction"], 10)}

  <h2>Model Diagnostics</h2>
  <p>
    Diagnostic model: <code>{model_diagnostics.model_name}</code>.
    Explanation method: <code>{model_diagnostics.explanation_method}</code>.
    Train/test samples: {model_diagnostics.train_samples}/{model_diagnostics.test_samples}.
    Accuracy: {model_diagnostics.accuracy:.3f}; balanced accuracy:
    {model_diagnostics.balanced_accuracy:.3f}.
  </p>
  {_table(model_importance, ["feature", "importance"], 10)}

  <h2>KPI Plots</h2>
  {''.join(f'<img src="{figure}" alt="{Path(figure).stem}">' for figure in relative_figures)}

  <h2>Engineering Interpretation</h2>
  <p>
    The logic separates weak coverage, interference, high-load congestion, and mobility failures
    using transparent evidence scores before ranking the KPIs that most separate degraded behavior
    from the healthy baseline. The RandomForest/SHAP diagnostic is used as a reproducibility check,
    not as an autonomous network optimization claim.
  </p>

  <h2>Recommended Troubleshooting Actions</h2>
  <ul>
    {''.join(f'<li>{item}</li>' for item in recommendations)}
  </ul>

  <h2>Limitations</h2>
  <p>
    This report uses synthetic KPI data. Real operator data is confidential, and field validation
    would require vendor-specific counters, topology context, configuration history, and drive-test
    or trace evidence.
  </p>
</body>
</html>
"""
    output.write_text(html, encoding="utf-8")
    return output

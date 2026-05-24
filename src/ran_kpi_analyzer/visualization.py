"""Plot generation for engineering reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402


def _save(fig: plt.Figure, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_kpi_trends(frame: pd.DataFrame, output_dir: str | Path) -> str:
    fig, ax = plt.subplots(figsize=(11, 5))
    plotted = False
    for cell_id, group in frame.groupby("cell_id"):
        if group["root_cause"].ne("healthy_baseline").any():
            ax.plot(group["timestamp"], group["throughput_dl_mbps"], label=cell_id, linewidth=1.4)
            plotted = True
    if not plotted:
        hourly = frame.groupby("timestamp")["throughput_dl_mbps"].mean()
        ax.plot(hourly.index, hourly.values, label="network_mean", linewidth=1.4)
    ax.set_title("Downlink Throughput Trend for Degraded Cells")
    ax.set_ylabel("Throughput DL (Mbps)")
    ax.set_xlabel("Timestamp")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.25)
    return _save(fig, Path(output_dir) / "kpi_trends.png")


def plot_throughput_vs_latency(frame: pd.DataFrame, output_dir: str | Path) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = frame["root_cause"].astype("category").cat.codes
    ax.scatter(frame["throughput_dl_mbps"], frame["latency_ms"], c=colors, alpha=0.72)
    ax.set_title("Throughput vs Latency")
    ax.set_xlabel("Throughput DL (Mbps)")
    ax.set_ylabel("Latency (ms)")
    ax.grid(True, alpha=0.25)
    return _save(fig, Path(output_dir) / "throughput_vs_latency.png")


def plot_anomaly_timeline(frame: pd.DataFrame, output_dir: str | Path) -> str:
    fig, ax = plt.subplots(figsize=(11, 4.8))
    timeline = frame.groupby("timestamp")["anomaly_flag"].sum()
    ax.bar(timeline.index, timeline.values, width=0.025, color="#b23a48")
    ax.set_title("Anomaly Timeline")
    ax.set_ylabel("Anomalous cell samples")
    ax.set_xlabel("Timestamp")
    ax.grid(True, axis="y", alpha=0.25)
    return _save(fig, Path(output_dir) / "anomaly_timeline.png")


def plot_root_cause_distribution(frame: pd.DataFrame, output_dir: str | Path) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    counts = frame["root_cause"].value_counts()
    ax.barh(counts.index, counts.values, color="#2f6f73")
    ax.set_title("Root-Cause Classification Distribution")
    ax.set_xlabel("Samples")
    ax.grid(True, axis="x", alpha=0.25)
    return _save(fig, Path(output_dir) / "root_cause_distribution.png")


def plot_feature_importance(contributors: pd.DataFrame, output_dir: str | Path) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    top = contributors.head(8).sort_values("importance")
    label_column = "feature" if "feature" in top.columns else "kpi"
    ax.barh(top[label_column], top["importance"], color="#445e93")
    ax.set_title("Model Feature Importance")
    ax.set_xlabel("Normalized mean absolute SHAP value")
    ax.grid(True, axis="x", alpha=0.25)
    return _save(fig, Path(output_dir) / "feature_importance.png")


def generate_all_plots(
    frame: pd.DataFrame, contributors: pd.DataFrame, output_dir: str | Path
) -> list[str]:
    """Generate the required report figures."""
    return [
        plot_kpi_trends(frame, output_dir),
        plot_throughput_vs_latency(frame, output_dir),
        plot_anomaly_timeline(frame, output_dir),
        plot_root_cause_distribution(frame, output_dir),
        plot_feature_importance(contributors, output_dir),
    ]

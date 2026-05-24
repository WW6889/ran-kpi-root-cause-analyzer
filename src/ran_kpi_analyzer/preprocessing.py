"""KPI cleaning, labels, aggregation, and feature engineering."""

from __future__ import annotations

import pandas as pd

from .config import (
    DEFAULT_CONFIG,
    FEATURE_COLUMNS,
    KPI_RANGES,
    AnalyzerConfig,
)
from .exceptions import DataValidationError


def validate_kpi_ranges(frame: pd.DataFrame) -> None:
    """Fail fast when KPI values are outside physically plausible ranges."""
    violations: list[str] = []
    for column, (minimum, maximum) in KPI_RANGES.items():
        invalid = frame[column].lt(minimum) | frame[column].gt(maximum)
        if invalid.any():
            violations.append(
                f"{column} outside [{minimum:g}, {maximum:g}] in {int(invalid.sum())} rows"
            )

    if violations:
        raise DataValidationError("; ".join(violations))


def clean_kpi_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize numeric fields and validate impossible KPI values."""
    data = frame.copy()
    for column in FEATURE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    if data[FEATURE_COLUMNS].isna().any().any():
        invalid_columns = data[FEATURE_COLUMNS].columns[data[FEATURE_COLUMNS].isna().any()]
        raise DataValidationError(f"Non-numeric KPI values found in: {', '.join(invalid_columns)}")

    validate_kpi_ranges(data)
    return data.reset_index(drop=True)


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add derived engineering signals used by anomaly and RCA modules."""
    data = frame.copy()
    data["spectral_quality_index"] = data["sinr_db"] * data["cqi"]
    data["load_pressure_index"] = data["prb_utilization_dl"] * data["active_users"] / 100
    data["service_degradation_index"] = (
        (100 - data["rrc_setup_success_rate"])
        + (100 - data["handover_success_rate"])
        + data["call_drop_rate"] * 100
        + data["packet_loss_rate"] * 100
    )
    data["throughput_per_user"] = data["throughput_dl_mbps"] / data["active_users"].clip(lower=1)
    return data


def add_degradation_labels(
    frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Create degraded-vs-healthy labels from practical RAN thresholds."""
    data = frame.copy()
    degraded = (
        (
            (data["rsrp_dbm"] < config.weak_rsrp_dbm)
            & (data["throughput_dl_mbps"] < config.low_throughput_mbps)
        )
        | ((data["sinr_db"] < config.poor_sinr_db) & (data["cqi"] < config.poor_cqi))
        | (
            (data["prb_utilization_dl"] > config.high_prb_utilization)
            & (data["active_users"] > config.high_active_users)
        )
        | (
            (data["handover_success_rate"] < config.poor_handover_success_rate)
            & (data["call_drop_rate"] > config.high_call_drop_rate)
        )
        | (data["packet_loss_rate"] > config.high_packet_loss_rate)
    )
    data["is_degraded"] = degraded.astype(int)
    return data


def aggregate_cell_kpis(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs by cell for report summaries."""
    aggregations = {
        "rsrp_dbm": "mean",
        "sinr_db": "mean",
        "cqi": "mean",
        "prb_utilization_dl": "mean",
        "throughput_dl_mbps": "mean",
        "latency_ms": "mean",
        "packet_loss_rate": "mean",
        "handover_success_rate": "mean",
        "call_drop_rate": "mean",
        "active_users": "mean",
        "is_degraded": "mean",
    }
    summary = frame.groupby("cell_id", as_index=False).agg(aggregations)
    summary["degraded_ratio"] = summary.pop("is_degraded")
    return summary.sort_values("degraded_ratio", ascending=False).reset_index(drop=True)


def prepare_kpi_data(frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Run the complete preprocessing pipeline."""
    return add_degradation_labels(add_engineered_features(clean_kpi_data(frame)), config)

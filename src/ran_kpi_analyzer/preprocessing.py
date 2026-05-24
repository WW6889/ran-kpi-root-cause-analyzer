"""KPI cleaning, labels, aggregation, and feature engineering."""

from __future__ import annotations

import pandas as pd

from .config import (
    FEATURE_COLUMNS,
    HIGH_ACTIVE_USERS,
    HIGH_DROP_RATE,
    LOW_THROUGHPUT_MBPS,
)


def clean_kpi_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize numeric fields and clamp impossible synthetic KPI values."""
    data = frame.copy()
    for column in FEATURE_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=FEATURE_COLUMNS).copy()
    data["cqi"] = data["cqi"].clip(1, 15)
    data["prb_utilization_dl"] = data["prb_utilization_dl"].clip(0, 100)
    data["throughput_dl_mbps"] = data["throughput_dl_mbps"].clip(lower=0)
    data["latency_ms"] = data["latency_ms"].clip(lower=1)
    data["packet_loss_rate"] = data["packet_loss_rate"].clip(0, 1)
    data["rrc_setup_success_rate"] = data["rrc_setup_success_rate"].clip(0, 100)
    data["handover_success_rate"] = data["handover_success_rate"].clip(0, 100)
    data["call_drop_rate"] = data["call_drop_rate"].clip(0, 1)
    data["active_users"] = data["active_users"].clip(lower=0)
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


def add_degradation_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Create degraded-vs-healthy labels from practical RAN thresholds."""
    data = frame.copy()
    degraded = (
        ((data["rsrp_dbm"] < -105) & (data["throughput_dl_mbps"] < LOW_THROUGHPUT_MBPS))
        | ((data["sinr_db"] < 5) & (data["cqi"] < 7))
        | ((data["prb_utilization_dl"] > 85) & (data["active_users"] > HIGH_ACTIVE_USERS))
        | ((data["handover_success_rate"] < 90) & (data["call_drop_rate"] > HIGH_DROP_RATE))
        | (data["packet_loss_rate"] > 0.03)
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


def prepare_kpi_data(frame: pd.DataFrame) -> pd.DataFrame:
    """Run the complete preprocessing pipeline."""
    return add_degradation_labels(add_engineered_features(clean_kpi_data(frame)))


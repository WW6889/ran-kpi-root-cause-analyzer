"""Anomaly detection for RAN KPI data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS


def add_zscore_anomalies(frame: pd.DataFrame, threshold: float = 2.6) -> pd.DataFrame:
    """Flag KPI rows with unusually high multivariate z-score deviation."""
    data = frame.copy()
    feature_data = data[FEATURE_COLUMNS].astype(float)
    std = feature_data.std(ddof=0).replace(0, 1)
    zscores = (feature_data - feature_data.mean()) / std
    abs_zscores = zscores.abs()
    data["anomaly_score"] = abs_zscores.max(axis=1)
    data["affected_kpi"] = abs_zscores.idxmax(axis=1)
    data["anomaly_flag"] = (data["anomaly_score"] >= threshold).astype(int)
    return data


def add_rolling_deviation(frame: pd.DataFrame, window: int = 6) -> pd.DataFrame:
    """Add rolling throughput deviation per cell."""
    data = frame.sort_values(["cell_id", "timestamp"]).copy()
    rolling = data.groupby("cell_id")["throughput_dl_mbps"].transform(
        lambda values: values.rolling(window=window, min_periods=2).mean()
    )
    data["throughput_rolling_mean"] = rolling.fillna(data["throughput_dl_mbps"])
    data["throughput_deviation"] = data["throughput_dl_mbps"] - data["throughput_rolling_mean"]
    return data


def add_isolation_forest_like_score(frame: pd.DataFrame) -> pd.DataFrame:
    """Add a dependency-light robust distance score similar to IsolationForest output.

    The README and requirements support scikit-learn for production use. This
    fallback keeps the project runnable in minimal environments while preserving
    deterministic anomaly behavior for tests and CI.
    """
    data = frame.copy()
    feature_data = data[FEATURE_COLUMNS].astype(float)
    median = feature_data.median()
    mad = (feature_data - median).abs().median().replace(0, 1)
    robust_distance = ((feature_data - median).abs() / mad).mean(axis=1)
    data["robust_anomaly_score"] = np.log1p(robust_distance)
    return data


def detect_anomalies(frame: pd.DataFrame) -> pd.DataFrame:
    """Run the project anomaly detection stack."""
    return add_isolation_forest_like_score(add_rolling_deviation(add_zscore_anomalies(frame)))


"""Anomaly detection for RAN KPI data."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import DEFAULT_CONFIG, FEATURE_COLUMNS, AnalyzerConfig


def add_robust_zscore_anomalies(
    frame: pd.DataFrame, threshold: float = DEFAULT_CONFIG.zscore_threshold
) -> pd.DataFrame:
    """Flag rows with unusually high robust multivariate KPI deviation."""
    data = frame.copy()
    feature_data = data[FEATURE_COLUMNS].astype(float)
    median = feature_data.median()
    mad = (feature_data - median).abs().median().replace(0, 1)
    zscores = 0.6745 * (feature_data - median) / mad
    abs_zscores = zscores.abs()
    data["anomaly_score"] = abs_zscores.max(axis=1)
    data["affected_kpi"] = abs_zscores.idxmax(axis=1)
    data["anomaly_flag"] = (data["anomaly_score"] >= threshold).astype(int)
    return data


def add_rolling_deviation(
    frame: pd.DataFrame, window: int = DEFAULT_CONFIG.rolling_window
) -> pd.DataFrame:
    """Add rolling throughput deviation per cell."""
    data = frame.sort_values(["cell_id", "timestamp"]).copy()
    rolling = data.groupby("cell_id")["throughput_dl_mbps"].transform(
        lambda values: values.rolling(window=window, min_periods=2).mean()
    )
    data["throughput_rolling_mean"] = rolling.fillna(data["throughput_dl_mbps"])
    data["throughput_deviation"] = data["throughput_dl_mbps"] - data["throughput_rolling_mean"]
    return data


def add_model_anomaly_score(
    frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Add deterministic IsolationForest anomaly scores with a robust fallback."""
    data = frame.copy()
    feature_data = data[FEATURE_COLUMNS].astype(float)
    try:
        from sklearn.ensemble import IsolationForest

        model = IsolationForest(
            n_estimators=150,
            contamination=0.08,
            random_state=config.random_seed,
            n_jobs=1,
        )
        model.fit(feature_data)
        data["model_anomaly_score"] = -model.score_samples(feature_data)
    except ImportError:  # pragma: no cover - fallback for minimal environments
        median = feature_data.median()
        mad = (feature_data - median).abs().median().replace(0, 1)
        robust_distance = ((feature_data - median).abs() / mad).mean(axis=1)
        data["model_anomaly_score"] = np.log1p(robust_distance)
    return data


def detect_anomalies(frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG) -> pd.DataFrame:
    """Run the project anomaly detection stack."""
    return add_model_anomaly_score(
        add_rolling_deviation(
            add_robust_zscore_anomalies(frame, config.zscore_threshold),
            config.rolling_window,
        ),
        config,
    )

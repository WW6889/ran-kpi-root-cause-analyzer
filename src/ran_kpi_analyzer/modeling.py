"""Deterministic ML diagnostics and SHAP-based feature explanations."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import DEFAULT_CONFIG, MODEL_FEATURE_COLUMNS, AnalyzerConfig

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelDiagnostics:
    """Summary metrics for the degradation classifier."""

    model_name: str
    explanation_method: str
    train_samples: int
    test_samples: int
    accuracy: float
    balanced_accuracy: float


def train_degradation_model(
    frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG
) -> tuple[ModelDiagnostics, pd.DataFrame]:
    """Train a small RandomForest and explain degraded-vs-healthy predictions.

    This is deliberately a diagnostic model, not an optimization claim. The
    rule engine remains the primary RCA mechanism; the model provides a
    reproducible sanity check and feature ranking.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, balanced_accuracy_score
        from sklearn.model_selection import train_test_split
    except ImportError as exc:  # pragma: no cover - exercised only in minimal envs
        raise RuntimeError("scikit-learn is required for ML diagnostics") from exc

    features = frame[MODEL_FEATURE_COLUMNS].astype(float)
    target = frame["is_degraded"].astype(int)
    if target.nunique() < 2:
        raise ValueError("Cannot train degradation classifier with a single target class")

    stratify = target if target.value_counts().min() >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        random_state=config.random_seed,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=4,
        random_state=config.random_seed,
        class_weight="balanced",
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    importances, method = _explain_model(model, x_test, config)
    diagnostics = ModelDiagnostics(
        model_name="RandomForestClassifier",
        explanation_method=method,
        train_samples=len(x_train),
        test_samples=len(x_test),
        accuracy=round(float(accuracy_score(y_test, predictions)), 3),
        balanced_accuracy=round(float(balanced_accuracy_score(y_test, predictions)), 3),
    )
    return diagnostics, importances


def _explain_model(
    model: object, samples: pd.DataFrame, config: AnalyzerConfig
) -> tuple[pd.DataFrame, str]:
    """Return mean absolute SHAP values, falling back to RF importances."""
    try:
        import shap

        background = samples.sample(n=min(200, len(samples)), random_state=config.random_seed)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(background)
        values = np.asarray(shap_values)
        if isinstance(shap_values, list):
            values = np.asarray(shap_values[1])
        elif values.ndim == 3:
            values = values[:, :, 1]
        mean_abs = np.abs(values).mean(axis=0)
        method = "mean_abs_shap"
    except Exception as exc:  # pragma: no cover - fallback safety for SHAP env issues
        LOGGER.warning("SHAP explanation failed; using model feature_importances_: %s", exc)
        mean_abs = np.asarray(getattr(model, "feature_importances_"))
        method = "random_forest_feature_importance"

    result = pd.DataFrame(
        {
            "feature": samples.columns,
            "importance": mean_abs,
        }
    )
    total = result["importance"].sum()
    if total > 0:
        result["importance"] = result["importance"] / total
    return result.sort_values("importance", ascending=False).reset_index(drop=True), method

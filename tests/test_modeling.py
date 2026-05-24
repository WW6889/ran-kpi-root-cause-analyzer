from __future__ import annotations

import pandas as pd

from ran_kpi_analyzer.anomaly_detection import detect_anomalies
from ran_kpi_analyzer.modeling import train_degradation_model
from ran_kpi_analyzer.preprocessing import prepare_kpi_data
from ran_kpi_analyzer.root_cause import add_root_cause_labels

from tests.helpers import kpi_row


def test_train_degradation_model_returns_diagnostics_and_importance():
    rows = []
    for idx in range(40):
        rows.append(kpi_row(timestamp=f"2026-01-01 {idx:02d}:00:00", cell_id=f"Cell_{idx:03d}"))
        rows.append(
            kpi_row(
                timestamp=f"2026-01-02 {idx:02d}:00:00",
                cell_id=f"Cell_D_{idx:03d}",
                rsrp_dbm=-112,
                throughput_dl_mbps=18,
                call_drop_rate=0.04,
            )
        )

    analyzed = add_root_cause_labels(detect_anomalies(prepare_kpi_data(pd.DataFrame(rows))))
    diagnostics, importance = train_degradation_model(analyzed)

    assert diagnostics.model_name == "RandomForestClassifier"
    assert diagnostics.test_samples > 0
    assert diagnostics.explanation_method in {
        "mean_abs_shap",
        "random_forest_feature_importance",
    }
    assert not importance.empty
    assert set(importance.columns) == {"feature", "importance"}

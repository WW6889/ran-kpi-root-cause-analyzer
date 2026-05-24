from __future__ import annotations

import pandas as pd
import pytest

from ran_kpi_analyzer.exceptions import DataValidationError
from ran_kpi_analyzer.preprocessing import (
    add_degradation_labels,
    add_engineered_features,
    aggregate_cell_kpis,
    clean_kpi_data,
)

from conftest import kpi_row


def _frame():
    return pd.DataFrame(
        [
            kpi_row(cell_id="Cell_A", rsrp_dbm=-110, throughput_dl_mbps=20, call_drop_rate=0.03),
            kpi_row(cell_id="Cell_B", band="B3", timestamp="2026-01-01 00:15:00"),
        ]
    )


def test_clean_kpi_data_rejects_out_of_range_values():
    data = _frame()
    data.loc[0, "prb_utilization_dl"] = 120
    with pytest.raises(DataValidationError, match="prb_utilization_dl"):
        clean_kpi_data(data)


def test_add_engineered_features_creates_expected_columns():
    engineered = add_engineered_features(clean_kpi_data(_frame()))
    assert "spectral_quality_index" in engineered
    assert "throughput_per_user" in engineered


def test_add_degradation_labels_flags_coverage_case():
    labeled = add_degradation_labels(add_engineered_features(clean_kpi_data(_frame())))
    assert labeled.loc[0, "is_degraded"] == 1
    assert labeled.loc[1, "is_degraded"] == 0


def test_clean_kpi_data_rejects_non_numeric_kpis():
    data = pd.DataFrame([kpi_row(sinr_db="bad")])
    with pytest.raises(DataValidationError, match="Non-numeric"):
        clean_kpi_data(data)


def test_aggregate_cell_kpis_returns_degraded_ratio():
    labeled = add_degradation_labels(add_engineered_features(clean_kpi_data(_frame())))
    summary = aggregate_cell_kpis(labeled)
    assert "degraded_ratio" in summary
    assert set(summary["cell_id"]) == {"Cell_A", "Cell_B"}

import pandas as pd

from ran_kpi_analyzer.preprocessing import (
    add_degradation_labels,
    add_engineered_features,
    aggregate_cell_kpis,
    clean_kpi_data,
)


def _frame():
    return pd.DataFrame(
        [
            {
                "timestamp": "2026-01-01 00:00:00",
                "cell_id": "Cell_A",
                "band": "n78",
                "rsrp_dbm": -110,
                "sinr_db": 10,
                "cqi": 10,
                "prb_utilization_dl": 40,
                "throughput_dl_mbps": 20,
                "latency_ms": 25,
                "packet_loss_rate": 0.01,
                "rrc_setup_success_rate": 98,
                "handover_success_rate": 96,
                "call_drop_rate": 0.03,
                "active_users": 90,
            },
            {
                "timestamp": "2026-01-01 00:15:00",
                "cell_id": "Cell_B",
                "band": "B3",
                "rsrp_dbm": -90,
                "sinr_db": 15,
                "cqi": 11,
                "prb_utilization_dl": 50,
                "throughput_dl_mbps": 80,
                "latency_ms": 20,
                "packet_loss_rate": 0.004,
                "rrc_setup_success_rate": 99,
                "handover_success_rate": 98,
                "call_drop_rate": 0.004,
                "active_users": 70,
            },
        ]
    )


def test_clean_kpi_data_clamps_values():
    data = _frame()
    data.loc[0, "prb_utilization_dl"] = 120
    cleaned = clean_kpi_data(data)
    assert cleaned.loc[0, "prb_utilization_dl"] == 100


def test_add_engineered_features_creates_expected_columns():
    engineered = add_engineered_features(clean_kpi_data(_frame()))
    assert "spectral_quality_index" in engineered
    assert "throughput_per_user" in engineered


def test_add_degradation_labels_flags_coverage_case():
    labeled = add_degradation_labels(add_engineered_features(clean_kpi_data(_frame())))
    assert labeled.loc[0, "is_degraded"] == 1
    assert labeled.loc[1, "is_degraded"] == 0


def test_aggregate_cell_kpis_returns_degraded_ratio():
    labeled = add_degradation_labels(add_engineered_features(clean_kpi_data(_frame())))
    summary = aggregate_cell_kpis(labeled)
    assert "degraded_ratio" in summary
    assert set(summary["cell_id"]) == {"Cell_A", "Cell_B"}


from __future__ import annotations

import pandas as pd

from ran_kpi_analyzer.anomaly_detection import detect_anomalies
from ran_kpi_analyzer.preprocessing import prepare_kpi_data
from tests.helpers import kpi_row


def test_detect_anomalies_adds_expected_outputs():
    rows = []
    for idx in range(12):
        rows.append(
            kpi_row(
                timestamp=f"2026-01-01 {idx:02d}:00:00",
                rsrp_dbm=-92 if idx < 11 else -118,
                sinr_db=14 if idx < 11 else 1,
                cqi=11 if idx < 11 else 3,
                prb_utilization_dl=50 if idx < 11 else 96,
                throughput_dl_mbps=75 if idx < 11 else 8,
                latency_ms=24 if idx < 11 else 90,
                packet_loss_rate=0.005 if idx < 11 else 0.08,
                rrc_setup_success_rate=99 if idx < 11 else 88,
                handover_success_rate=97 if idx < 11 else 82,
                call_drop_rate=0.005 if idx < 11 else 0.08,
                active_users=80 if idx < 11 else 190,
            )
        )
    analyzed = detect_anomalies(prepare_kpi_data(pd.DataFrame(rows)))
    assert {
        "anomaly_score",
        "anomaly_flag",
        "affected_kpi",
        "throughput_deviation",
        "model_anomaly_score",
    }.issubset(analyzed.columns)
    assert analyzed["anomaly_flag"].sum() >= 1

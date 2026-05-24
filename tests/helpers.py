from __future__ import annotations

import pandas as pd


def kpi_row(**updates: object) -> dict[str, object]:
    base: dict[str, object] = {
        "timestamp": pd.Timestamp("2026-01-01 00:00:00"),
        "cell_id": "Cell_A",
        "band": "n78",
        "rsrp_dbm": -90.0,
        "sinr_db": 14.0,
        "cqi": 11.0,
        "prb_utilization_dl": 50.0,
        "throughput_dl_mbps": 75.0,
        "latency_ms": 25.0,
        "packet_loss_rate": 0.005,
        "rrc_setup_success_rate": 99.0,
        "handover_success_rate": 97.0,
        "call_drop_rate": 0.005,
        "active_users": 80,
    }
    base.update(updates)
    return base

"""Synthetic but realistic RAN KPI dataset generation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCENARIOS = {
    "Cell_001": "healthy",
    "Cell_002": "coverage",
    "Cell_003": "interference",
    "Cell_004": "congestion",
    "Cell_005": "mobility",
    "Cell_006": "healthy",
    "Cell_007": "coverage",
    "Cell_008": "interference",
    "Cell_009": "congestion",
    "Cell_010": "mobility",
    "Cell_011": "healthy",
    "Cell_012": "healthy",
}


def _base_sample(rng: np.random.Generator, timestamp, cell_id: str, scenario: str) -> dict:
    hour = timestamp.hour
    busy_hour = 17 <= hour <= 21
    sample = {
        "timestamp": timestamp,
        "cell_id": cell_id,
        "band": rng.choice(["n78", "B3", "B7", "B20"]),
        "rsrp_dbm": rng.normal(-92, 5),
        "sinr_db": rng.normal(15, 3),
        "cqi": rng.normal(11, 1.4),
        "prb_utilization_dl": rng.normal(48 + (18 if busy_hour else 0), 8),
        "throughput_dl_mbps": rng.normal(72 - (12 if busy_hour else 0), 10),
        "latency_ms": rng.normal(24 + (8 if busy_hour else 0), 4),
        "packet_loss_rate": rng.normal(0.006, 0.002),
        "rrc_setup_success_rate": rng.normal(98.5, 0.6),
        "handover_success_rate": rng.normal(97.0, 1.0),
        "call_drop_rate": rng.normal(0.006, 0.002),
        "active_users": rng.normal(88 + (42 if busy_hour else 0), 14),
    }

    degraded_window = timestamp.hour in {8, 9, 18, 19, 20}
    if scenario == "coverage" and degraded_window:
        sample["rsrp_dbm"] = rng.normal(-111, 3)
        sample["throughput_dl_mbps"] = rng.normal(20, 5)
        sample["call_drop_rate"] = rng.normal(0.037, 0.008)
    elif scenario == "interference" and degraded_window:
        sample["sinr_db"] = rng.normal(2.8, 1.1)
        sample["cqi"] = rng.normal(5.2, 0.9)
        sample["throughput_dl_mbps"] = rng.normal(24, 6)
        sample["packet_loss_rate"] = rng.normal(0.027, 0.006)
    elif scenario == "congestion" and busy_hour:
        sample["prb_utilization_dl"] = rng.normal(92, 3)
        sample["active_users"] = rng.normal(172, 16)
        sample["latency_ms"] = rng.normal(58, 9)
        sample["throughput_dl_mbps"] = rng.normal(26, 7)
    elif scenario == "mobility" and degraded_window:
        sample["handover_success_rate"] = rng.normal(84, 3)
        sample["call_drop_rate"] = rng.normal(0.044, 0.009)
        sample["throughput_dl_mbps"] = rng.normal(36, 7)

    return sample


def generate_synthetic_dataset(output_path: str | Path, periods: int = 96, seed: int = 42) -> pd.DataFrame:
    """Generate a multi-cell, 15-minute KPI dataset."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2026-01-05", periods=periods, freq="15min")
    rows = []
    for cell_id, scenario in SCENARIOS.items():
        for timestamp in timestamps:
            rows.append(_base_sample(rng, timestamp, cell_id, scenario))

    frame = pd.DataFrame(rows)
    frame["cqi"] = frame["cqi"].clip(1, 15).round(1)
    frame["prb_utilization_dl"] = frame["prb_utilization_dl"].clip(0, 100).round(2)
    frame["throughput_dl_mbps"] = frame["throughput_dl_mbps"].clip(1, None).round(2)
    frame["latency_ms"] = frame["latency_ms"].clip(1, None).round(2)
    frame["packet_loss_rate"] = frame["packet_loss_rate"].clip(0, 1).round(4)
    frame["rrc_setup_success_rate"] = frame["rrc_setup_success_rate"].clip(0, 100).round(2)
    frame["handover_success_rate"] = frame["handover_success_rate"].clip(0, 100).round(2)
    frame["call_drop_rate"] = frame["call_drop_rate"].clip(0, 1).round(4)
    frame["active_users"] = frame["active_users"].clip(1, None).round().astype(int)
    frame["rsrp_dbm"] = frame["rsrp_dbm"].round(2)
    frame["sinr_db"] = frame["sinr_db"].round(2)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)
    return frame


if __name__ == "__main__":
    generate_synthetic_dataset("data/raw/sample_ran_kpi_data.csv")
    print("Generated data/raw/sample_ran_kpi_data.csv")

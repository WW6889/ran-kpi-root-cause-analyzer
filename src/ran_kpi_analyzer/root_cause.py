"""Rule-based root-cause classification and explainable contributors."""

from __future__ import annotations

from collections import Counter

import pandas as pd

from .config import HIGH_ACTIVE_USERS, HIGH_DROP_RATE, LOW_THROUGHPUT_MBPS


ROOT_CAUSE_ACTIONS = {
    "coverage_limitation": [
        "Validate antenna azimuth, tilt, feeder health, and site power.",
        "Inspect weak coverage boundaries and neighbor cell overlap.",
    ],
    "interference": [
        "Check uplink/downlink interference counters and recent spectrum changes.",
        "Review neighboring cells, external interferers, and PCI planning.",
    ],
    "capacity_congestion": [
        "Verify traffic distribution, scheduler behavior, and busy-hour PRB load.",
        "Inspect load balancing and potential carrier expansion options.",
    ],
    "mobility_degradation": [
        "Review neighbor relations, handover parameters, and recent configuration changes.",
        "Check drive-test traces around failed handover areas.",
    ],
    "healthy_baseline": [
        "Continue periodic KPI monitoring and baseline comparison.",
    ],
}


def classify_row(row: pd.Series) -> str:
    """Classify a single KPI sample using practical RAN engineering rules."""
    if row["rsrp_dbm"] < -105 and row["throughput_dl_mbps"] < LOW_THROUGHPUT_MBPS:
        return "coverage_limitation"
    if row["sinr_db"] < 5 and row["rsrp_dbm"] >= -105 and row["cqi"] < 8:
        return "interference"
    if row["prb_utilization_dl"] > 85 and row["active_users"] > HIGH_ACTIVE_USERS:
        return "capacity_congestion"
    if row["handover_success_rate"] < 90 and row["call_drop_rate"] > HIGH_DROP_RATE:
        return "mobility_degradation"
    return "healthy_baseline"


def add_root_cause_labels(frame: pd.DataFrame) -> pd.DataFrame:
    """Add root-cause labels to every KPI row."""
    data = frame.copy()
    data["root_cause"] = data.apply(classify_row, axis=1)
    return data


def summarize_root_causes(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize dominant root cause per cell."""
    rows = []
    for cell_id, group in frame.groupby("cell_id"):
        causes = Counter(group["root_cause"])
        dominant, count = causes.most_common(1)[0]
        rows.append(
            {
                "cell_id": cell_id,
                "dominant_root_cause": dominant,
                "samples": len(group),
                "degraded_samples": int((group["root_cause"] != "healthy_baseline").sum()),
                "dominant_share": count / len(group),
            }
        )
    return pd.DataFrame(rows).sort_values(["degraded_samples", "dominant_share"], ascending=False)


def rank_kpi_contributors(frame: pd.DataFrame) -> pd.DataFrame:
    """Rank KPI contributors using class-separation from healthy baseline."""
    healthy = frame[frame["root_cause"] == "healthy_baseline"]
    degraded = frame[frame["root_cause"] != "healthy_baseline"]
    if healthy.empty or degraded.empty:
        return pd.DataFrame(columns=["kpi", "importance", "direction"])

    candidates = [
        "rsrp_dbm",
        "sinr_db",
        "cqi",
        "prb_utilization_dl",
        "throughput_dl_mbps",
        "latency_ms",
        "packet_loss_rate",
        "handover_success_rate",
        "call_drop_rate",
        "active_users",
    ]
    rows = []
    for column in candidates:
        spread = frame[column].std(ddof=0) or 1
        delta = degraded[column].mean() - healthy[column].mean()
        rows.append(
            {
                "kpi": column,
                "importance": abs(delta) / spread,
                "direction": "higher" if delta > 0 else "lower",
            }
        )
    return pd.DataFrame(rows).sort_values("importance", ascending=False).reset_index(drop=True)


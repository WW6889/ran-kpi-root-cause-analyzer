"""Evidence-based root-cause classification and KPI contributors."""

from __future__ import annotations

import pandas as pd

from .config import DEFAULT_CONFIG, AnalyzerConfig


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


def score_root_causes(row: pd.Series, config: AnalyzerConfig = DEFAULT_CONFIG) -> dict[str, float]:
    """Score RCA evidence from independent KPI symptoms.

    The output is not a probability. It is a transparent engineering evidence
    score that favors believable symptom combinations over single KPI triggers.
    """
    throughput_per_user = row.get("throughput_per_user", 0.0)
    scores = {
        "coverage_limitation": 0.0,
        "interference": 0.0,
        "capacity_congestion": 0.0,
        "mobility_degradation": 0.0,
    }

    if row["rsrp_dbm"] < config.poor_rsrp_dbm:
        scores["coverage_limitation"] += 0.45
    elif row["rsrp_dbm"] < config.weak_rsrp_dbm:
        scores["coverage_limitation"] += 0.25
    if row["throughput_dl_mbps"] < config.low_throughput_mbps:
        scores["coverage_limitation"] += 0.20
    if row["call_drop_rate"] > config.high_call_drop_rate:
        scores["coverage_limitation"] += 0.10
    if row["sinr_db"] < config.poor_sinr_db:
        scores["coverage_limitation"] += 0.10

    if row["sinr_db"] < config.poor_sinr_db:
        scores["interference"] += 0.40
    if row["rsrp_dbm"] >= config.weak_rsrp_dbm:
        scores["interference"] += 0.20
    if row["cqi"] < config.poor_cqi:
        scores["interference"] += 0.20
    if row["packet_loss_rate"] > config.high_packet_loss_rate:
        scores["interference"] += 0.10
    if row["throughput_dl_mbps"] < config.low_throughput_mbps:
        scores["interference"] += 0.10

    if row["prb_utilization_dl"] > config.high_prb_utilization:
        scores["capacity_congestion"] += 0.35
    if row["active_users"] > config.high_active_users:
        scores["capacity_congestion"] += 0.25
    if row["latency_ms"] > config.high_latency_ms:
        scores["capacity_congestion"] += 0.15
    if throughput_per_user < config.low_throughput_per_user_mbps:
        scores["capacity_congestion"] += 0.15
    if row["throughput_dl_mbps"] < config.low_throughput_mbps:
        scores["capacity_congestion"] += 0.10

    if row["handover_success_rate"] < config.poor_handover_success_rate:
        scores["mobility_degradation"] += 0.45
    if row["call_drop_rate"] > config.high_call_drop_rate:
        scores["mobility_degradation"] += 0.25
    if row["rrc_setup_success_rate"] >= 95:
        scores["mobility_degradation"] += 0.10
    if row["rsrp_dbm"] >= config.poor_rsrp_dbm:
        scores["mobility_degradation"] += 0.10
    if row["throughput_dl_mbps"] < config.low_throughput_mbps:
        scores["mobility_degradation"] += 0.10

    return scores


def classify_row(row: pd.Series, config: AnalyzerConfig = DEFAULT_CONFIG) -> str:
    """Classify a single KPI sample using evidence-based RCA rules."""
    scores = score_root_causes(row, config)
    root_cause, score = max(scores.items(), key=lambda item: item[1])
    if score < 0.50:
        return "healthy_baseline"
    return root_cause


def _evidence_text(row: pd.Series, root_cause: str, config: AnalyzerConfig) -> str:
    evidence = {
        "coverage_limitation": [
            f"RSRP {row['rsrp_dbm']:.1f} dBm",
            f"throughput {row['throughput_dl_mbps']:.1f} Mbps",
        ],
        "interference": [
            f"SINR {row['sinr_db']:.1f} dB",
            f"CQI {row['cqi']:.1f}",
            f"RSRP {row['rsrp_dbm']:.1f} dBm",
        ],
        "capacity_congestion": [
            f"PRB {row['prb_utilization_dl']:.1f}%",
            f"active users {row['active_users']:.0f}",
            f"latency {row['latency_ms']:.1f} ms",
        ],
        "mobility_degradation": [
            f"HOSR {row['handover_success_rate']:.1f}%",
            f"drop rate {row['call_drop_rate']:.3f}",
        ],
        "healthy_baseline": ["No degradation rule exceeded evidence threshold"],
    }
    return "; ".join(evidence[root_cause])


def add_root_cause_labels(
    frame: pd.DataFrame, config: AnalyzerConfig = DEFAULT_CONFIG
) -> pd.DataFrame:
    """Add root-cause labels to every KPI row."""
    data = frame.copy()
    scored = data.apply(lambda row: score_root_causes(row, config), axis=1)
    data["root_cause"] = scored.apply(
        lambda scores: max(scores.items(), key=lambda item: item[1])[0]
    )
    data["root_cause_confidence"] = scored.apply(lambda scores: max(scores.values())).round(3)
    data.loc[data["root_cause_confidence"] < 0.50, "root_cause"] = "healthy_baseline"
    data.loc[data["root_cause"] == "healthy_baseline", "root_cause_confidence"] = 0.0
    data["root_cause_evidence"] = data.apply(
        lambda row: _evidence_text(row, row["root_cause"], config), axis=1
    )
    return data


def summarize_root_causes(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize dominant root cause per cell."""
    rows: list[dict[str, object]] = []
    for cell_id, group in frame.groupby("cell_id"):
        degraded = group[group["root_cause"] != "healthy_baseline"]
        if degraded.empty:
            dominant = "healthy_baseline"
            count = len(group)
            mean_confidence = 0.0
        else:
            dominant = degraded["root_cause"].mode().iat[0]
            count = int((group["root_cause"] == dominant).sum())
            mean_confidence = float(
                degraded.loc[degraded["root_cause"] == dominant, "root_cause_confidence"].mean()
            )
        rows.append(
            {
                "cell_id": cell_id,
                "dominant_root_cause": dominant,
                "samples": len(group),
                "degraded_samples": int((group["root_cause"] != "healthy_baseline").sum()),
                "dominant_share": count / len(group),
                "mean_confidence": round(mean_confidence, 3),
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

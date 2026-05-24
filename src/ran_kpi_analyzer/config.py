"""Project configuration and engineering thresholds.

The threshold values are intentionally explicit and conservative. They are not
vendor acceptance limits; they are diagnostic guardrails for synthetic KPI
scenarios that should remain believable to RAN validation engineers.
"""

from __future__ import annotations

from dataclasses import dataclass

REQUIRED_COLUMNS = [
    "timestamp",
    "cell_id",
    "band",
    "rsrp_dbm",
    "sinr_db",
    "cqi",
    "prb_utilization_dl",
    "throughput_dl_mbps",
    "latency_ms",
    "packet_loss_rate",
    "rrc_setup_success_rate",
    "handover_success_rate",
    "call_drop_rate",
    "active_users",
]

FEATURE_COLUMNS = [
    "rsrp_dbm",
    "sinr_db",
    "cqi",
    "prb_utilization_dl",
    "throughput_dl_mbps",
    "latency_ms",
    "packet_loss_rate",
    "rrc_setup_success_rate",
    "handover_success_rate",
    "call_drop_rate",
    "active_users",
]

ENGINEERED_FEATURE_COLUMNS = [
    "spectral_quality_index",
    "load_pressure_index",
    "service_degradation_index",
    "throughput_per_user",
]

MODEL_FEATURE_COLUMNS = FEATURE_COLUMNS + ENGINEERED_FEATURE_COLUMNS

VALID_BANDS = {"B3", "B7", "B20", "n78"}

KPI_RANGES = {
    "rsrp_dbm": (-140.0, -50.0),
    "sinr_db": (-20.0, 40.0),
    "cqi": (1.0, 15.0),
    "prb_utilization_dl": (0.0, 100.0),
    "throughput_dl_mbps": (0.0, 1000.0),
    "latency_ms": (1.0, 1000.0),
    "packet_loss_rate": (0.0, 1.0),
    "rrc_setup_success_rate": (0.0, 100.0),
    "handover_success_rate": (0.0, 100.0),
    "call_drop_rate": (0.0, 1.0),
    "active_users": (0.0, 10000.0),
}


@dataclass(frozen=True)
class AnalyzerConfig:
    """Thresholds and deterministic runtime controls for the analyzer."""

    weak_rsrp_dbm: float = -105.0
    poor_rsrp_dbm: float = -108.0
    poor_sinr_db: float = 5.0
    poor_cqi: float = 7.0
    high_prb_utilization: float = 85.0
    high_active_users: float = 145.0
    high_latency_ms: float = 45.0
    low_throughput_mbps: float = 28.0
    low_throughput_per_user_mbps: float = 0.25
    poor_handover_success_rate: float = 90.0
    high_call_drop_rate: float = 0.025
    high_packet_loss_rate: float = 0.025
    zscore_threshold: float = 2.8
    rolling_window: int = 6
    random_seed: int = 42


DEFAULT_CONFIG = AnalyzerConfig()

"""Project configuration constants."""

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

LOW_THROUGHPUT_MBPS = 28
HIGH_DROP_RATE = 0.025
HIGH_ACTIVE_USERS = 140


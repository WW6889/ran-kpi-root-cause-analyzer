import pandas as pd

from ran_kpi_analyzer.root_cause import (
    add_root_cause_labels,
    classify_row,
    rank_kpi_contributors,
    summarize_root_causes,
)


def _row(**updates):
    base = {
        "rsrp_dbm": -90,
        "sinr_db": 14,
        "cqi": 11,
        "prb_utilization_dl": 50,
        "throughput_dl_mbps": 75,
        "latency_ms": 25,
        "packet_loss_rate": 0.005,
        "rrc_setup_success_rate": 99,
        "handover_success_rate": 97,
        "call_drop_rate": 0.005,
        "active_users": 80,
    }
    base.update(updates)
    return pd.Series(base)


def test_classify_row_coverage_limitation():
    assert classify_row(_row(rsrp_dbm=-112, throughput_dl_mbps=18)) == "coverage_limitation"


def test_classify_row_interference():
    assert classify_row(_row(sinr_db=2, cqi=5, rsrp_dbm=-92)) == "interference"


def test_classify_row_congestion():
    assert classify_row(_row(prb_utilization_dl=92, active_users=170)) == "capacity_congestion"


def test_classify_row_mobility():
    assert classify_row(_row(handover_success_rate=84, call_drop_rate=0.05)) == "mobility_degradation"


def test_root_cause_summary_and_contributors():
    frame = pd.DataFrame([_row(cell_id="A"), _row(cell_id="A", sinr_db=2, cqi=4), _row(cell_id="B")])
    labeled = add_root_cause_labels(frame)
    summary = summarize_root_causes(labeled)
    contributors = rank_kpi_contributors(labeled)
    assert "dominant_root_cause" in summary
    assert not contributors.empty


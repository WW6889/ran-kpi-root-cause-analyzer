from __future__ import annotations

from ran_kpi_analyzer.synthetic_data import generate_synthetic_dataset


def test_synthetic_dataset_is_deterministic(tmp_path):
    first = generate_synthetic_dataset(tmp_path / "first.csv", periods=8, seed=123)
    second = generate_synthetic_dataset(tmp_path / "second.csv", periods=8, seed=123)

    assert first.equals(second)


def test_synthetic_dataset_contains_all_expected_scenarios(tmp_path):
    data = generate_synthetic_dataset(tmp_path / "sample.csv", periods=96, seed=42)

    assert data["cell_id"].nunique() == 12
    assert (data["rsrp_dbm"] < -108).any()
    assert (data["sinr_db"] < 5).any()
    assert (data["prb_utilization_dl"] > 85).any()
    assert (data["handover_success_rate"] < 90).any()

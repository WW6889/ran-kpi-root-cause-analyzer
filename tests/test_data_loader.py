from __future__ import annotations

import pandas as pd
import pytest

from ran_kpi_analyzer.data_loader import load_kpi_data
from ran_kpi_analyzer.exceptions import DataValidationError

from conftest import kpi_row


def test_load_kpi_data_rejects_missing_required_column(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame([kpi_row()]).drop(columns=["sinr_db"]).to_csv(path, index=False)

    with pytest.raises(DataValidationError, match="Missing required columns"):
        load_kpi_data(path)


def test_load_kpi_data_rejects_duplicate_cell_timestamp(tmp_path):
    path = tmp_path / "duplicate.csv"
    pd.DataFrame([kpi_row(), kpi_row()]).to_csv(path, index=False)

    with pytest.raises(DataValidationError, match="duplicate"):
        load_kpi_data(path)


def test_load_kpi_data_rejects_unsupported_band(tmp_path):
    path = tmp_path / "bad_band.csv"
    pd.DataFrame([kpi_row(band="B99")]).to_csv(path, index=False)

    with pytest.raises(DataValidationError, match="Unsupported band"):
        load_kpi_data(path)

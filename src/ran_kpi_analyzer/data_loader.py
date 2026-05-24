"""CSV loading and schema validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import REQUIRED_COLUMNS, VALID_BANDS
from .exceptions import DataValidationError


def load_kpi_data(path: str | Path) -> pd.DataFrame:
    """Load a RAN KPI CSV file and validate required fields."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    if frame.empty:
        raise DataValidationError("Input file contains no KPI rows")

    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise DataValidationError(f"Missing required columns: {', '.join(missing)}")

    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    if frame["timestamp"].isna().any():
        raise DataValidationError("Column 'timestamp' contains invalid values")

    if frame[REQUIRED_COLUMNS].isna().any().any():
        null_columns = frame[REQUIRED_COLUMNS].columns[frame[REQUIRED_COLUMNS].isna().any()]
        raise DataValidationError(f"Missing values found in: {', '.join(null_columns)}")

    frame["cell_id"] = frame["cell_id"].astype(str).str.strip()
    if (frame["cell_id"] == "").any():
        raise DataValidationError("Column 'cell_id' contains blank values")

    invalid_bands = sorted(set(frame["band"]) - VALID_BANDS)
    if invalid_bands:
        raise DataValidationError(f"Unsupported band values: {', '.join(invalid_bands)}")

    duplicates = frame.duplicated(subset=["timestamp", "cell_id"]).sum()
    if duplicates:
        raise DataValidationError(f"Found {duplicates} duplicate timestamp/cell_id KPI rows")

    return frame.sort_values(["cell_id", "timestamp"]).reset_index(drop=True)

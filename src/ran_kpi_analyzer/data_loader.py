"""CSV loading and schema validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import REQUIRED_COLUMNS


class DataValidationError(ValueError):
    """Raised when input KPI data does not match the expected schema."""


def load_kpi_data(path: str | Path) -> pd.DataFrame:
    """Load a RAN KPI CSV file and validate required fields."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    frame = pd.read_csv(csv_path)
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

    return frame.sort_values(["cell_id", "timestamp"]).reset_index(drop=True)


from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_spreadsheet(file_path: Path) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    if suffix == ".xlsx":
        return pd.read_excel(file_path, dtype=object)
    if suffix == ".csv":
        return pd.read_csv(file_path, dtype=object)
    raise ValueError(f"Unsupported file format: {file_path.suffix}")

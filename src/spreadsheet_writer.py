from __future__ import annotations

from pathlib import Path

import pandas as pd

from config import AppConfig


def ensure_output_columns(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    if config.product_id_column not in df.columns:
        df[config.product_id_column] = ""
    if config.output_url_column not in df.columns:
        df[config.output_url_column] = ""
    return df


def validate_output_path(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"Output file already exists and will not be overwritten: {output_path}")

    probe_path = output_path.with_name(f".{output_path.stem}.write_test.tmp")
    try:
        probe_path.write_text("write-check", encoding="utf-8")
    except OSError as exc:
        raise PermissionError(f"Output folder is not writable: {output_path.parent}") from exc
    finally:
        if probe_path.exists():
            probe_path.unlink()


def write_updated_spreadsheet(df: pd.DataFrame, output_path: Path) -> None:
    validate_output_path(output_path)
    df.to_excel(output_path, index=False, engine="openpyxl")

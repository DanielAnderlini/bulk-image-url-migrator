from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from config import AppConfig
from file_manager import SUPPORTED_EXTENSIONS


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_file_path(file_path: Path) -> ValidationResult:
    errors: list[str] = []
    if not file_path.exists():
        errors.append(f"File does not exist: {file_path}")
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        errors.append(f"Unsupported file format: {file_path.suffix}")
    return ValidationResult(is_valid=not errors, errors=errors)


def validate_dataframe(df: pd.DataFrame, config: AppConfig) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if df.empty:
        errors.append("Spreadsheet is empty.")

    if config.image_url_column not in df.columns:
        errors.append(f"Missing required column: {config.image_url_column}")

    missing_recommended = [column for column in config.recommended_columns if column not in df.columns]
    if missing_recommended:
        warnings.append(f"Missing recommended columns: {', '.join(missing_recommended)}")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)

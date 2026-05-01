from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from config import AppConfig


SUPPORTED_EXTENSIONS = {".xlsx", ".csv"}


def timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_input_files(config: AppConfig) -> list[Path]:
    files: list[Path] = []
    for pattern in config.input_file_patterns:
        files.extend(config.input_folder.glob(pattern))

    unique_files = sorted({path.resolve() for path in files})
    return [
        path
        for path in unique_files
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not path.name.startswith("~$")
        and not path.name.startswith(".")
    ]


def build_timestamped_path(folder: Path, source_file: Path, label: str, timestamp: str) -> Path:
    candidate = folder / f"{source_file.stem}_{label}_{timestamp}{source_file.suffix}"
    counter = 1
    while candidate.exists():
        candidate = folder / f"{source_file.stem}_{label}_{timestamp}_{counter}{source_file.suffix}"
        counter += 1
    return candidate


def move_processed_file(source_file: Path, config: AppConfig, timestamp: str) -> Path:
    destination = build_timestamped_path(config.processed_folder, source_file, "PROCESSED", timestamp)
    return Path(shutil.move(str(source_file), str(destination)))


def move_failed_file(source_file: Path, config: AppConfig, timestamp: str) -> Path:
    destination = build_timestamped_path(config.failed_folder, source_file, "FAILED", timestamp)
    return Path(shutil.move(str(source_file), str(destination)))


def output_file_path(source_file: Path, config: AppConfig, timestamp: str) -> Path:
    return config.output_folder / f"{source_file.stem}_updated_{timestamp}.xlsx"


def log_file_path(source_file: Path, config: AppConfig, timestamp: str) -> Path:
    return config.output_folder / f"{source_file.stem}_process_log_{timestamp}.csv"

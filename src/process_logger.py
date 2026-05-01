from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass
class ProcessLogEntry:
    file_name: str
    execution_batch_id: str
    row_number: int
    product_description: str
    GeneratedProductID: str
    original_url: str
    download_status: str
    detected_format: str
    local_file: str
    upload_status: str
    public_url: str
    error_message: str
    processed_at: str


class ProcessLogger:
    def __init__(self) -> None:
        self._entries: list[ProcessLogEntry] = []

    def add(self, entry: ProcessLogEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> list[ProcessLogEntry]:
        return self._entries

    def write_csv(self, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            raise FileExistsError(f"Process log already exists and will not be overwritten: {output_path}")

        columns = [
            "file_name",
            "execution_batch_id",
            "row_number",
            "product_description",
            "GeneratedProductID",
            "original_url",
            "download_status",
            "detected_format",
            "local_file",
            "upload_status",
            "public_url",
            "error_message",
            "processed_at",
        ]
        rows = [asdict(entry) for entry in self._entries]
        pd.DataFrame(rows, columns=columns).to_csv(output_path, index=False, encoding="utf-8-sig")

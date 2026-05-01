from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from uuid import uuid4

import pandas as pd

from config import AppConfig, load_config
from file_manager import (
    find_input_files,
    log_file_path,
    move_failed_file,
    move_processed_file,
    output_file_path,
    timestamp_for_filename,
)
from image_detector import detect_image_format
from image_downloader import download_image
from image_uploader import configure_cloudinary, upload_image
from input_validator import validate_dataframe, validate_file_path
from process_logger import ProcessLogger, ProcessLogEntry
from product_id_generator import generate_product_id
from spreadsheet_reader import read_spreadsheet
from spreadsheet_writer import ensure_output_columns, validate_output_path, write_updated_spreadsheet


SUCCESS = "SUCCESS"
FAILED = "FAILED"
SKIPPED = "SKIPPED"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def generate_execution_batch_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = uuid4().hex[:6].upper()
    return f"BATCH_{timestamp}_{suffix}"


def format_duration(started_at: datetime, finished_at: datetime) -> str:
    total_seconds = int((finished_at - started_at).total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def clean_cell(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def save_downloaded_image(content: bytes, product_id: str, extension: str, config: AppConfig) -> Path:
    local_file = config.download_folder / f"{product_id}.{extension}"
    config.download_folder.mkdir(parents=True, exist_ok=True)
    local_file.write_bytes(content)
    return local_file


def build_log_entry(
    file_name: str,
    execution_batch_id: str,
    row_number: int,
    product_description: str,
    product_id: str,
    original_url: str,
    download_status: str = SKIPPED,
    detected_format: str = "",
    local_file: str = "",
    upload_status: str = SKIPPED,
    public_url: str = "",
    error_message: str = "",
) -> ProcessLogEntry:
    return ProcessLogEntry(
        file_name=file_name,
        execution_batch_id=execution_batch_id,
        row_number=row_number,
        product_description=product_description,
        GeneratedProductID=product_id,
        original_url=original_url,
        download_status=download_status,
        detected_format=detected_format,
        local_file=local_file,
        upload_status=upload_status,
        public_url=public_url,
        error_message=error_message,
        processed_at=now_iso(),
    )


@dataclass
class ExecutionSummary:
    files_processed: int = 0
    files_failed: int = 0
    rows_success: int = 0
    rows_failed: int = 0
    rows_skipped: int = 0
    images_downloaded: int = 0
    images_uploaded: int = 0

    def add_log_entries(self, entries: list[ProcessLogEntry]) -> None:
        for entry in entries:
            if entry.download_status == SUCCESS:
                self.images_downloaded += 1
            if entry.upload_status == SUCCESS:
                self.images_uploaded += 1

            if entry.download_status == SUCCESS and entry.upload_status == SUCCESS and not entry.error_message:
                self.rows_success += 1
            elif entry.download_status == SKIPPED and entry.upload_status == SKIPPED:
                self.rows_skipped += 1
            else:
                self.rows_failed += 1


@dataclass(frozen=True)
class FileProcessResult:
    processed: bool
    logger: ProcessLogger | None = None


def process_row(
    index: int,
    row: pd.Series,
    df: pd.DataFrame,
    file_name: str,
    execution_batch_id: str,
    config: AppConfig,
    logger: ProcessLogger,
) -> None:
    spreadsheet_row_number = index + 2
    original_url = clean_cell(row.get(config.image_url_column, ""))
    product_description = clean_cell(row.get("Long Description", ""))
    product_id = clean_cell(row.get(config.product_id_column, "")) or generate_product_id(
        row_number=spreadsheet_row_number,
        original_url=original_url,
    )

    df.at[index, config.product_id_column] = product_id

    if not original_url:
        logger.add(
            build_log_entry(
                file_name=file_name,
                execution_batch_id=execution_batch_id,
                row_number=spreadsheet_row_number,
                product_description=product_description,
                product_id=product_id,
                original_url=original_url,
                error_message="ImageURL is empty.",
            )
        )
        return

    detected_format = ""
    local_file = ""
    public_url = ""
    download_status = SKIPPED
    upload_status = SKIPPED
    phase = "download"

    try:
        download = download_image(
            original_url,
            timeout_seconds=config.request_timeout_seconds,
            retry_count=config.download_retry_count,
            retry_delay_seconds=config.download_retry_delay_seconds,
        )
        download_status = SUCCESS
        phase = "detect"
        detection = detect_image_format(download.content, config.supported_image_formats)
        detected_format = detection.extension
        saved_file = save_downloaded_image(download.content, product_id, detection.extension, config)
        local_file = str(saved_file)

        phase = "upload"
        public_url = upload_image(saved_file, product_id, config)
        upload_status = SUCCESS
        df.at[index, config.output_url_column] = public_url
        if config.replace_original_image_url:
            df.at[index, config.image_url_column] = public_url

        logger.add(
            build_log_entry(
                file_name=file_name,
                execution_batch_id=execution_batch_id,
                row_number=spreadsheet_row_number,
                product_description=product_description,
                product_id=product_id,
                original_url=original_url,
                download_status=download_status,
                detected_format=detected_format,
                local_file=local_file,
                upload_status=upload_status,
                public_url=public_url,
            )
        )
    except Exception as exc:
        if phase == "download":
            download_status = FAILED
            upload_status = SKIPPED
        elif phase == "upload":
            upload_status = FAILED

        logger.add(
            build_log_entry(
                file_name=file_name,
                execution_batch_id=execution_batch_id,
                row_number=spreadsheet_row_number,
                product_description=product_description,
                product_id=product_id,
                original_url=original_url,
                download_status=download_status,
                detected_format=detected_format,
                local_file=local_file,
                upload_status=upload_status,
                public_url=public_url,
                error_message=str(exc),
            )
        )
        print(f"    Row {spreadsheet_row_number}: FAILED - {exc}")
        if config.stop_on_first_error:
            raise


def fail_file(file_path: Path, config: AppConfig, timestamp: str, errors: list[str]) -> None:
    moved_path = move_failed_file(file_path, config, timestamp)
    print("  FILE FAILED")
    print(f"  Why: Critical validation or output error.")
    print(f"  What failed: {'; '.join(errors)}")
    print(f"  Moved to: {moved_path}")


def process_file(file_path: Path, config: AppConfig, execution_batch_id: str) -> FileProcessResult:
    timestamp = timestamp_for_filename()
    print(f"\nProcessing: {file_path.name}")

    path_validation = validate_file_path(file_path)
    if not path_validation.is_valid:
        fail_file(file_path, config, timestamp, path_validation.errors)
        return FileProcessResult(processed=False)

    try:
        df = read_spreadsheet(file_path)
    except Exception as exc:
        fail_file(file_path, config, timestamp, [f"File cannot be opened: {exc}"])
        return FileProcessResult(processed=False)

    validation = validate_dataframe(df, config)
    for warning in validation.warnings:
        print(f"  Warning: {warning}")

    if not validation.is_valid:
        fail_file(file_path, config, timestamp, validation.errors)
        return FileProcessResult(processed=False)

    df = ensure_output_columns(df, config)
    logger = ProcessLogger()

    for index, row in df.iterrows():
        print(f"  Row {index + 2}: processing")
        try:
            process_row(
                index=index,
                row=row,
                df=df,
                file_name=file_path.name,
                execution_batch_id=execution_batch_id,
                config=config,
                logger=logger,
            )
        except Exception as exc:
            print(f"  Stopped early because STOP_ON_FIRST_ERROR=true: {exc}")
            break

    output_path = output_file_path(file_path, config, timestamp)
    log_path = log_file_path(file_path, config, timestamp)

    try:
        validate_output_path(output_path)
        validate_output_path(log_path)
        write_updated_spreadsheet(df, output_path)
        logger.write_csv(log_path)
    except Exception as exc:
        fail_file(file_path, config, timestamp, [f"Cannot write output file: {exc}"])
        return FileProcessResult(processed=False, logger=logger)

    print(f"  Updated spreadsheet: {output_path}")
    print(f"  Process log: {log_path}")

    if config.mark_input_as_processed:
        moved_path = move_processed_file(file_path, config, timestamp)
        print(f"  Moved to processed: {moved_path}")

    return FileProcessResult(processed=True, logger=logger)


def warn_if_cloudinary_missing(config: AppConfig) -> None:
    if all([config.cloudinary_cloud_name, config.cloudinary_api_key, config.cloudinary_api_secret]):
        return

    print("\nCloudinary credentials not configured.")
    print("Uploads will fail but local processing and logging will continue.")


def print_execution_summary(summary: ExecutionSummary, started_at: datetime, finished_at: datetime) -> None:
    print("\nEXECUTION SUMMARY")
    print(f"FILES PROCESSED: {summary.files_processed}")
    print(f"FILES FAILED: {summary.files_failed}")
    print("")
    print(f"ROWS SUCCESS: {summary.rows_success}")
    print(f"ROWS FAILED: {summary.rows_failed}")
    print(f"ROWS SKIPPED: {summary.rows_skipped}")
    print("")
    print(f"TOTAL IMAGES DOWNLOADED: {summary.images_downloaded}")
    print(f"TOTAL IMAGES UPLOADED: {summary.images_uploaded}")
    print("")
    print(f"TOTAL EXECUTION TIME: {format_duration(started_at, finished_at)}")


def main() -> int:
    started_at = datetime.now()
    execution_batch_id = generate_execution_batch_id()
    summary = ExecutionSummary()

    config = load_config()
    configure_cloudinary(config)
    warn_if_cloudinary_missing(config)

    input_files = find_input_files(config)
    if not input_files:
        print(f"No .xlsx or .csv files found in {config.input_folder}")
        print_execution_summary(summary, started_at, datetime.now())
        return 0

    print(f"Execution batch: {execution_batch_id}")
    print(f"Found {len(input_files)} input file(s).")
    for file_path in input_files:
        try:
            result = process_file(file_path, config, execution_batch_id)
            if result.processed:
                summary.files_processed += 1
            else:
                summary.files_failed += 1
            if result.logger:
                summary.add_log_entries(result.logger.entries)
        except Exception as exc:
            summary.files_failed += 1
            print(f"Unexpected error while processing {file_path.name}: {exc}")

    print_execution_summary(summary, started_at, datetime.now())
    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

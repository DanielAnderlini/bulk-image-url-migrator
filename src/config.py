from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os


def _parse_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    input_folder: Path
    processed_folder: Path
    failed_folder: Path
    output_folder: Path
    download_folder: Path
    input_file_patterns: list[str]
    image_url_column: str
    product_id_column: str
    output_url_column: str
    recommended_columns: list[str]
    request_timeout_seconds: int
    download_retry_count: int
    download_retry_delay_seconds: float
    supported_image_formats: set[str]
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str
    cloudinary_folder: str
    replace_original_image_url: bool
    mark_input_as_processed: bool
    stop_on_first_error: bool


def load_config() -> AppConfig:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    def folder(name: str, default: str) -> Path:
        raw_value = os.getenv(name, default)
        path = Path(raw_value)
        if not path.is_absolute():
            path = project_root / path
        return path

    config = AppConfig(
        project_root=project_root,
        input_folder=folder("INPUT_FOLDER", "input"),
        processed_folder=folder("PROCESSED_FOLDER", "processed"),
        failed_folder=folder("FAILED_FOLDER", "failed"),
        output_folder=folder("OUTPUT_FOLDER", "output"),
        download_folder=folder("DOWNLOAD_FOLDER", "output/downloaded_images"),
        input_file_patterns=_parse_list(os.getenv("INPUT_FILE_PATTERN", "*.xlsx,*.csv")),
        image_url_column=os.getenv("IMAGE_URL_COLUMN", "ImageURL"),
        product_id_column=os.getenv("PRODUCT_ID_COLUMN", "GeneratedProductID"),
        output_url_column=os.getenv("OUTPUT_URL_COLUMN", "PublicImageURL"),
        recommended_columns=_parse_list(
            os.getenv(
                "RECOMMENDED_COLUMNS",
                "Long Description,Product Categories,Item Sub category,Base Unit of Measure",
            )
        ),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        download_retry_count=int(os.getenv("DOWNLOAD_RETRY_COUNT", "3")),
        download_retry_delay_seconds=float(os.getenv("DOWNLOAD_RETRY_DELAY_SECONDS", "2")),
        supported_image_formats={fmt.lower() for fmt in _parse_list(os.getenv("SUPPORTED_IMAGE_FORMATS", "jpg,jpeg,png,webp,gif"))},
        cloudinary_cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        cloudinary_api_key=os.getenv("CLOUDINARY_API_KEY", ""),
        cloudinary_api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
        cloudinary_folder=os.getenv("CLOUDINARY_FOLDER", "upwork-demo-products"),
        replace_original_image_url=_parse_bool(os.getenv("REPLACE_ORIGINAL_IMAGE_URL", "false")),
        mark_input_as_processed=_parse_bool(os.getenv("MARK_INPUT_AS_PROCESSED", "true"), default=True),
        stop_on_first_error=_parse_bool(os.getenv("STOP_ON_FIRST_ERROR", "false")),
    )

    create_required_folders(config)
    return config


def create_required_folders(config: AppConfig) -> None:
    for folder_path in (
        config.input_folder,
        config.processed_folder,
        config.failed_folder,
        config.output_folder,
        config.download_folder,
    ):
        folder_path.mkdir(parents=True, exist_ok=True)

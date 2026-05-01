from __future__ import annotations

from pathlib import Path

from config import AppConfig


def configure_cloudinary(config: AppConfig) -> None:
    try:
        import cloudinary
    except ImportError:
        return

    cloudinary.config(
        cloud_name=config.cloudinary_cloud_name,
        api_key=config.cloudinary_api_key,
        api_secret=config.cloudinary_api_secret,
        secure=True,
    )


def upload_image(local_file: Path, product_id: str, config: AppConfig) -> str:
    try:
        import cloudinary.uploader
    except ImportError as exc:
        raise RuntimeError(
            "Cloudinary package is not installed. Run: pip install -r requirements.txt"
        ) from exc

    if not all([
        config.cloudinary_cloud_name,
        config.cloudinary_api_key,
        config.cloudinary_api_secret
    ]):
        raise RuntimeError(
            "Cloudinary credentials are missing. Check CLOUDINARY_* values in .env."
        )

    try:
        result = cloudinary.uploader.upload(
            str(local_file),
            public_id=product_id,
            folder=config.cloudinary_folder,
            overwrite=True,
            resource_type="auto",
        )
    except Exception as exc:
        raise RuntimeError(
            f"Cloudinary upload failed: {exc}"
        ) from exc

    secure_url = result.get("secure_url")

    if not secure_url:
        raise RuntimeError(
            "Cloudinary upload response did not include secure_url."
        )

    return str(secure_url)

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


FORMAT_TO_EXTENSION = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
    "GIF": "gif",
}


@dataclass(frozen=True)
class ImageDetectionResult:
    extension: str
    pillow_format: str


def detect_image_format(content: bytes, supported_formats: set[str]) -> ImageDetectionResult:
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
            pillow_format = image.format or ""
    except UnidentifiedImageError as exc:
        raise ValueError("Downloaded content is not a valid image.") from exc
    except Exception as exc:
        raise ValueError(f"Image validation failed: {exc}") from exc

    extension = FORMAT_TO_EXTENSION.get(pillow_format.upper())
    if not extension:
        raise ValueError(f"Unsupported image format detected: {pillow_format or 'unknown'}")

    normalized_supported = {"jpg" if item == "jpeg" else item for item in supported_formats}
    if extension not in normalized_supported:
        raise ValueError(f"Image format is not allowed by configuration: {extension}")

    return ImageDetectionResult(extension=extension, pillow_format=pillow_format.upper())

from __future__ import annotations

from dataclasses import dataclass
import time
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class DownloadResult:
    content: bytes
    content_type: str


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _is_temporary_http_status(status_code: int) -> bool:
    return status_code in {408, 425, 429, 500, 502, 503, 504}


def _should_retry_exception(exc: requests.RequestException) -> bool:
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True

    response = getattr(exc, "response", None)
    return response is not None and _is_temporary_http_status(response.status_code)


def download_image(
    url: str,
    timeout_seconds: int,
    retry_count: int = 3,
    retry_delay_seconds: float = 2,
) -> DownloadResult:
    if not is_valid_url(url):
        raise ValueError("Invalid URL. Expected an absolute http or https URL.")

    max_attempts = max(1, retry_count + 1)
    last_error: requests.RequestException | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=timeout_seconds, allow_redirects=True)
            response.raise_for_status()
            break
        except requests.HTTPError as exc:
            if not _should_retry_exception(exc) or attempt == max_attempts:
                raise RuntimeError(f"Download failed: {exc}") from exc
            last_error = exc
        except requests.RequestException as exc:
            if not _should_retry_exception(exc) or attempt == max_attempts:
                raise RuntimeError(f"Download failed: {exc}") from exc
            last_error = exc

        time.sleep(max(0, retry_delay_seconds))
    else:
        raise RuntimeError(f"Download failed after {max_attempts} attempts: {last_error}")

    if not response.content:
        raise RuntimeError("Download failed: response body was empty.")

    return DownloadResult(
        content=response.content,
        content_type=response.headers.get("Content-Type", ""),
    )

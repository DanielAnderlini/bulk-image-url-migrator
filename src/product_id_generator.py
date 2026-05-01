from __future__ import annotations

import hashlib
from datetime import datetime
from uuid import uuid4


def _url_hash(url: str) -> str:
    if not url:
        return "NOURL"
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:6].upper()


def generate_product_id(row_number: int | None = None, original_url: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    uuid_part = uuid4().hex[:8].upper()
    if row_number is None:
        return f"IMG_{timestamp}_{uuid_part}"
    return f"IMG_{timestamp}_R{row_number}_{_url_hash(original_url)}_{uuid_part}"

"""Download, license-check, and resize images."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from common import SESSION, get, slugify

MAX_WIDTH = 1200
SKIP_LICENSE_HINTS = (
    "all rights reserved",
    "fair use",
    "trademark",
    "unlicensed",
)


def resize_bytes(data: bytes, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(BytesIO(data))
    im = im.convert("RGB") if im.mode not in ("RGB", "L") else im
    w, h = im.size
    if w > MAX_WIDTH:
        h = int(h * MAX_WIDTH / w)
        im = im.resize((MAX_WIDTH, h), Image.Resampling.LANCZOS)
    dest = dest.with_suffix(".jpg")
    im.save(dest, "JPEG", quality=80, optimize=True)
    return dest


def license_ok(text: str | None) -> bool:
    if not text:
        return True
    low = text.lower()
    if any(s in low for s in SKIP_LICENSE_HINTS):
        return False
    return True


def save_image(url: str, dest_dir: Path, stem: str) -> Path | None:
    try:
        r = get(url, timeout=90)
    except Exception:
        return None
    ctype = r.headers.get("Content-Type", "")
    if "svg" in ctype or url.lower().endswith(".svg"):
        return None
    dest = dest_dir / f"{slugify(stem)}.jpg"
    try:
        return resize_bytes(r.content, dest)
    except Exception:
        return None


def write_manifest(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

#!/usr/bin/env python3
"""Re-download book images from images.json manifests (not stored in git)."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT, get
from images import fetch_bytes, looks_like_image, looks_like_jpeg, resize_bytes, save_jpeg_bytes

BOOKS = ROOT / "books"
DEFAULT_ORIGINS = (
    "https://guaka.github.io/books",
    "https://books.hitchwiki.org",
)
_live_origin: list[str | None] = []


def pages_origins() -> list[str]:
    out: list[str] = []
    extra = os.environ.get("PAGES_ORIGIN", "")
    for part in extra.replace(",", " ").split():
        origin = part.strip().rstrip("/")
        if origin and origin not in out:
            out.append(origin)
    for default in DEFAULT_ORIGINS:
        if default not in out:
            out.append(default)
    return out


def live_origin() -> str | None:
    if _live_origin:
        return _live_origin[0]
    found = None
    for origin in pages_origins():
        try:
            get(f"{origin}/", timeout=15, retries=1)
            found = origin
            break
        except Exception:
            continue
    _live_origin.append(found)
    return found


def try_pages(slug: str, name: str) -> bytes | None:
    origin = live_origin()
    if not origin:
        return None
    url = f"{origin}/{slug}/images/{name}"
    try:
        r = get(url, timeout=20, retries=1)
    except Exception:
        return None
    if r.content and looks_like_image(r.content):
        return r.content
    return None


def restore_book(book: Path) -> tuple[int, int, int, int]:
    manifest = book / "images" / "images.json"
    if not manifest.exists():
        return 0, 0, 0, 0
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    dest = book / "images"
    cached = pages = wiki = skipped = 0
    for entry in entries:
        name = entry.get("file")
        url = entry.get("source")
        if not name or not url:
            skipped += 1
            continue
        path = dest / name
        if path.exists() and path.stat().st_size > 0:
            cached += 1
            continue
        try:
            data = try_pages(book.name, name)
            if data:
                if looks_like_jpeg(data):
                    save_jpeg_bytes(data, path)
                else:
                    resize_bytes(data, path)
                pages += 1
                continue
            resize_bytes(fetch_bytes(url), path)
            wiki += 1
        except Exception as exc:
            skipped += 1
            print(f"{book.name}: miss {name}: {exc}", file=sys.stderr)
    return cached, pages, wiki, skipped


def main() -> None:
    total = [0, 0, 0, 0]
    for book in sorted(p for p in BOOKS.iterdir() if p.is_dir()):
        cached, pages, wiki, skipped = restore_book(book)
        ok = cached + pages + wiki
        if ok or skipped:
            print(
                f"{book.name}: {ok} ok "
                f"({cached} cache, {pages} pages, {wiki} wiki), {skipped} skipped"
            )
        total[0] += cached
        total[1] += pages
        total[2] += wiki
        total[3] += skipped
    ok = total[0] + total[1] + total[2]
    print(
        f"images: {ok} ok ({total[0]} cache, {total[1]} pages, {total[2]} wiki), "
        f"{total[3]} skipped"
    )


if __name__ == "__main__":
    main()

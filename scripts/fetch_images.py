#!/usr/bin/env python3
"""Re-download book images from images.json manifests (not stored in git)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT
from images import fetch_bytes, resize_bytes

BOOKS = ROOT / "books"


def restore_book(book: Path) -> tuple[int, int]:
    manifest = book / "images" / "images.json"
    if not manifest.exists():
        return 0, 0
    entries = json.loads(manifest.read_text(encoding="utf-8"))
    dest = book / "images"
    ok = skipped = 0
    for entry in entries:
        name = entry.get("file")
        url = entry.get("source")
        if not name or not url:
            skipped += 1
            continue
        path = dest / name
        if path.exists() and path.stat().st_size > 0:
            ok += 1
            continue
        try:
            saved = resize_bytes(fetch_bytes(url), path)
        except Exception as exc:
            saved = None
            print(f"{book.name}: miss {name}: {exc}", file=sys.stderr)
        if saved:
            ok += 1
        else:
            skipped += 1
    return ok, skipped


def main() -> None:
    total_ok = total_skip = 0
    for book in sorted(p for p in BOOKS.iterdir() if p.is_dir()):
        ok, skipped = restore_book(book)
        if ok or skipped:
            print(f"{book.name}: {ok} images, {skipped} skipped")
        total_ok += ok
        total_skip += skipped
    print(f"images: {total_ok} ok, {total_skip} skipped")


if __name__ == "__main__":
    main()

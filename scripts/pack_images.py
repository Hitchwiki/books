#!/usr/bin/env python3
"""Pack resized book JPEGs into cache/book-images.tar.gz for the `images` GitHub Release."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT

BOOKS = ROOT / "books"
ARCHIVE = ROOT / "cache" / "book-images.tar.gz"
RELEASE_TAG = "images"


def jpeg_files() -> list[Path]:
    return sorted(p for p in BOOKS.glob("*/images/*.jpg") if p.is_file() and p.stat().st_size > 0)


def pack(dest: Path = ARCHIVE) -> Path:
    files = jpeg_files()
    if not files:
        raise SystemExit("no JPEGs under books/*/images/ — run make images first")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    with tarfile.open(tmp, "w:gz") as tar:
        for path in files:
            tar.add(path, arcname=str(path.relative_to(ROOT)))
    tmp.replace(dest)
    print(f"packed {len(files)} JPEGs -> {dest} ({dest.stat().st_size} bytes)")
    return dest


def upload(dest: Path) -> None:
    view = subprocess.run(["gh", "release", "view", RELEASE_TAG], capture_output=True)
    if view.returncode != 0:
        subprocess.run(
            [
                "gh",
                "release",
                "create",
                RELEASE_TAG,
                str(dest),
                "--title",
                "Book images",
                "--notes",
                "Resized JPEGs for CI. Manifests stay in git as books/*/images/images.json.",
            ],
            check=True,
        )
        print(f"created release {RELEASE_TAG}")
        return
    subprocess.run(
        ["gh", "release", "upload", RELEASE_TAG, str(dest), "--clobber"],
        check=True,
    )
    print(f"updated release {RELEASE_TAG}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--upload", action="store_true", help="create or update GitHub release `images`")
    args = p.parse_args()
    dest = pack()
    if args.upload:
        upload(dest)


if __name__ == "__main__":
    main()

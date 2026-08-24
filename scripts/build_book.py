#!/usr/bin/env python3
"""Build one book to HTML, EPUB, and PDF with a 0.1-yyyymmdd-hhmm stamp."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def version_stamp(raw: str | None) -> str:
    if raw:
        return raw
    return "0.1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")


def chapter_files(book: Path) -> list[Path]:
    src = book / "src"
    if not src.exists():
        return []
    files = [p for p in src.rglob("*.md") if p.is_file()]
    return sorted(files, key=lambda p: str(p.relative_to(src)))


def run_pandoc(defaults: Path) -> bool:
    try:
        subprocess.run(["pandoc", "-d", str(defaults)], check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"pandoc failed: {exc}", file=sys.stderr)
        return False


def write_defaults(path: Path, spec: dict) -> None:
    path.write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")


def build(slug: str, version: str, formats: list[str], out: Path) -> None:
    book = ROOT / "books" / slug
    meta_path = book / "metadata.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta["version"] = version
    chapters = chapter_files(book)
    if not chapters:
        print(f"{slug}: no chapters, skip")
        return
    work = out / "tmp" / slug
    work.mkdir(parents=True, exist_ok=True)
    meta_out = work / "metadata.yaml"
    meta_out.write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")
    css = ROOT / "assets" / "book.css"
    epub_css = ROOT / "assets" / "epub.css"
    downloads = out / "site" / "downloads"
    html_dir = out / "site" / slug
    downloads.mkdir(parents=True, exist_ok=True)
    html_dir.mkdir(parents=True, exist_ok=True)
    img = book / "images"
    if img.exists():
        dest_img = html_dir / "images"
        if dest_img.exists():
            shutil.rmtree(dest_img)
        shutil.copytree(img, dest_img)
    if css.exists():
        shutil.copy2(css, html_dir / "book.css")
    inputs = [str(c) for c in chapters]
    resource = [str(book), str(book / "src"), str(book / "images"), str(html_dir)]
    base = {
        "from": "markdown",
        "toc": True,
        "toc-depth": 2,
        "metadata-file": str(meta_out),
        "resource-path": resource,
        "input-files": inputs,
    }
    if "html" in formats:
        defaults = work / "html.yaml"
        write_defaults(
            defaults,
            {
                **base,
                "to": "html5",
                "standalone": True,
                "css": [str(html_dir / "book.css")],
                "output-file": str(html_dir / "index.html"),
            },
        )
        run_pandoc(defaults)
        index = html_dir / "index.html"
        if index.exists():
            html = index.read_text(encoding="utf-8")
            banner = (
                f'<header class="book-banner"><p>'
                f'<a href="../">books.hitchwiki.org</a> · {meta.get("title", slug)} · {version}'
                f"</p></header>\n"
            )
            html = html.replace("<body>", "<body>\n" + banner, 1)
            index.write_text(html, encoding="utf-8")
    stem = f"{slug}-{version}"
    if "epub" in formats:
        epub = downloads / f"{stem}.epub"
        spec = {
            **base,
            "to": "epub3",
            "css": [str(epub_css)] if epub_css.exists() else [],
            "output-file": str(epub),
        }
        cover = book / "images" / "cover.jpg"
        if cover.exists():
            spec["epub-cover-image"] = str(cover)
        write_defaults(work / "epub.yaml", spec)
        if run_pandoc(work / "epub.yaml") and epub.exists():
            shutil.copy2(epub, downloads / f"{slug}.epub")
    if "pdf" in formats:
        pdf = downloads / f"{stem}.pdf"
        ok = False
        for engine in ("tectonic", "xelatex", "lualatex", "pdflatex"):
            if not shutil.which(engine):
                continue
            spec = {
                **base,
                "output-file": str(pdf),
                "pdf-engine": engine,
                "variables": {"geometry": "margin=2cm", "documentclass": "book"},
            }
            write_defaults(work / f"pdf-{engine}.yaml", spec)
            if run_pandoc(work / f"pdf-{engine}.yaml"):
                ok = True
                break
        if not ok and shutil.which("weasyprint") and (html_dir / "index.html").exists():
            try:
                subprocess.run(
                    ["weasyprint", str(html_dir / "index.html"), str(pdf)],
                    check=True,
                )
                ok = True
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                print(f"weasyprint failed: {exc}", file=sys.stderr)
        if not ok:
            print(f"{slug}: PDF skipped (no engine)", file=sys.stderr)
        elif pdf.exists():
            shutil.copy2(pdf, downloads / f"{slug}.pdf")
    print(f"{slug} {version} formats={formats} chapters={len(chapters)}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--book", required=True)
    p.add_argument("--version", default="")
    p.add_argument("--formats", default="html,epub,pdf")
    p.add_argument("--out", default="build")
    args = p.parse_args()
    build(args.book, version_stamp(args.version or None), args.formats.split(","), Path(args.out))


if __name__ == "__main__":
    main()

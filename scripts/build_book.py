#!/usr/bin/env python3
"""Build one book to HTML, EPUB, and PDF with a 0.1-yyyymmdd-hhmm stamp."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
from html import escape, unescape
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import github_icon_link, rewrite_html_images, wiki_image_map
from editorial import is_omitted_chapter, is_redirect_chapter
from themes import THEMES, cover_html, fonts_dir, logos_dir, photo_credit_markdown, photos_dir, write_css_files
from titles import geo_src_key
from toc import enhance_html
from ui_strings import ui_strings
from wiki_links import strip_interwiki_html


DRUPAL_SOURCE_DUMPS = {
    "random-roads": ("randomroads-nodes.xml.gz", "https://randomroads.org/"),
    "dumpsterdam": ("dumpsterdam-nodes.xml.gz", "https://dumpsterdam.nl/"),
    "moneyless": ("moneylessorg-nodes.xml.gz", "https://moneyless.org/"),
    "geldloos": ("geldloosnl-nodes.xml.gz", "https://geldloos.nl/"),
    "sin-dinero": ("sindineronet-nodes.xml.gz", "https://sindinero.net/"),
    "shoestring-nomad": ("casarobino-nodes.xml.gz", "https://casarobino.org/"),
}

SOURCE_PARAGRAPH_RE = re.compile(
    r'<p>Source:\s*(?:<a\s+href="(?P<href>[^"]+)"[^>]*>.*?</a>|'
    r'(?P<text>https?://[^<\s]+))\s*</p>',
    re.I | re.S,
)


def compact_drupal_source_links(html_doc: str, slug: str) -> str:
    """Render Drupal source attributions as quiet canonical node links."""
    spec = DRUPAL_SOURCE_DUMPS.get(slug)
    if not spec:
        return html_doc
    dump_name, base = spec
    dump_path = ROOT / "dumps" / "sql" / dump_name
    if not dump_path.exists():
        return html_doc
    aliases: dict[str, tuple[str, str]] = {}
    root = ET.parse(gzip.open(dump_path)).getroot()
    for row in root.findall("row"):
        fields = {f.get("name") or "": f.text or "" for f in row.findall("field")}
        nid = fields.get("nid", "").strip()
        if not nid.isdigit():
            continue
        node_path = f"node/{nid}"
        canonical = base + node_path
        aliases[canonical.rstrip("/")] = (canonical, node_path)
        alias = fields.get("alias", "").strip("/")
        if alias:
            aliases[(base + alias).rstrip("/")] = (canonical, node_path)

    def replace(match: re.Match[str]) -> str:
        source_url = unescape(match.group("href") or match.group("text") or "").rstrip("/")
        target = aliases.get(source_url)
        if not target:
            return match.group(0)
        canonical, node_path = target
        return (
            f'<p class="chapter-source"><a href="{escape(canonical, quote=True)}">'
            f'{node_path}</a></p>'
        )

    return SOURCE_PARAGRAPH_RE.sub(replace, html_doc)


def drupal_source_manifest(book: Path) -> dict[str, dict[str, str]]:
    path = book / "editorial" / "drupal-nodes.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def version_stamp(raw: str | None) -> str:
    if raw:
        return raw
    return "0.1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")


def chapter_files(book: Path, lang: str = "en") -> list[Path]:
    src = book / "src"
    if not src.exists():
        return []
    files = [
        p
        for p in src.rglob("*.md")
        if p.is_file()
        and not is_omitted_chapter(book, p)
        and not is_redirect_chapter(book, p)
    ]
    def sort_key(path: Path) -> tuple:
        rel = path.relative_to(src)
        # Keep front matter first, then the book's primary language, then translations.
        language_rank = 0 if len(rel.parts) == 1 else (1 if rel.parts[0] == lang else 2)
        return (language_rank, geo_src_key(rel))

    fallback = sorted(files, key=sort_key)
    order_path = book / "editorial" / "order.txt"
    if not order_path.exists():
        return fallback
    rank: dict[str, int] = {}
    for line in order_path.read_text(encoding="utf-8").splitlines():
        rel = line.strip()
        if rel and not rel.startswith("#") and rel not in rank:
            rank[rel] = len(rank)
    return sorted(
        fallback,
        key=lambda p: (
            0 if p.relative_to(src).as_posix() in rank else 1,
            rank.get(p.relative_to(src).as_posix(), 0),
            sort_key(p),
        ),
    )


def run_pandoc(defaults: Path) -> bool:
    try:
        subprocess.run(["pandoc", "-d", str(defaults)], check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"pandoc failed: {exc}", file=sys.stderr)
        return False


def write_defaults(path: Path, spec: dict) -> None:
    path.write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")


def epub_theme_css(slug: str) -> str:
    t = THEMES.get(slug) or THEMES["hitchhikers-guide"]
    return (
        f"body {{ font-family: {t['fallback']}; line-height: 1.45; color: {t['fg']}; }}\n"
        f"h1, h2, h3 {{ font-family: {t['fallback']}; page-break-after: avoid; color: {t['accent2']}; }}\n"
        f"a {{ color: {t['accent']}; }}\n"
        "img { max-width: 100%; height: auto; }\n"
        "figcaption { font-size: 0.85em; font-style: italic; }\n"
    )


def copy_theme_assets(slug: str, html_dir: Path) -> Path | None:
    write_css_files()
    theme_css = ROOT / "assets" / "themes" / f"{slug}.css"
    if theme_css.exists():
        shutil.copy2(theme_css, html_dir / "book.css")
    book_js = ROOT / "assets" / "book.js"
    if book_js.exists():
        shutil.copy2(book_js, html_dir / "book.js")
    font_src = fonts_dir()
    if font_src.exists():
        font_dest = html_dir / "fonts"
        font_dest.mkdir(exist_ok=True)
        t = THEMES.get(slug) or {}
        for key in ("display_file", "body_file", "body_bold", "ui_file", "ui_bold"):
            name = t.get(key)
            if name and (font_src / name).exists():
                shutil.copy2(font_src / name, font_dest / name)
    cover = ROOT / "assets" / "covers" / f"{slug}.jpg"
    logo_name = (THEMES.get(slug) or {}).get("logo")
    if logo_name:
        src_logo = logos_dir() / logo_name
        if src_logo.exists():
            dest_logos = html_dir / "logos"
            dest_logos.mkdir(exist_ok=True)
            shutil.copy2(src_logo, dest_logos / logo_name)
    photo = photos_dir() / f"{slug}.jpg"
    if photo.exists():
        dest_covers = html_dir / "covers"
        dest_covers.mkdir(exist_ok=True)
        shutil.copy2(photo, dest_covers / "photo.jpg")
    if cover.exists():
        shutil.copy2(cover, html_dir / "cover.jpg")
        img = html_dir / "images"
        img.mkdir(exist_ok=True)
        shutil.copy2(cover, img / "cover.jpg")
        return cover
    return None


def build(slug: str, version: str, formats: list[str], out: Path) -> None:
    book = ROOT / "books" / slug
    meta_path = book / "metadata.yaml"
    meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta["version"] = version
    lang = str(meta.get("lang", "en"))
    labels = ui_strings(lang)
    chapters = chapter_files(book, lang)
    if not chapters:
        print(f"{slug}: no chapters, skip")
        return
    work = out / "tmp" / slug
    work.mkdir(parents=True, exist_ok=True)
    meta_out = work / "metadata.yaml"
    meta_out.write_text(yaml.safe_dump(meta, allow_unicode=True), encoding="utf-8")
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
    cover_path = copy_theme_assets(slug, html_dir)
    if not (html_dir / "book.css").exists():
        fallback = ROOT / "assets" / "book.css"
        if fallback.exists():
            shutil.copy2(fallback, html_dir / "book.css")
    epub_css = work / "epub.css"
    epub_css.write_text(epub_theme_css(slug), encoding="utf-8")
    inputs = [str(c) for c in chapters]
    credit_md = photo_credit_markdown(slug)
    if credit_md:
        credit_path = work / "cover-photo.md"
        credit_path.write_text(credit_md, encoding="utf-8")
        inputs = [str(credit_path), *inputs]
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
                "toc": False,
                "standalone": True,
                "css": ["book.css"],
                "output-file": str(html_dir / "index.html"),
            },
        )
        run_pandoc(defaults)
        index = html_dir / "index.html"
        if index.exists():
            html = index.read_text(encoding="utf-8")
            title = escape(str(meta.get("title", slug)))
            banner = (
                '<header class="book-banner">'
                '<div class="book-banner-inner">'
                '<div class="book-banner-title">'
                f'<span class="book-banner-book-title">{title}</span>'
                f'<span class="book-banner-version">{version}</span>'
                '</div>'
                f'<nav class="book-banner-actions" aria-label="{labels["book_links"]}">'
                f'<a class="book-banner-contents" href="#TOC">{labels["contents"]}</a>'
                '<div class="book-banner-utility">'
                '<div class="book-banner-project">'
                '<a class="book-banner-site" href="../">Hitchwiki Books</a>'
                f'{github_icon_link(labels["source_on_github"])}'
                '</div>'
                '<div class="book-banner-downloads">'
                f'<a href="../downloads/{slug}.epub">EPUB</a>'
                f'<a href="../downloads/{slug}.pdf">PDF</a>'
                '</div>'
                '</div>'
                '</nav>'
                '</div>'
                '</header>\n'
            )
            cover = cover_html(slug, meta)
            html = html.replace(
                "<body>",
                f'<body class="book book-{slug}">\n{banner}{cover}',
                1,
            )
            html = re.sub(r"(?:\.\./)+images/", "images/", html)
            html = rewrite_html_images(html, wiki_image_map(book / "images"))
            html = strip_interwiki_html(html)
            html = compact_drupal_source_links(html, slug)
            html = enhance_html(
                html,
                chapters,
                book / "src",
                lang,
                drupal_source_manifest(book),
            )
            index.write_text(html, encoding="utf-8")
    stem = f"{slug}-{version}"
    if "epub" in formats:
        epub = downloads / f"{stem}.epub"
        spec = {
            **base,
            "to": "epub3",
            "css": [str(epub_css)],
            "output-file": str(epub),
        }
        if cover_path and cover_path.exists():
            spec["epub-cover-image"] = str(cover_path)
        write_defaults(work / "epub.yaml", spec)
        if run_pandoc(work / "epub.yaml") and epub.exists():
            shutil.copy2(epub, downloads / f"{slug}.epub")
    if "pdf" in formats:
        pdf = downloads / f"{stem}.pdf"
        ok = False
        html_index = html_dir / "index.html"
        if html_index.exists():
            weasy = shutil.which("weasyprint") or str(ROOT / ".venv" / "bin" / "weasyprint")
            cmd = [weasy] if Path(weasy).exists() else [sys.executable, "-m", "weasyprint"]
            try:
                subprocess.run([*cmd, str(html_index), str(pdf)], check=True)
                ok = True
            except (FileNotFoundError, subprocess.CalledProcessError) as exc:
                print(f"weasyprint failed: {exc}", file=sys.stderr)
        if not ok:
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
        if not ok:
            print(f"{slug}: PDF skipped", file=sys.stderr)
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

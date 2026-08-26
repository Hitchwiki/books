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
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    github_icon_link,
    rewrite_html_images,
    unwrap_broken_fragment_links,
    wiki_image_map,
    wiki_history_url,
)
from editorial import is_omitted_chapter, is_redirect_chapter
from themes import THEMES, cover_html, fonts_dir, logos_dir, photo_credit_markdown, photos_dir, write_css_files
from titles import geo_src_key
from toc import enhance_html
from ui_strings import ui_strings
from wiki_contributors import MARKDOWN_SOURCE_RE, normalize_contributor_name
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
BIDI_MARKS = str.maketrans("", "", "\u200e\u200f\u202a\u202b\u202c\u202d\u202e")
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
    has_subsections = False
    for line in order_path.read_text(encoding="utf-8").splitlines():
        rel = line.strip()
        if rel.startswith("[[") and rel.endswith("]]" ):
            has_subsections = True
        if rel and not rel.startswith(("#", "[")) and rel not in rank:
            rank[rel] = len(rank)
    if has_subsections:
        part_order: dict[str, int] = {}
        for path in fallback:
            rel = path.relative_to(src)
            part = rel.parts[0] if len(rel.parts) > 1 else rel.stem
            part_order.setdefault(part, len(part_order))
        return sorted(
            fallback,
            key=lambda p: (
                part_order[(p.relative_to(src).parts[0] if len(p.relative_to(src).parts) > 1 else p.relative_to(src).stem)],
                0 if p.relative_to(src).as_posix() in rank else 1,
                rank.get(p.relative_to(src).as_posix(), 0),
                sort_key(p),
            ),
        )
    return sorted(
        fallback,
        key=lambda p: (
            0 if p.relative_to(src).as_posix() in rank else 1,
            rank.get(p.relative_to(src).as_posix(), 0),
            sort_key(p),
        ),
    )


ATTRIBUTION_LABELS = {
    "en": {
        "title": "Attribution",
        "contributors": "Contributors",
        "sources": "Sources and licence",
        "registered": "The wiki-derived chapters include work by these registered contributors, listed alphabetically:",
        "anonymous": "Anonymous contributors are credited through the revision histories linked in the chapter-source list below.",
        "credited": "This edition credits **{author}**.",
        "source": "This edition was compiled from [{label}]({url}). Source pages and revision histories for imported chapters are listed below.",
        "license": "The book metadata records the content licence as **{license}**.",
        "images": "Photograph and illustration credits appear with their images and are consolidated below.",
        "image_heading": "Image credits",
        "cover_image": "Cover photograph",
        "unknown_creator": "creator not recorded",
        "unknown_license": "licence not recorded",
        "chapter_sources": "Chapter sources",
        "history": "revision history",
    },
    "nl": {
        "title": "Naamsvermelding",
        "contributors": "Bijdragers",
        "sources": "Bronnen en licentie",
        "registered": "De uit wiki's afkomstige hoofdstukken bevatten werk van deze geregistreerde bijdragers, alfabetisch gerangschikt:",
        "anonymous": "Anonieme bijdragers worden vermeld via de revisiegeschiedenissen in de bronnenlijst per hoofdstuk hieronder.",
        "credited": "Deze editie vermeldt **{author}**.",
        "source": "Deze editie is samengesteld uit [{label}]({url}). Bronpagina's en revisiegeschiedenissen van geïmporteerde hoofdstukken staan hieronder.",
        "license": "De metadata van het boek vermeldt **{license}** als inhoudslicentie.",
        "images": "Credits voor foto's en illustraties staan bij de afbeeldingen en zijn hieronder samengebracht.",
        "image_heading": "Beeldcredits",
        "cover_image": "Omslagfoto",
        "unknown_creator": "maker niet vermeld",
        "unknown_license": "licentie niet vermeld",
        "chapter_sources": "Bronnen per hoofdstuk",
        "history": "revisiegeschiedenis",
    },
    "es": {
        "title": "Atribución",
        "contributors": "Colaboradores",
        "sources": "Fuentes y licencia",
        "registered": "Los capítulos procedentes de wikis incluyen el trabajo de estos colaboradores registrados, en orden alfabético:",
        "anonymous": "Las contribuciones anónimas se reconocen mediante los historiales enlazados en la lista de fuentes de los capítulos que figura a continuación.",
        "credited": "Esta edición acredita a **{author}**.",
        "source": "Esta edición se compiló a partir de [{label}]({url}). Las páginas de origen y los historiales de revisión de los capítulos importados se enumeran a continuación.",
        "license": "Los metadatos del libro indican **{license}** como licencia del contenido.",
        "images": "Los créditos de fotografías e ilustraciones aparecen junto a las imágenes y se reúnen a continuación.",
        "image_heading": "Créditos de imágenes",
        "cover_image": "Fotografía de cubierta",
        "unknown_creator": "autoría no registrada",
        "unknown_license": "licencia no registrada",
        "chapter_sources": "Fuentes de los capítulos",
        "history": "historial de revisiones",
    },
}


def markdown_name(name: str) -> str:
    return re.sub(r"([\\`*_[\]<>])", r"\\\1", name)


def alphabetical_key(text: str) -> tuple[str, str]:
    folded = unicodedata.normalize("NFKD", text.casefold())
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    folded = "".join(char for char in folded if char.isalnum())
    return (folded, text)


def image_attribution_markdown(book: Path, labels: dict[str, str]) -> str:
    """Consolidate credits for cover art and locally published book images."""
    credits: list[str] = []
    photo = (THEMES.get(book.name) or {}).get("cover_photo") or {}
    if photo:
        caption = str(photo.get("caption") or labels["cover_image"])
        page = str(photo.get("page") or "")
        linked_caption = (
            f"[{markdown_name(caption)}](<{page}>)" if page else markdown_name(caption)
        )
        author = markdown_name(str(photo.get("author") or labels["unknown_creator"]))
        license_name = markdown_name(
            str(photo.get("license") or labels["unknown_license"])
        )
        credits.append(
            f'- **{labels["cover_image"]}:** {linked_caption} — {author} · {license_name}'
        )

    manifest = book / "images" / "images.json"
    entries = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else []
    seen: set[str] = set()
    for entry in entries:
        filename = str(entry.get("file") or "")
        source = str(entry.get("source") or "")
        if not filename or not source or not (book / "images" / filename).is_file():
            continue
        key = source.casefold()
        if key in seen:
            continue
        seen.add(key)
        source_name = unquote(urlparse(source).path.rsplit("/", 1)[-1]).strip()
        source_name = source_name.translate(BIDI_MARKS).strip() or filename
        author = markdown_name(str(entry.get("author") or labels["unknown_creator"]))
        license_name = markdown_name(
            str(entry.get("license") or labels["unknown_license"])
        )
        credits.append(
            f"- [{markdown_name(source_name)}](<{source}>) — {author} · {license_name}"
        )
    if not credits:
        return ""
    return f'## {labels["image_heading"]}\n\n' + "\n".join(credits) + "\n"


def chapter_source_markdown(chapters: list[Path], labels: dict[str, str]) -> str:
    """Move generated per-chapter source notes into the Attribution chapter."""
    sources: list[tuple[str, str]] = []
    seen: set[str] = set()
    for chapter in chapters:
        text = chapter.read_text(encoding="utf-8")
        for label, url in MARKDOWN_SOURCE_RE.findall(text):
            if url.casefold() in seen:
                continue
            seen.add(url.casefold())
            sources.append((label.strip(), url))
    if not sources:
        return ""
    sources.sort(key=lambda item: (*alphabetical_key(item[0]), item[1]))
    rendered: list[str] = []
    for label, url in sources:
        item = f"[{markdown_name(label)}](<{url}>)"
        if history := wiki_history_url(url):
            item += f' ([{labels["history"]}](<{history}>))'
        rendered.append(item)
    items = " · ".join(rendered)
    return (
        f'## {labels["chapter_sources"]}\n\n'
        f'::: {{.chapter-sources}}\n{items}\n:::\n'
    )


def attribution_markdown(book: Path, meta: dict, chapters: list[Path]) -> str:
    """Build the final attribution section for every title."""
    lang = str(meta.get("lang") or "en").split("-", 1)[0]
    labels = ATTRIBUTION_LABELS.get(lang, ATTRIBUTION_LABELS["en"])
    author = str(meta.get("author") or "respective contributors")
    source = str(meta.get("source") or "")
    license_name = str(meta.get("license") or "")
    manifest_path = book / "editorial" / "wiki-contributors.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {}
    )
    contributors = sorted(
        {
            normalized
            for name in (manifest.get("contributors") or [])
            if (normalized := normalize_contributor_name(str(name)))
        },
        key=lambda name: (name.casefold(), name),
    )

    contributor_text = labels["credited"].format(author=author)
    if contributors:
        names = ", ".join(markdown_name(str(name)) for name in contributors)
        contributor_text = f'{labels["registered"]}\n\n{names}'
        if manifest.get("anonymous_contributors"):
            contributor_text += f'\n\n{labels["anonymous"]}'

    source_text: list[str] = []
    if source:
        label = urlparse(source).hostname or source
        source_text.append(labels["source"].format(label=label, url=source))
    if license_name:
        source_text.append(labels["license"].format(license=license_name))
    source_text.append(labels["images"])
    if any(chapter.stem == "wikihow" for chapter in chapters):
        source_text.append(
            "**WikiHow** is by wikiHow contributors: "
            "[original article](https://www.wikihow.com/Dumpster-Dive), "
            "via [Trashwiki](https://trashwiki.org/en/WikiHow); CC BY-NC-SA 3.0."
        )
    image_credits = image_attribution_markdown(book, labels)
    chapter_sources = chapter_source_markdown(chapters, labels)
    return (
        f'# {labels["title"]}\n\n'
        f'## {labels["contributors"]}\n\n{contributor_text}\n\n'
        f'## {labels["sources"]}\n\n' + "\n\n".join(source_text) + "\n\n"
        + chapter_sources
        + "\n"
        + image_credits
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


def write_image_filter(book: Path, work: Path) -> Path:
    """Map available licensed images locally and discard unresolved image nodes."""
    entries: dict[str, str] = {}
    images = book / "images"
    manifest = images / "images.json"
    if manifest.exists():
        for item in json.loads(manifest.read_text(encoding="utf-8")):
            dest = str(item.get("file") or "")
            target = images / dest
            if not dest or not target.is_file():
                continue
            names = {dest}
            source = str(item.get("source") or "")
            if source:
                raw_name = urlparse(source).path.rsplit("/", 1)[-1]
                names.update({raw_name, unquote(raw_name), quote(unquote(raw_name))})
            for name in names:
                clean = name.translate(BIDI_MARKS).strip()
                if clean:
                    entries[clean] = str(target.resolve())
                    entries[clean.casefold()] = str(target.resolve())

    rows = "\n".join(
        f"  [{json.dumps(name, ensure_ascii=False)}] = {json.dumps(path, ensure_ascii=False)},"
        for name, path in sorted(entries.items())
    )
    path = work / "local-images.lua"
    path.write_text(
        "local images = {\n"
        + rows
        + "\n}\n\n"
        + "function Image(image)\n"
        + "  local src = image.src\n"
        + "  for _, mark in ipairs({'\\226\\128\\142', '\\226\\128\\143', '\\226\\128\\170', '\\226\\128\\171', '\\226\\128\\172', '\\226\\128\\173', '\\226\\128\\174'}) do\n"
        + "    src = src:gsub(mark, '')\n"
        + "  end\n"
        + "  local clean = src:gsub('[?#].*$', '')\n"
        + "  local name = clean:match('([^/\\\\]+)$') or clean\n"
        + "  local target = images[name] or images[string.lower(name)]\n"
        + "  if not target then return {} end\n"
        + "  image.src = target\n"
        + "  return image\n"
        + "end\n\n"
        + "local function discard_raw_image(element)\n"
        + "  if element.format:match('html') then\n"
        + "    local text = string.lower(element.text)\n"
        + "    if text:match('<img[%s>]') or text:match('<references[%s/>]') then\n"
        + "      return {}\n"
        + "    end\n"
        + "  end\n"
        + "end\n\n"
        + "RawInline = discard_raw_image\n"
        + "RawBlock = discard_raw_image\n",
        encoding="utf-8",
    )
    return path


def epub_theme_css(slug: str) -> str:
    t = THEMES.get(slug) or THEMES["hitchhikers-guide"]
    return (
        f"body {{ font-family: {t['fallback']}; line-height: 1.45; color: {t['fg']}; }}\n"
        f"h1, h2, h3 {{ font-family: {t['fallback']}; page-break-after: avoid; color: {t['accent2']}; }}\n"
        f"a {{ color: {t['accent']}; }}\n"
        "img { max-width: 100%; height: auto; }\n"
        "figcaption { font-size: 0.85em; font-style: italic; }\n"
        "#attribution ~ p, #attribution ~ ul, #attribution ~ ol { font-size: 0.9em; line-height: 1.45; }\n"
        "#attribution ~ h2 { font-size: 1.2em; }\n"
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
    edition = version.split("-", 1)[0]
    lang = str(meta.get("lang", "en"))
    labels = ui_strings(lang)
    chapters = chapter_files(book, lang)
    if not chapters:
        print(f"{slug}: no chapters, skip")
        return
    work = out / "tmp" / slug
    work.mkdir(parents=True, exist_ok=True)
    toc_chapters = list(chapters)
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
    attribution_path = work / "99-attribution.md"
    attribution_path.write_text(
        attribution_markdown(book, meta, chapters), encoding="utf-8"
    )
    inputs.append(str(attribution_path))
    toc_chapters.append(attribution_path)
    credit_md = photo_credit_markdown(slug)
    if credit_md:
        credit_path = work / "cover-photo.md"
        credit_path.write_text(credit_md, encoding="utf-8")
        inputs = [str(credit_path), *inputs]
    resource = [str(book), str(book / "src"), str(book / "images"), str(html_dir)]
    image_filter = write_image_filter(book, work)
    base = {
        "from": "markdown",
        "file-scope": True,
        "toc": True,
        "toc-depth": 2,
        "metadata-file": str(meta_out),
        "resource-path": resource,
        "input-files": inputs,
        "filters": [
            str(image_filter),
            str(ROOT / "scripts" / "reader_links.lua"),
            str(ROOT / "scripts" / "remove_chapter_footers.lua"),
        ],
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
                f'<a href="../downloads/{slug}-{edition}.epub">EPUB</a>'
                f'<a href="../downloads/{slug}-{edition}.pdf">PDF</a>'
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
            html = rewrite_html_images(
                html, wiki_image_map(book / "images"), image_root=html_dir
            )
            html = strip_interwiki_html(html)
            html = compact_drupal_source_links(html, slug)
            html = enhance_html(
                html,
                toc_chapters,
                book / "src",
                lang,
                drupal_source_manifest(book),
            )
            html = unwrap_broken_fragment_links(html)
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
            (downloads / f"{slug}.epub").unlink(missing_ok=True)
            shutil.copy2(epub, downloads / f"{slug}-{edition}.epub")
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
            (downloads / f"{slug}.pdf").unlink(missing_ok=True)
            shutil.copy2(pdf, downloads / f"{slug}-{edition}.pdf")
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

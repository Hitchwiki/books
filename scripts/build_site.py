#!/usr/bin/env python3
"""Write the books.hitchwiki.org catalog homepage."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import github_icon_link
from themes import THEMES, fonts_dir, logos_dir

BOOKS = list(THEMES)
LANG_ORDER = ["en", "nl", "es"]
LANG_LABELS = {"en": "English", "nl": "Nederlands", "es": "Español"}


def version_stamp(raw: str | None) -> str:
    if raw:
        return raw
    return "0.1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")


def build_when(version: str) -> dt.datetime:
    parts = version.rsplit("-", 2)
    if len(parts) >= 2:
        date_part, time_part = parts[-2], parts[-1]
        if len(date_part) == 8 and date_part.isdigit() and len(time_part) == 4 and time_part.isdigit():
            return dt.datetime.strptime(date_part + time_part, "%Y%m%d%H%M").replace(
                tzinfo=dt.timezone.utc
            )
    return dt.datetime.now(dt.timezone.utc)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="")
    p.add_argument("--out", default="build/site")
    args = p.parse_args()
    version = version_stamp(args.version or None)
    when = build_when(version)
    built = when.strftime("%Y-%m-%d %H:%M")
    built_iso = when.strftime("%Y-%m-%dT%H:%M:00Z")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    covers_src = ROOT / "assets" / "covers"
    covers_dest = assets / "covers"
    covers_dest.mkdir(exist_ok=True)
    catalog_css = ROOT / "assets" / "catalog.css"
    if catalog_css.exists():
        shutil.copy2(catalog_css, assets / "catalog.css")
    font_dest = assets / "fonts"
    font_dest.mkdir(exist_ok=True)
    if fonts_dir().exists():
        for ttf in fonts_dir().glob("*.ttf"):
            shutil.copy2(ttf, font_dest / ttf.name)
    logos_dest = assets / "logos"
    logos_dest.mkdir(exist_ok=True)

    def card_html(slug: str) -> str:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"title": slug}
        title = meta.get("title", slug)
        license_id = meta.get("license", "")
        kicker = THEMES[slug]["kicker"]
        pdf = out / "downloads" / f"{slug}.pdf"
        epub = f'<a href="./downloads/{slug}.epub">EPUB</a>'
        pdf_link = f' · <a href="./downloads/{slug}.pdf">PDF</a>' if pdf.exists() else ""
        cover = covers_src / f"{slug}.jpg"
        cover_html = ""
        if cover.exists():
            shutil.copy2(cover, covers_dest / f"{slug}.jpg")
            cover_html = f'<a class="cover" href="./{slug}/"><img src="./assets/covers/{slug}.jpg" alt=""></a>'
        logo_name = THEMES[slug].get("logo")
        if logo_name:
            src_logo = logos_dir() / logo_name
            if src_logo.exists():
                shutil.copy2(src_logo, logos_dest / logo_name)
        return f"""<article class="card card-{slug}">
  <a class="open" href="./{slug}/" aria-label="Read {title}"></a>
  {cover_html}
  <div class="card-body">
    <p class="kicker">{kicker}</p>
    <h2><a href="./{slug}/">{title}</a></h2>
    <p class="license"><span class="badge">{license_id}</span></p>
    <p class="formats">
      <a href="./{slug}/">Read</a>
      · {epub}{pdf_link}
    </p>
  </div>
</article>"""

    by_lang: dict[str, list[str]] = {}
    for slug in BOOKS:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        lang = meta.get("lang") or "en"
        by_lang.setdefault(lang, []).append(slug)
    sections = []
    seen = set()
    for lang in [*LANG_ORDER, *by_lang]:
        if lang in seen or lang not in by_lang:
            continue
        seen.add(lang)
        label = LANG_LABELS.get(lang, lang)
        heading = f'    <h2 class="lang-label">{label}</h2>\n' if lang != "en" else ""
        cards = "".join(card_html(slug) for slug in by_lang[lang])
        sections.append(
            f'''  <section class="lang" lang="{lang}">
{heading}    <div class="grid">
    {cards}
    </div>
  </section>'''
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>books.hitchwiki.org</title>
  <link rel="stylesheet" href="./assets/catalog.css">
</head>
<body class="catalog">
  <header>
    <h1>books.hitchwiki.org</h1>
  </header>
{chr(10).join(sections)}
  <p class="lede">A growing collection of freely licensed books. Created by thousands of people over two decades.</p>
  <p class="foot">Content licenses live with each book. {github_icon_link()} Built <time datetime="{built_iso}">{built}</time>.</p>
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"catalog {version} -> {out}")


if __name__ == "__main__":
    main()

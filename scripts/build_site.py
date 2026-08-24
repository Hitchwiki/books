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

from themes import THEMES, fonts_dir, logos_dir

BOOKS = list(THEMES)


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
    cards = []
    for slug in BOOKS:
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
            cover_html = f'<a href="./{slug}/"><img src="./assets/covers/{slug}.jpg" alt=""></a>'
        logo_name = THEMES[slug].get("logo")
        if logo_name:
            src_logo = logos_dir() / logo_name
            if src_logo.exists():
                shutil.copy2(src_logo, logos_dest / logo_name)
        cards.append(
            f"""<article class="card card-{slug}">
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
    <p class="lede">Seven freely licensed books, each with its own type, cover, and license. Compiled from Hitchwiki, Trashwiki, Nomadwiki, Random Roads, Dumpsterdam, Trustroots Wiki, and Moneyless.</p>
  </header>
  <div class="grid">
    {"".join(cards)}
  </div>
  <p class="foot">Scripts MIT. Content licenses live with each book. <a class="github" href="https://github.com/guaka/books" aria-label="Source on GitHub"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/></svg></a> Built <time datetime="{built_iso}">{built}</time>.</p>
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"catalog {version} -> {out}")


if __name__ == "__main__":
    main()

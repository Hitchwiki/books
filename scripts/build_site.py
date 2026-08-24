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

from themes import THEMES, fonts_dir

BOOKS = list(THEMES)


def version_stamp(raw: str | None) -> str:
    if raw:
        return raw
    return "0.1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="")
    p.add_argument("--out", default="build/site")
    args = p.parse_args()
    version = version_stamp(args.version or None)
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
        cards.append(
            f"""<article class="card card-{slug}">
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
    <p class="lede">Seven freely licensed books, each with its own type, cover, and license. Compiled from Hitchwiki, Trashwiki, Nomadwiki, Random Roads, Dumpsterdam, Trustroots Wiki, and Moneyless. Build {version}.</p>
  </header>
  <div class="grid">
    {"".join(cards)}
  </div>
  <p class="foot">Scripts MIT. Content licenses live with each book. <a href="https://github.com/guaka/books">Source</a>.</p>
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"catalog {version} -> {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Write the books.hitchwiki.org catalog homepage."""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BOOKS = [
    "hitchhikers-guide",
    "dumpster-diving",
    "random-roads",
    "dumpsterdam",
    "hospitality-exchange",
    "moneyless",
    "shoestring-nomad",
]


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
    cards = []
    for slug in BOOKS:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"title": slug}
        title = meta.get("title", slug)
        license_id = meta.get("license", "")
        rights = meta.get("rights", "")
        pdf = out / "downloads" / f"{slug}.pdf"
        epub = f'<a href="./downloads/{slug}.epub">EPUB</a>'
        pdf_link = f' · <a href="./downloads/{slug}.pdf">PDF</a>' if pdf.exists() else ""
        cards.append(
            f"""<article class="card">
  <h2><a href="./{slug}/">{title}</a></h2>
  <p class="license"><span class="badge">{license_id}</span> {rights}</p>
  <p>
    <a href="./{slug}/">Read</a>
    · {epub}{pdf_link}
  </p>
</article>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>books.hitchwiki.org</title>
  <link rel="stylesheet" href="./assets/book.css">
  <style>
    .grid {{ display: grid; gap: 1.5rem; }}
    @media (min-width: 720px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
    .badge {{ display: inline-block; border: 1px solid #2c5f4a; padding: 0.1rem 0.4rem; font-size: 0.8rem; }}
    .card {{ border-bottom: 1px solid #ddd; padding-bottom: 1rem; }}
  </style>
</head>
<body>
  <header class="book-banner">
    <h1>books.hitchwiki.org</h1>
    <p>Freely licensed books from Hitchwiki, Trashwiki, Nomadwiki, Random Roads, Dumpsterdam, Trustroots, and Moneyless. Each book has its own license. Build {version}.</p>
  </header>
  <div class="grid">
    {"".join(cards)}
  </div>
  <p class="license">Scripts MIT. Content licenses live with each book. <a href="https://github.com/guaka/books">Source</a>.</p>
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    css = ROOT / "assets" / "book.css"
    if css.exists():
        (assets / "book.css").write_text(css.read_text(encoding="utf-8"), encoding="utf-8")
    (out / "CNAME").write_text("books.hitchwiki.org\n", encoding="utf-8")
    print(f"catalog {version} -> {out}")


if __name__ == "__main__":
    main()

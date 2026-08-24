#!/usr/bin/env python3
"""Compile Drupal node XML dumps into book Markdown."""

from __future__ import annotations

import argparse
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from markdownify import markdownify as html_md

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT, slugify

DUMPS = ROOT / "dumps" / "sql"

SKIP_TYPES = {
    "poll",
    "webform",
    "forum",
    "postcard",
    "book",
    "publicity",
    "publicidad",
    "publiciteit",
    "reclame_horizontaal",
    "embeddable",
    "quotes",
    "photos_gallery",
}

SOURCES = [
    {
        "file": "randomroads-nodes.xml.gz",
        "book": "random-roads",
        "lang": "en",
        "base": "https://randomroads.org/",
        "skip_types": SKIP_TYPES | {"art", "magazine", "link", "video"},
    },
    {
        "file": "dumpsterdam-nodes.xml.gz",
        "book": "dumpsterdam",
        "lang": "auto",
        "base": "https://dumpsterdam.nl/",
        "skip_types": SKIP_TYPES,
    },
    {
        "file": "moneylessorg-nodes.xml.gz",
        "book": "moneyless",
        "lang": "en",
        "base": "https://moneyless.org/",
        "skip_types": SKIP_TYPES,
    },
    {
        "file": "geldloosnl-nodes.xml.gz",
        "book": "moneyless",
        "lang": "nl",
        "base": "https://geldloos.nl/",
        "skip_types": SKIP_TYPES | {"featured", "video"},
    },
    {
        "file": "sindineronet-nodes.xml.gz",
        "book": "moneyless",
        "lang": "es",
        "base": "https://sindinero.net/",
        "skip_types": SKIP_TYPES,
    },
    {
        "file": "casarobino-nodes.xml.gz",
        "book": "shoestring-nomad",
        "lang": "en",
        "subdir": "casa-robino",
        "base": "https://casarobino.org/",
        "skip_types": SKIP_TYPES,
    },
]

NL_HINTS = re.compile(
    r"\b(het|een|van|voor|niet|met|zijn|naar|ook|maar|wel|dit|deze|voedsel|dumpster|missie)\b",
    re.I,
)
EN_HINTS = re.compile(
    r"\b(the|and|with|from|about|this|that|diving|mission|why)\b",
    re.I,
)


def row_dict(row: ET.Element) -> dict[str, str]:
    out = {}
    for field in row.findall("field"):
        out[field.get("name") or ""] = field.text or ""
    return out


def guess_lang(title: str, body: str, default: str) -> str:
    if default != "auto":
        return default
    text = f"{title} {body[:800]}"
    nl = len(NL_HINTS.findall(text))
    en = len(EN_HINTS.findall(text))
    if en > nl + 1:
        return "en"
    return "nl"


def html_to_md(html: str) -> str:
    if not html.strip():
        return ""
    md = html_md(html, heading_style="ATX", strip=["script", "style"])
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def compile_source(cfg: dict) -> int:
    path = DUMPS / cfg["file"]
    if not path.exists():
        print(f"  missing {path}", file=sys.stderr)
        return 0
    root = ET.parse(gzip.open(path)).getroot()
    book = ROOT / "books" / cfg["book"]
    skip = cfg.get("skip_types") or set()
    n = 0
    seen_slugs: set[tuple[str, str]] = set()
    for row in root.findall("row"):
        d = row_dict(row)
        ntype = d.get("type") or ""
        if ntype in skip:
            continue
        title = (d.get("title") or "").strip() or f"node-{d.get('nid')}"
        body = html_to_md(d.get("body") or "")
        if not body:
            continue
        lang = guess_lang(title, body, cfg["lang"])
        sub = cfg.get("subdir") or lang
        dest_dir = book / "src" / sub
        dest_dir.mkdir(parents=True, exist_ok=True)
        slug = slugify(title)
        key = (sub, slug)
        if key in seen_slugs:
            slug = f"{slug}-{d.get('nid')}"
        seen_slugs.add((sub, slug))
        alias = (d.get("alias") or "").lstrip("/")
        url = cfg["base"] + (alias or f"node/{d.get('nid')}")
        dest = dest_dir / f"{slug}.md"
        dest.write_text(
            f"# {title}\n\n{body}\n\n---\n\nSource: {url}\n",
            encoding="utf-8",
        )
        n += 1
    print(f"  {cfg['file']}: {n} chapters")
    return n


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    total = 0
    for cfg in SOURCES:
        print(f"== {cfg['file']} ==")
        total += compile_source(cfg)
    print(f"total {total}")


if __name__ == "__main__":
    main()

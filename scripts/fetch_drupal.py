#!/usr/bin/env python3
"""Fetch Drupal article HTML (Random Roads, Dumpsterdam, Moneyless, Casa Robino)."""

from __future__ import annotations

import argparse
import re
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup
from markdownify import markdownify as html_md

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT, get, slugify
from images import save_image, write_manifest
from titles import DRUPAL_SITES

SKIP_PATH_PREFIXES = (
    "/user",
    "/users/",
    "/tags/",
    "/tag/",
    "/taxonomy/",
    "/comment",
    "/filter",
    "/sites/",
    "/misc/",
    "/category/",
)


def soup(url: str) -> BeautifulSoup:
    r = get(url, timeout=60)
    return BeautifulSoup(r.text, "html.parser")


def canon(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", p.query, ""))


def is_skipped(path: str, url: str, skip) -> bool:
    if any(s in url for s in skip):
        return True
    if any(path.startswith(p) for p in SKIP_PATH_PREFIXES):
        return True
    if path.endswith("/rss.xml") or path.endswith("/feed"):
        return True
    return False


def looks_like_article(path: str, article_re: re.Pattern | None) -> bool:
    if path in ("", "/"):
        return False
    if article_re:
        return bool(article_re.search(path))
    if re.search(r"/\d+$", path) or "/node/" in path:
        return True
    if re.search(r"/\d{4}/\d{2}/", path):
        return True
    return False


def article_urls(base: str, list_paths: list[str], skip, article_re: str | None, max_pages: int = 40) -> list[str]:
    pattern = re.compile(article_re) if article_re else None
    found: list[str] = []
    seen_articles: set[str] = set()
    seen_pages: set[str] = set()
    queue: deque[str] = deque()
    for path in list_paths:
        queue.append(canon(urljoin(base + "/", path.lstrip("/"))))
    while queue and len(seen_pages) < max_pages:
        url = queue.popleft()
        if url in seen_pages:
            continue
        seen_pages.add(url)
        try:
            doc = soup(url)
        except Exception as exc:
            print(f"  list {url} failed: {exc}", file=sys.stderr, flush=True)
            continue
        print(f"  list {url}", flush=True)
        for a in doc.select("a[href]"):
            href = a.get("href") or ""
            absu = canon(urljoin(url, href))
            if not absu.startswith(base):
                continue
            p = urlparse(absu).path.rstrip("/") or "/"
            if is_skipped(p, absu, skip):
                continue
            qs = urlparse(absu).query
            if "page=" in qs or re.search(r"page=\d+", href):
                if absu not in seen_pages:
                    queue.append(absu)
                continue
            if looks_like_article(p, pattern) or a.find_parent("article") or "read more" in (a.get_text() or "").lower():
                if absu not in seen_articles:
                    seen_articles.add(absu)
                    found.append(absu)
    return found


def extract_article(url: str) -> tuple[str, str, str] | None:
    doc = soup(url)
    title_el = doc.select_one("h1") or doc.select_one("title")
    title = title_el.get_text(" ", strip=True) if title_el else url
    node = doc.select_one("article") or doc.select_one(".node") or doc.select_one("#content")
    if not node:
        return None
    for junk in node.select("nav, .comment, #comments, .links, script, style, .field-type-taxonomy-term-reference"):
        junk.decompose()
    html = str(node)
    md = html_md(html, heading_style="ATX", strip=["script", "style"])
    return title, md, html


def fetch_images_from_html(html: str, page_url: str, img_dir: Path, manifest: list) -> str:
    doc = BeautifulSoup(html, "html.parser")
    bits = []
    for img in doc.select("img[src]")[:8]:
        src = urljoin(page_url, img.get("src") or "")
        if "logo" in src.lower() or src.endswith(".svg"):
            continue
        alt = img.get("alt") or "image"
        path = save_image(src, img_dir, alt)
        if not path:
            continue
        bits.append(f"![{alt}](../../images/{path.name})\n")
        manifest.append({"file": path.name, "source": src, "author": "", "license": "", "caption": alt})
    return "\n".join(bits)


def fetch_site(key: str, *, limit: int | None) -> None:
    cfg = DRUPAL_SITES[key]
    print(f"== {key} {cfg['base']} ==", flush=True)
    urls = article_urls(
        cfg["base"],
        list(cfg["list_paths"]),
        cfg.get("skip_path_contains") or (),
        cfg.get("article_path_re"),
        max_pages=int(cfg.get("max_list_pages") or 40),
    )
    if limit:
        urls = urls[:limit]
    print(f"  articles={len(urls)}", flush=True)
    book = ROOT / "books" / cfg["book"]
    lang = cfg.get("lang", "en")
    sub = cfg.get("subdir")
    src = book / "src" / (sub or lang)
    img_dir = book / "images"
    src.mkdir(parents=True, exist_ok=True)
    manifest = []
    n = 0
    for url in urls:
        try:
            got = extract_article(url)
        except Exception as exc:
            print(f"  fail {url}: {exc}", file=sys.stderr, flush=True)
            continue
        if not got:
            continue
        title, md, html = got
        extra = fetch_images_from_html(html, url, img_dir, manifest)
        dest = src / f"{slugify(title)}.md"
        dest.write_text(
            f"# {title}\n\n{md}\n\n{extra}\n\n---\n\nSource: {url}\n",
            encoding="utf-8",
        )
        n += 1
        if n % 10 == 0:
            print(f"  wrote {n}/{len(urls)}", flush=True)
    if manifest:
        write_manifest(img_dir / "images.json", manifest)
    print(f"  wrote {n} chapters", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--site", choices=list(DRUPAL_SITES), action="append")
    p.add_argument("--all", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    args = p.parse_args()
    sites = list(DRUPAL_SITES) if args.all or not args.site else args.site
    for s in sites:
        fetch_site(s, limit=args.limit)


if __name__ == "__main__":
    main()

"""Shared helpers for fetch/build scripts."""

from __future__ import annotations

import datetime as dt
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "dumps"
GITHUB_URL = "https://github.com/guaka/books"
GITHUB_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">'
    '<path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8"/>'
    "</svg>"
)
USER_AGENT = (
    f"books.hitchwiki.org/0.1 (+{GITHUB_URL}; "
    "compiler for CC-licensed books)"
)
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*"})


def github_icon_link() -> str:
    return (
        f'<a class="github" href="{GITHUB_URL}" aria-label="Source on GitHub">'
        f"{GITHUB_ICON_SVG}</a>"
    )


def utc_version(prefix: str = "0.1") -> str:
    return f"{prefix}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M')}"


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s[:80] or "untitled"


def wiki_image_map(images_dir: Path) -> dict[str, str]:
    """Map wiki filenames to images/<saved jpeg> using images.json."""
    mapping: dict[str, str] = {}
    manifest = images_dir / "images.json"
    if not manifest.is_file():
        return mapping
    for entry in json.loads(manifest.read_text(encoding="utf-8")):
        dest = entry.get("file") or ""
        if not dest:
            continue
        rel = f"images/{dest}"
        names = {dest}
        source = entry.get("source") or ""
        if source:
            names.add(unquote(urlparse(source).path.rsplit("/", 1)[-1]))
        for name in names:
            name = name.strip().strip("\u200e\u200f")
            if not name:
                continue
            mapping[name] = rel
            mapping[name.replace(" ", "_")] = rel
    return mapping


_IMG_SRC = re.compile(r'(<img\b)([^>]*?\bsrc=")([^"]+)(")', re.I | re.S)

_WIKI_HOSTS = {
    "hitchwiki.org",
    "nomadwiki.org",
    "trashwiki.org",
    "wiki.trustroots.org",
}


def rewrite_html_images(html: str, mapping: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        start, mid, src, end = m.group(1), m.group(2), m.group(3), m.group(4)
        name = Path(unquote(src)).name.strip().strip("\u200e\u200f")
        target = mapping.get(name) or mapping.get(name.replace(" ", "_"))
        src_out = target or src
        attrs = start + mid
        if "loading=" not in attrs.lower():
            attrs = attrs.replace("<img", '<img loading="lazy" decoding="async"', 1)
        return f"{attrs}{src_out}{end}"

    return _IMG_SRC.sub(repl, html)


def wiki_edit_url(url: str) -> str | None:
    """Return a MediaWiki edit URL for the wikis compiled into these books."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if parsed.scheme not in {"http", "https"} or host not in _WIKI_HOSTS:
        return None
    query = parsed.query
    if re.search(r"(?:^|&)action=", query):
        query = re.sub(r"(^|&)action=[^&]*", r"\1action=edit", query)
    else:
        query = f"{query}&action=edit" if query else "action=edit"
    return parsed._replace(query=query, fragment="").geturl()


def get(url: str, *, timeout: int = 60, retries: int = 4, **kwargs) -> requests.Response:
    last = None
    for i in range(retries):
        try:
            r = SESSION.get(url, timeout=timeout, **kwargs)
            if r.status_code in (429, 502, 503, 504) or r.status_code == 403:
                time.sleep(1.5 * (i + 1))
                last = r
                continue
            r.raise_for_status()
            return r
        except requests.RequestException as exc:
            last = exc
            time.sleep(1.5 * (i + 1))
    if isinstance(last, requests.Response):
        last.raise_for_status()
    raise last  # type: ignore[misc]


def download(url: str, dest: Path, *, timeout: int = 120) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    r = get(url, timeout=timeout, stream=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with tmp.open("wb") as fh:
        for chunk in r.iter_content(1024 * 64):
            fh.write(chunk)
    tmp.replace(dest)
    return dest


def mw_api(api: str, params: dict) -> dict:
    params = {"format": "json", **params}
    r = get(api, params=params, timeout=90)
    return r.json()


def category_members(api: str, category: str, namespace: int = 0) -> list[str]:
    titles: list[str] = []
    cont = None
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category if category.startswith("Category:") else f"Category:{category}",
            "cmlimit": "500",
            "cmnamespace": str(namespace),
        }
        if cont:
            params["cmcontinue"] = cont
        data = mw_api(api, params)
        titles.extend(m["title"] for m in data.get("query", {}).get("categorymembers", []))
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
    return titles


def file_url_join(base: str, path: str) -> str:
    return urljoin(base if base.endswith("/") else base + "/", quote(path, safe="/"))

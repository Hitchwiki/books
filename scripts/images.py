"""Download, license-check, and resize images."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image, ImageFile

from common import get, mw_api, slugify

ImageFile.LOAD_TRUNCATED_IMAGES = True

MAX_WIDTH = 1200
SKIP_LICENSE_HINTS = (
    "all rights reserved",
    "fair use",
    "trademark",
    "unlicensed",
)
WIKI_APIS = (
    ("hitchwiki.org", "https://hitchwiki.org/en/api.php"),
    ("trashwiki.org", "https://trashwiki.org/api.php"),
    ("nomadwiki.org", "https://nomadwiki.org/api.php"),
    ("wiki.trustroots.org", "https://wiki.trustroots.org/api.php"),
    ("commons.wikimedia.org", "https://commons.wikimedia.org/w/api.php"),
    ("upload.wikimedia.org", "https://commons.wikimedia.org/w/api.php"),
)


def to_rgb(im: Image.Image) -> Image.Image:
    if im.mode in ("RGB", "L"):
        return im
    if im.mode in ("RGBA", "LA", "P") or "transparency" in im.info:
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.getchannel("A"))
        return bg
    return im.convert("RGB")


def resize_bytes(data: bytes, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = to_rgb(Image.open(BytesIO(data)))
    w, h = im.size
    if w > MAX_WIDTH:
        h = int(h * MAX_WIDTH / w)
        im = im.resize((MAX_WIDTH, h), Image.Resampling.LANCZOS)
    dest = dest.with_suffix(".jpg")
    im.save(dest, "JPEG", quality=80, optimize=True)
    return dest


def license_ok(text: str | None) -> bool:
    if not text:
        return True
    low = text.lower()
    if any(s in low for s in SKIP_LICENSE_HINTS):
        return False
    return True


def _wiki_api(url: str) -> str | None:
    host = urlparse(url).netloc.lower()
    for needle, api in WIKI_APIS:
        if needle in host:
            return api
    return None


def _filename_from_url(url: str) -> str:
    return unquote(urlparse(url).path.rsplit("/", 1)[-1])


def candidate_urls(url: str) -> list[str]:
    out: list[str] = []
    api = _wiki_api(url)
    name = _filename_from_url(url)
    if api and name:
        try:
            data = mw_api(
                api,
                {
                    "action": "query",
                    "titles": f"File:{name}",
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "iiurlwidth": str(MAX_WIDTH),
                },
            )
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                info = (page.get("imageinfo") or [None])[0]
                if not info:
                    continue
                for key in ("thumburl", "url"):
                    u = info.get(key)
                    if u and u not in out:
                        out.append(u)
        except Exception:
            pass
    if url not in out:
        out.append(url)
    return out


def fetch_bytes(url: str, *, timeout: int = 90) -> bytes:
    last: Exception | None = None
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"
    for candidate in candidate_urls(url):
        try:
            r = get(
                candidate,
                timeout=timeout,
                headers={"Referer": origin, "Accept": "image/*,*/*;q=0.8"},
            )
            if r.content and len(r.content) > 32:
                return r.content
        except Exception as exc:
            last = exc
            continue
    if last:
        raise last
    raise RuntimeError(f"empty image {url}")


def save_image(url: str, dest_dir: Path, stem: str) -> Path | None:
    dest = dest_dir / f"{slugify(stem)}.jpg"
    try:
        return resize_bytes(fetch_bytes(url), dest)
    except Exception:
        return None


def write_manifest(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

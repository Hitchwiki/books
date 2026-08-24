#!/usr/bin/env python3
"""Download OFL fonts, write theme CSS, and paint JPEG covers."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT, get
from themes import (
    FONT_URL_FALLBACKS,
    FONT_URLS,
    SOURCE_SERIF_FILES,
    SOURCE_SERIF_ZIP,
    THEMES,
    covers_dir,
    fonts_dir,
    logos_dir,
    write_css_files,
)

W, H = 1400, 2100


def hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


def paste_logo(img: Image.Image, slug: str, *, x: int, y: int, max_h: int = 280, max_w: int = 900) -> int:
    """Paste a source-site logo; return y below it."""
    t = THEMES[slug]
    name = t.get("logo")
    if not name:
        return y
    path = logos_dir() / name
    if not path.exists():
        return y
    try:
        logo = Image.open(path).convert("RGBA")
    except OSError:
        return y
    w, h = logo.size
    scale = min(max_w / max(w, 1), max_h / max(h, 1), 1.0 if w > 400 else 4.0)
    nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
    logo = logo.resize((nw, nh), Image.Resampling.LANCZOS)
    if x < 0:
        x = (W - nw) // 2
    img.paste(logo, (x, y), logo)
    return y + nh + 40


def fetch_source_serif() -> None:
    dest_dir = fonts_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    if all((dest_dir / name).exists() and (dest_dir / name).stat().st_size > 1000 for name in SOURCE_SERIF_FILES):
        return
    print("  Source Serif 4 zip")
    r = get(SOURCE_SERIF_ZIP, timeout=120, retries=2)
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    for info in zf.infolist():
        base = Path(info.filename).name
        if base in SOURCE_SERIF_FILES and not info.is_dir():
            (dest_dir / base).write_bytes(zf.read(info))
            print(f"  font {base} ({info.file_size} bytes)")


def fetch_font(name: str) -> Path:
    dest = fonts_dir() / name
    if dest.exists() and dest.stat().st_size > 1000:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    urls = [FONT_URLS[name], *FONT_URL_FALLBACKS.get(name, [])]
    last = None
    for url in urls:
        try:
            r = get(url, timeout=90, retries=2)
            if r.status_code == 200 and len(r.content) > 1000:
                dest.write_bytes(r.content)
                print(f"  font {name} ({len(r.content)} bytes)")
                return dest
            last = f"HTTP {r.status_code} {url}"
        except Exception as exc:
            last = f"{exc} {url}"
    raise RuntimeError(f"could not download {name}: {last}")


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = fonts_dir() / name
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size=size)
        except OSError:
            pass
    for fallback in (
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ):
        if Path(fallback).exists():
            return ImageFont.truetype(fallback, size=size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [text]


def paint(slug: str, meta: dict) -> Image.Image:
    t = THEMES[slug]
    img = Image.new("RGB", (W, H), hex_rgb(t["cover_bg"]))
    d = ImageDraw.Draw(img)
    motif = t["motif"]
    fg = hex_rgb(t["cover_fg"])
    accent = hex_rgb(t["accent"])
    accent2 = hex_rgb(t["accent2"])
    display = load_font(t["display_file"], 118)
    small = load_font(t.get("body_file") or t["display_file"], 36)
    tiny = load_font(t.get("body_file") or t["display_file"], 28)
    title = meta.get("title", slug)
    sub = meta.get("subtitle", "")
    license_id = meta.get("license", "")
    kicker = t["kicker"].upper()
    logo_x = 110
    logo_y = 110
    logo_h = 280
    logo_w = 720

    if motif == "hitchwiki":
        d.rectangle([0, H - 28, W, H], fill=hex_rgb("#b73327"))
        y_title = 620
        kicker_y = 480
    elif motif == "trashwiki":
        y_title = 640
        kicker_y = 500
        logo_h = 320
    elif motif == "masthead":
        d.rectangle([0, 0, W, 90], fill=accent2)
        d.rectangle([0, H - 90, W, H], fill=accent2)
        fg = hex_rgb(t["cover_fg"])
        y_title = 720
        kicker_y = 560
        logo_w = 1100
        logo_h = 160
        logo_x = -1
    elif motif == "slab":
        d.rectangle([0, 0, 70, H], fill=accent2)
        display = load_font(t["display_file"], 150)
        y_title = 720
        kicker_y = 560
        logo_x = 130
    elif motif == "door":
        d.rectangle([0, 0, W, H], fill=hex_rgb(t["bg"]))
        d.rectangle([70, 70, W - 70, H - 70], fill=accent2)
        d.rectangle([110, 110, W - 110, H - 110], fill=hex_rgb(t["cover_bg"]))
        y_title = 980
        kicker_y = 820
        logo_x = -1
        logo_y = 180
        logo_h = 360
    elif motif == "spare":
        d.rectangle([0, 0, W, H], fill=hex_rgb(t["cover_bg"]))
        fg = hex_rgb(t["cover_fg"])
        y_title = 1480
        kicker_y = 1280
        display = load_font(t["display_file"], 88)
        logo_w = 1100
        logo_h = 220
        logo_x = 110
        logo_y = 160
    elif motif == "grid":
        d.rectangle([0, 0, W, 70], fill=hex_rgb("#ffdc18"))
        d.rectangle([0, H - 70, W, H], fill=hex_rgb("#ffdc18"))
        y_title = 820
        kicker_y = 660
        logo_h = 360
        logo_x = -1
        logo_y = 140
    else:
        y_title = 640
        kicker_y = 500

    paste_logo(img, slug, x=logo_x, y=logo_y, max_h=logo_h, max_w=logo_w)

    max_w = W - 220
    d.text((110, kicker_y), kicker, font=tiny, fill=fg)
    lines = wrap(d, title, display, max_w)
    y = y_title
    for line in lines:
        d.text((110, y), line, font=display, fill=fg)
        y += int(display.size * 1.12) if hasattr(display, "size") else 130
    if sub:
        for line in wrap(d, sub, small, max_w - 40):
            y += 12
            d.text((110, y), line, font=small, fill=fg)
            y += 48
    d.text((110, H - 140), f"books.hitchwiki.org  ·  {license_id}", font=tiny, fill=fg)
    return img


def metadata(slug: str) -> dict:
    import yaml

    path = ROOT / "books" / slug / "metadata.yaml"
    if not path.exists():
        return {"title": slug}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> None:
    print("fonts")
    fetch_source_serif()
    for name in FONT_URLS:
        try:
            fetch_font(name)
        except Exception as exc:
            print(f"  WARN {name}: {exc}", file=sys.stderr)
    write_css_files()
    out = covers_dir()
    out.mkdir(parents=True, exist_ok=True)
    for slug in THEMES:
        img = paint(slug, metadata(slug))
        dest = out / f"{slug}.jpg"
        img.save(dest, "JPEG", quality=88, optimize=True)
        print(f"cover {dest}")


if __name__ == "__main__":
    main()

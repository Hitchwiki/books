#!/usr/bin/env python3
"""Download OFL fonts, write theme CSS, and paint JPEG covers."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import get
from themes import (
    FONT_URL_FALLBACKS,
    FONT_URLS,
    SOURCE_SERIF_FILES,
    SOURCE_SERIF_ZIP,
    THEMES,
    covers_dir,
    fonts_dir,
    write_css_files,
)
from common import ROOT

W, H = 1400, 2100


def hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)


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

    if motif == "horizon":
        d.rectangle([0, 0, W, int(H * 0.62)], fill=hex_rgb("#1e3a5f"))
        d.rectangle([0, int(H * 0.62), W, H], fill=hex_rgb("#c45c26"))
        d.rectangle([0, int(H * 0.62) - 6, W, int(H * 0.62) + 6], fill=hex_rgb("#f3ead7"))
        for i in range(18):
            x0 = 80 + i * 70
            d.rectangle([x0, int(H * 0.62) - 2, x0 + 36, int(H * 0.62) + 2], fill=hex_rgb("#1e3a5f"))
        fg = hex_rgb("#f3ead7")
        y_title = 280
    elif motif == "hazard":
        stripe = 54
        for i in range(-8, 50):
            pts = [
                (i * stripe, 0),
                (i * stripe + 28, 0),
                (i * stripe + 28 + H, H),
                (i * stripe + H, H),
            ]
            d.polygon(pts, fill=hex_rgb("#14160f") if i % 2 else hex_rgb("#e2c93a"))
        d.rectangle([70, 620, W - 70, 1480], fill=hex_rgb("#14160f"))
        fg = hex_rgb("#e2c93a")
        y_title = 700
    elif motif == "masthead":
        d.rectangle([0, 0, W, 90], fill=accent)
        d.rectangle([0, H - 90, W, H], fill=accent)
        d.rectangle([90, 220, W - 90, 228], fill=hex_rgb(t["fg"]))
        fg = hex_rgb(t["fg"])
        y_title = 360
    elif motif == "slab":
        d.rectangle([0, 0, 70, H], fill=hex_rgb("#1f4d3a"))
        display = load_font(t["display_file"], 150)
        y_title = 520
    elif motif == "door":
        d.rectangle([0, 0, W, H], fill=hex_rgb(t["bg"]))
        d.rectangle([70, 70, W - 70, H - 70], fill=accent2)
        d.rectangle([110, 110, W - 110, H - 110], fill=hex_rgb(t["cover_bg"]))
        y_title = 720
    elif motif == "spare":
        d.rectangle([0, 0, W, H], fill=hex_rgb(t["bg"]))
        d.rectangle([110, 110, 190, 190], fill=accent)
        fg = hex_rgb(t["fg"])
        y_title = 1480
        display = load_font(t["display_file"], 88)
    elif motif == "grid":
        step = 48
        grid = hex_rgb("#5a7390")
        for x in range(0, W, step):
            d.line([(x, 0), (x, H)], fill=grid, width=1)
        for y in range(0, H, step):
            d.line([(0, y), (W, y)], fill=grid, width=1)
        d.line([(120, 520), (1180, 980)], fill=hex_rgb(t["cover_fg"]), width=3)
        y_title = 1100
    else:
        y_title = 500

    kicker_y = 120
    if motif == "hazard":
        kicker_y = 650
    elif motif == "door":
        kicker_y = 180
    elif motif == "spare":
        kicker_y = 220

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

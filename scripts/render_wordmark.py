#!/usr/bin/env python3
"""Crop the catalog's Hitchwiki wordmark from the licensed source artwork."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "logos" / "hitchwiki-2015.png"
DESTINATION = ROOT / "assets" / "logos" / "hitchwiki-wordmark.png"
CROP = (55, 45, 1105, 320)


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    wordmark = image.crop(CROP)
    wordmark.save(DESTINATION, optimize=True)
    print(DESTINATION)


if __name__ == "__main__":
    main()

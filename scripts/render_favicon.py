#!/usr/bin/env python3
"""Render the books.hitchwiki.org favicon in the Hitchwiki palette."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SIZE = 512
YELLOW = "#f7df79"
BROWN = "#6e3100"
ORANGE = "#b96800"
PAPER = "#fffaf0"


def render() -> Image.Image:
    image = Image.new("RGB", (SIZE, SIZE), YELLOW)
    draw = ImageDraw.Draw(image)

    # A broad open-book silhouette remains legible after reduction to 16px.
    left_page = [(62, 128), (232, 158), (256, 190), (256, 432), (226, 408), (62, 378)]
    right_page = [(450, 128), (280, 158), (256, 190), (256, 432), (286, 408), (450, 378)]
    draw.polygon(left_page, fill=PAPER, outline=BROWN, width=22)
    draw.polygon(right_page, fill=PAPER, outline=BROWN, width=22)

    # Page suggestions and an orange bookmark add depth without tiny detail.
    draw.line([(92, 190), (214, 211), (236, 229)], fill=ORANGE, width=15)
    draw.line([(420, 190), (298, 211), (276, 229)], fill=ORANGE, width=15)
    draw.polygon([(238, 160), (274, 164), (274, 302), (256, 280), (238, 302)], fill=ORANGE)
    draw.line([(256, 188), (256, 431)], fill=BROWN, width=18)
    return image


def main() -> None:
    destination = ROOT / "assets" / "favicon.ico"
    render().save(
        destination,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(destination)


if __name__ == "__main__":
    main()

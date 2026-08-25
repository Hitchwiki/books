"""Per-book visual identity: color, type, cover motif, source logos.

Tokens come from the related websites (see books/*/DESIGN.md).
CSS and JPEG covers are generated from this file (scripts/render_covers.py).
"""

from __future__ import annotations

import re
from pathlib import Path

from common import ROOT

THEMES: dict[str, dict] = {
    "hitchhikers-guide": {
        "motif": "hitchwiki",
        "bg": "#fbf7e9",
        "fg": "#5b2b08",
        "muted": "#76563c",
        "accent": "#b96800",
        "accent2": "#b73327",
        "rule": "#e5d8ba",
        "cover_fg": "#6e3100",
        "cover_bg": "#f7df79",
        "display": "Oswald",
        "display_file": "Oswald-Bold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": 'Palatino, "Palatino Linotype", Georgia, serif',
        "measure": "44rem",
        "kicker": "By 1,300+ hitchhikers",
        "logo": "hitchhikers-guide.png",
        "logo_alt": "Hitchwiki",
        "cover_hide_subtitle": True,
        "cover_photo": {
            "commons": "Hitchhiker-Luxemburg-1977.jpg",
            "author": "Roger McLassus",
            "license": "CC BY-SA 3.0",
            "page": "https://commons.wikimedia.org/wiki/File:Hitchhiker-Luxemburg-1977.jpg",
            "caption": "Hitchhiker in Luxembourg, August 1977 — also used on hitchhiking.org",
            "focus": (0.52, 0.38),
            "pos": "center 28%",
            "wash": 72,
        },
    },
    "dumpster-diving": {
        "motif": "trashwiki",
        "bg": "#f9f9f4",
        "fg": "#1f241c",
        "muted": "#4a5c48",
        "accent": "#2f5a40",
        "accent2": "#4a6b52",
        "rule": "#c5c6b6",
        "cover_fg": "#1f241c",
        "cover_bg": "#dcddcb",
        "display": "Oswald",
        "display_file": "Oswald-Bold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "46rem",
        "kicker": "By 230+ dumpster divers",
        "logo": "dumpster-diving.png",
        "logo_alt": "Trashwiki",
        "cover_photo": {
            "commons": "Edible food from a food retailer's container.jpg",
            "author": "PizzaToast",
            "license": "CC0",
            "page": "https://commons.wikimedia.org/wiki/File:Edible_food_from_a_food_retailer%27s_container.jpg",
            "caption": "Edible food recovered from a food retailer's container",
            "focus": (0.5, 0.48),
            "pos": "center 42%",
            "wash": 58,
        },
    },
    "random-roads": {
        "motif": "masthead",
        "bg": "#ffffea",
        "fg": "#261c14",
        "muted": "#555555",
        "accent": "#0ca6bb",
        "accent2": "#076370",
        "rule": "#d3d7d9",
        "cover_fg": "#ffffff",
        "cover_bg": "#0ca6bb",
        "display": "Georgia",
        "body": "Georgia",
        "fallback": 'Georgia, "Times New Roman", Times, serif',
        "ui": "Open Sans",
        "ui_file": "OpenSans-Regular.ttf",
        "ui_bold": "OpenSans-Bold.ttf",
        "measure": "42rem",
        "kicker": "A hitchhiking zine",
        "logo": "random-roads.png",
        "logo_alt": "Random Roads",
        "logo_wide": True,
        "cover_logo_is_title": True,
        "cover_photo": {
            "commons": "Country Road Hitchhiker (Unsplash).jpg",
            "author": "Seth Doyle",
            "license": "CC0 1.0",
            "page": "https://commons.wikimedia.org/wiki/File:Country_Road_Hitchhiker_(Unsplash).jpg",
            "caption": "Country road hitchhiker, 2017",
            "focus": (0.34, 0.5),
            "pos": "38% 45%",
            "wash": 24,
        },
    },
    "dumpsterdam": {
        "motif": "slab",
        "bg": "#fff6ea",
        "fg": "#111111",
        "muted": "#5c4038",
        "accent": "#9a2016",
        "accent2": "#759236",
        "rule": "#e4d4c4",
        "cover_fg": "#fff6ea",
        "cover_bg": "#9a2016",
        "display": "Oswald",
        "display_file": "Oswald-Bold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "46rem",
        "kicker": "Voedselactivisme uit Amsterdam",
        "logo": "dumpsterdam.png",
        "logo_alt": "Trasher",
        "logo_small": True,
        "cover_photo": {
            "commons": "An empty, clean container from a food retailer.jpg",
            "author": "PizzaToast",
            "license": "CC0",
            "page": "https://commons.wikimedia.org/wiki/File:An_empty,_clean_container_from_a_food_retailer.jpg",
            "caption": "Open food-retail dumpster",
            "focus": (0.5, 0.42),
            "pos": "center 35%",
            "wash": 96,
        },
    },
    "geldloos": {
        "motif": "gift",
        "bg": "#eef4ea",
        "fg": "#1c2818",
        "muted": "#5a6b52",
        "accent": "#3d6b3a",
        "accent2": "#8b5a2b",
        "rule": "#d5e0d0",
        "cover_fg": "#eef4ea",
        "cover_bg": "#1e2e1c",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": "Georgia, Palatino, serif",
        "measure": "42rem",
        "kicker": "Leven met minder, of zonder",
        "cover_photo": {
            "commons": "Netherlands, Kaag en Braassem, Hoogmade, Piestpolders (2).jpg",
            "author": "Vincent van Zeijst",
            "license": "CC BY-SA 4.0",
            "page": "https://commons.wikimedia.org/wiki/File:Netherlands,_Kaag_en_Braassem,_Hoogmade,_Piestpolders_(2).jpg",
            "caption": "Allotment gardens in the Piest polder, Hoogmade",
            "focus": (0.5, 0.42),
            "pos": "center 38%",
            "wash": 64,
        },
    },
    "hospitality-exchange": {
        "motif": "door",
        "bg": "#faf7f2",
        "fg": "#2a2724",
        "muted": "#6a6158",
        "accent": "#3f6f68",
        "accent2": "#8b5e3c",
        "rule": "#e4d9cc",
        "cover_fg": "#faf7f2",
        "cover_bg": "#2c2824",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": "Georgia, Palatino, serif",
        "measure": "44rem",
        "kicker": "By 30+ people",
        "cover_photo": {
            "commons": "Tengboche, Sherpa family, Nepal.jpg",
            "author": "Vyacheslav Argenberg",
            "license": "CC BY 4.0",
            "page": "https://commons.wikimedia.org/wiki/File:Tengboche,_Sherpa_family,_Nepal.jpg",
            "caption": "A traveler sharing a meal with a Sherpa family in Tengboche, Nepal",
            "focus": (0.45, 0.5),
            "pos": "45% center",
            "wash": 54,
        },
    },
    "moneyless": {
        "motif": "gift",
        "bg": "#f7f1e6",
        "fg": "#2a1c14",
        "muted": "#7a5e4a",
        "accent": "#c4452d",
        "accent2": "#5c3a1e",
        "rule": "#e4d4c0",
        "cover_fg": "#f7f1e6",
        "cover_bg": "#3a2418",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": "Georgia, Palatino, serif",
        "measure": "42rem",
        "kicker": "On living with less, or none",
        "cover_photo": {
            "commons": "Basket of tomatoes and peppers (556d293c-c060-43ee-bc99-636b82fa3969).jpg",
            "author": "National Park Service",
            "license": "Public domain",
            "page": "https://commons.wikimedia.org/wiki/File:Basket_of_tomatoes_and_peppers_(556d293c-c060-43ee-bc99-636b82fa3969).jpg",
            "caption": "Garden harvest of tomatoes and peppers, Lincoln Home National Historic Site",
            "focus": (0.5, 0.38),
            "pos": "center 32%",
            "wash": 56,
        },
    },
    "sin-dinero": {
        "motif": "gift",
        "bg": "#f8f0e4",
        "fg": "#2c1a10",
        "muted": "#8a6240",
        "accent": "#c45c1a",
        "accent2": "#6b3a18",
        "rule": "#ead8c4",
        "cover_fg": "#f8f0e4",
        "cover_bg": "#4a220c",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": "Georgia, Palatino, serif",
        "measure": "42rem",
        "kicker": "Vivir con menos, o sin nada",
        "cover_photo": {
            "commons": "Ambersweet oranges.jpg",
            "author": "USDA Agricultural Research Service",
            "license": "Public domain",
            "page": "https://commons.wikimedia.org/wiki/File:Ambersweet_oranges.jpg",
            "caption": "Ambersweet oranges",
            "focus": (0.5, 0.42),
            "pos": "center 38%",
            "wash": 56,
        },
    },
    "shoestring-nomad": {
        "motif": "grid",
        "bg": "#fffdf8",
        "fg": "#25232b",
        "muted": "#5f5a52",
        "accent": "#654d00",
        "accent2": "#4a3a08",
        "rule": "#d9d0bc",
        "cover_fg": "#4a3a08",
        "cover_bg": "#f6f3e9",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "46rem",
        "kicker": "From Nomadwiki",
        "logo": "shoestring-nomad.png",
        "logo_alt": "Nomadwiki",
        "cover_hide_kicker": True,
        "cover_hide_subtitle": True,
        "cover_photo": {
            "commons": "Tent Camping (f74c8bec-5813-4f56-b690-9db8b3caac30).JPG",
            "author": "National Park Service",
            "license": "Public domain",
            "page": "https://commons.wikimedia.org/wiki/File:Tent_Camping_(f74c8bec-5813-4f56-b690-9db8b3caac30).JPG",
            "caption": "A backpacker setting up camp in the Denali backcountry",
            "focus": (0.68, 0.5),
            "pos": "68% center",
            "wash": 38,
        },
    },
}

FONT_URLS = {
    "SourceSans3-Regular.ttf": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-sans@3.052R/release/TTF/SourceSans3-Regular.ttf",
    "SourceSans3-Bold.ttf": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-sans@3.052R/release/TTF/SourceSans3-Bold.ttf",
    "Oswald-Bold.ttf": "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf",
    "OpenSans-Regular.ttf": "https://cdn.jsdelivr.net/gh/googlefonts/opensans@main/fonts/ttf/OpenSans-Regular.ttf",
    "OpenSans-Bold.ttf": "https://cdn.jsdelivr.net/gh/googlefonts/opensans@main/fonts/ttf/OpenSans-Bold.ttf",
    "IBMPlexSerif-Regular.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-serif/fonts/complete/ttf/IBMPlexSerif-Regular.ttf",
    "IBMPlexSans-Regular.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf",
    "IBMPlexSans-Bold.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Bold.ttf",
}

FONT_URL_FALLBACKS = {
    "Oswald-Bold.ttf": ["https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf"],
    "OpenSans-Regular.ttf": [
        "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Regular.ttf"
    ],
    "OpenSans-Bold.ttf": [
        "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Bold.ttf"
    ],
    "IBMPlexSerif-Regular.ttf": [
        "https://github.com/IBM/plex/raw/master/IBM-Plex-Serif/fonts/complete/ttf/IBMPlexSerif-Regular.ttf"
    ],
    "IBMPlexSans-Regular.ttf": [
        "https://github.com/IBM/plex/raw/master/IBM-Plex-Sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf"
    ],
    "IBMPlexSans-Bold.ttf": [
        "https://github.com/IBM/plex/raw/master/IBM-Plex-Sans/fonts/complete/ttf/IBMPlexSans-Bold.ttf"
    ],
    "SourceSans3-Regular.ttf": [
        "https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-Regular.ttf"
    ],
    "SourceSans3-Bold.ttf": [
        "https://github.com/adobe-fonts/source-sans/raw/release/TTF/SourceSans3-Bold.ttf"
    ],
}

SOURCE_SERIF_ZIP = (
    "https://github.com/adobe-fonts/source-serif/releases/download/"
    "4.005R/source-serif-4.005_Desktop.zip"
)
SOURCE_SERIF_FILES = (
    "SourceSerif4-Regular.ttf",
    "SourceSerif4-Semibold.ttf",
    "SourceSerif4-Bold.ttf",
)


def fonts_dir() -> Path:
    return ROOT / "assets" / "fonts"


def covers_dir() -> Path:
    return ROOT / "assets" / "covers"


def logos_dir() -> Path:
    return ROOT / "assets" / "logos"


def photos_dir() -> Path:
    return ROOT / "assets" / "covers" / "photos"


def cover_rights(meta: dict) -> str:
    """Return the compact licence and copyright notice used on covers."""
    license_id = str(meta.get("license", "")).strip()
    match = re.search(r"©\s+(\d{4}[–-]\d{4})", str(meta.get("rights", "")))
    copyright_years = match.group(1) if match else ""
    parts = [part for part in (license_id, "🄯" if license_id else "", copyright_years) if part]
    return " ".join(parts)


def cover_html(slug: str, meta: dict) -> str:
    from ui_strings import ui_strings

    t = THEMES[slug]
    labels = ui_strings(str(meta.get("lang", "en")))
    title = "" if t.get("cover_logo_is_title") else meta.get("title", slug)
    sub = "" if t.get("cover_hide_subtitle") else meta.get("subtitle", "")
    kicker = "" if t.get("cover_hide_kicker") else t["kicker"]
    if sub.casefold() == kicker.casefold():
        sub = ""
    rights_line = cover_rights(meta)
    logo = t.get("logo")
    wide = " cover-logo-wide" if t.get("logo_wide") else ""
    logo_title = " cover-logo-title" if t.get("cover_logo_is_title") else ""
    logo_html = ""
    if logo:
        alt = t.get("logo_alt", "")
        logo_version = '<span class="cover-version">0.1</span>' if logo_title else ""
        logo_html = (
            f'<p class="cover-logo-wrap{wide}{logo_title}">'
            f'<img class="cover-logo" src="logos/{logo}" alt="{alt}">'
            f"{logo_version}"
            f"</p>"
        )
    photo_class = " cover-has-photo" if t.get("cover_photo") else ""
    return f"""<section class="cover-page{photo_class}" aria-label="{labels['cover']}">
  {logo_html}
  {f'<p class="cover-kicker">{kicker}</p>' if kicker else ''}
  <div class="cover-main">
    {f'<h1 class="cover-title">{title} <span class="cover-version">0.1</span></h1>' if title else ''}
    {f'<p class="cover-sub">{sub}</p>' if sub else ''}
  </div>
  <p class="cover-foot"><span>books.hitchwiki.org</span><span>{rights_line}</span></p>
</section>
"""


def photo_credit_markdown(slug: str) -> str:
    """Cover-photo attribution for the first interior page, not the cover."""
    photo = (THEMES.get(slug) or {}).get("cover_photo") or {}
    if not photo:
        return ""
    who = photo.get("author") or ""
    lic = photo.get("license") or ""
    page = photo.get("page") or ""
    caption = photo.get("caption") or ""
    if who and page:
        who_bit = f'<a href="{page}">{who}</a>'
    elif who:
        who_bit = who
    elif page:
        who_bit = f'<a href="{page}">source</a>'
    else:
        who_bit = ""
    parts = [p for p in (who_bit, lic) if p]
    if not parts and not caption:
        return ""
    line = "Cover photograph: " + " · ".join(parts)
    if caption:
        line += f" — {caption}"
    return f'<p class="photo-credit">{line}</p>\n'


def _font_faces(t: dict, prefix: str) -> str:
    faces = []
    seen: set[tuple[str, str]] = set()
    for family, name, weight in (
        (t["display"], t.get("display_file"), "600"),
        (t["body"], t.get("body_file"), "400"),
        (t["body"], t.get("body_bold"), "700"),
        (t.get("ui"), t.get("ui_file"), "400"),
        (t.get("ui"), t.get("ui_bold"), "700"),
    ):
        if not family or not name or (family, name) in seen:
            continue
        seen.add((family, name))
        faces.append(
            f"""@font-face {{
  font-family: "{family}";
  src: url("{prefix}{name}") format("truetype");
  font-weight: {weight};
  font-style: normal;
  font-display: swap;
}}"""
        )
    return "\n".join(faces)


MOTIF_CSS = {
    "hitchwiki": """
body.book-SLUG .cover-title {
  font-style: normal;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
body.book-SLUG .cover-page::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 10px;
  z-index: 3;
  background: var(--accent2);
}
""",
    "trashwiki": """
body.book-SLUG .cover-title {
  font-style: normal;
  text-transform: uppercase;
}
body.book-SLUG .cover-logo {
  background: #e4e6d8;
  padding: 0.35rem;
  border-radius: 0.35rem;
}
""",
    "masthead": """
body.book-SLUG .cover-page {
  border-top: 14px solid var(--accent2);
  border-bottom: 14px solid var(--accent2);
}
body.book-SLUG .cover-title {
  font-style: normal;
  font-weight: 700;
  text-transform: uppercase;
  border-bottom: 1px solid currentColor;
  padding-bottom: 0.6rem;
}
body.book-SLUG .cover-kicker,
body.book-SLUG .cover-foot,
body.book-SLUG .cover-read,
body.book-SLUG .book-banner,
body.book-SLUG nav#TOC,
body.book-SLUG .toc-jump {
  font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-style: normal;
}
body.book-SLUG .cover-kicker { letter-spacing: 0.28em; }
""",
    "slab": """
body.book-SLUG .cover-title {
  font-style: normal;
  text-transform: uppercase;
  font-size: 4.4rem;
  line-height: 0.9;
}
body.book-SLUG .cover-page {
  border-left: 12px solid var(--accent2);
  box-sizing: border-box;
}
body.book-SLUG .cover-logo {
  background: #dcddcb;
  padding: 0.12rem;
}
""",
    "door": """
body.book-SLUG .cover-title {
  font-style: italic;
}
body.book-SLUG .cover-main { text-align: left; }
body.book-SLUG .cover-kicker { letter-spacing: 0.18em; }
""",
    "gift": """
body.book-SLUG .cover-title { font-style: normal; font-weight: 600; }
body.book-SLUG .cover-main { text-align: left; }
body.book-SLUG .cover-kicker { letter-spacing: 0.2em; }
body.book-SLUG .cover-page::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 14px;
  z-index: 3;
  background: var(--accent);
}
""",
    "grid": """
body.book-SLUG .cover-page {
  border-top: 18px solid #ffdc18;
  border-bottom: 18px solid #ffdc18;
}
body.book-SLUG .cover-title { font-style: italic; }
""",
}


def book_css(slug: str, *, font_prefix: str = "fonts/") -> str:
    t = THEMES[slug]
    italic = "italic" if slug in {"shoestring-nomad"} else "normal"
    cover_italic = "italic" if slug in {"shoestring-nomad", "hospitality-exchange"} else italic
    extra = MOTIF_CSS[t["motif"]].replace("SLUG", slug)
    if t.get("logo_small"):
        logo_max, logo_max_h = "2.5rem", "2.5rem"
    elif t.get("logo_wide"):
        logo_max, logo_max_h = "16rem", "5.6rem"
    else:
        logo_max, logo_max_h = "6.2rem", "5.6rem"
    photo = t.get("cover_photo") or {}
    photo_css = ""
    if photo:
        pos = photo.get("pos", "center")
        bg = t["cover_bg"]
        photo_css = f"""
body.book-{slug} .cover-page.cover-has-photo {{
  min-height: 34rem;
}}
body.book-{slug} .cover-page.cover-has-photo::before {{
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  background-image:
    linear-gradient(to top, {bg} 8%, {bg}d8 32%, {bg}00 62%),
    url("covers/photo.jpg");
  background-size: cover, cover;
  background-position: bottom, {pos};
  background-repeat: no-repeat;
  pointer-events: none;
}}
body.book-{slug} .cover-has-photo .cover-kicker,
body.book-{slug} .cover-has-photo .cover-main,
body.book-{slug} .cover-has-photo .cover-foot,
body.book-{slug} .cover-has-photo .cover-logo-wrap {{
  position: relative;
  z-index: 2;
}}
body.book-{slug} .photo-credit {{
  margin: 2rem 0 2.5rem;
  font-size: 0.88rem;
  color: var(--muted);
  max-width: 28rem;
}}
"""
    drop = ""
    if slug == "random-roads":
        drop = """
body.book-random-roads h1 + p::first-letter {
  float: left;
  font-family: Georgia, "Times New Roman", Times, serif;
  font-size: 3.4rem;
  line-height: 0.85;
  padding-right: 0.35rem;
  color: var(--accent);
}"""
    return f"""{_font_faces(t, font_prefix)}

html {{
  overflow-x: clip;
}}
body.book-{slug},
body.book-{slug} * {{
  box-sizing: border-box;
}}

body.book-{slug} {{
  --fg: {t["fg"]};
  --muted: {t["muted"]};
  --bg: {t["bg"]};
  --accent: {t["accent"]};
  --accent2: {t["accent2"]};
  --rule: {t["rule"]};
  --cover-bg: {t["cover_bg"]};
  --cover-fg: {t["cover_fg"]};
  --measure: {t["measure"]};
  --toc: 20rem;
  --banner: 5.1rem;
  background: var(--bg);
  color: var(--fg);
  font-family: "{t["body"]}", {t["fallback"]};
  max-width: var(--measure);
  margin: 0 auto;
  padding: 0 1.25rem 5rem;
  line-height: 1.58;
  font-size: 1.06rem;
  min-height: 100vh;
  width: 100%;
  overflow-wrap: anywhere;
}}
body.book-{slug} h1,
body.book-{slug} h2,
body.book-{slug} h3,
body.book-{slug} .cover-title {{
  font-family: "{t["display"]}", {t["fallback"]};
  font-style: {italic};
  font-weight: 600;
  line-height: 1.15;
  color: var(--fg);
}}
body.book-{slug} h1 {{ font-size: 2.15rem; margin: 2.4rem 0 0.8rem; }}
body.book-{slug} h2 {{ font-size: 1.45rem; margin-top: 2rem; }}
body.book-{slug} .book-body > #attribution ~ p,
body.book-{slug} .book-body > #attribution ~ ul,
body.book-{slug} .book-body > #attribution ~ ol {{
  font-size: 0.9rem;
  line-height: 1.45;
}}
body.book-{slug} .book-body > #attribution ~ h2 {{ font-size: 1.25rem; }}
body.book-{slug} .chapter-sources {{
  columns: 2 16rem;
  column-gap: 2rem;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.4;
}}
body.book-{slug} .chapter-sources p {{ margin: 0; }}
body.book-{slug} a {{ color: var(--accent); }}
body.book-{slug} hr {{ border: 0; border-top: 1px solid var(--rule); }}
body.book-{slug} .chapter-heading {{
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}}
body.book-{slug} .chapter-heading h1 {{ flex: 1 1 auto; min-width: 0; }}
body.book-{slug} .chapter-edit {{
  flex: 0 0 auto;
  color: var(--muted);
  font-family: {t["fallback"]};
  font-size: 0.72rem;
  font-style: normal;
  font-weight: 400;
  letter-spacing: 0.03em;
  text-decoration: none;
  border-bottom: 1px dotted currentColor;
}}
body.book-{slug} .chapter-edit:hover,
body.book-{slug} .chapter-edit:focus-visible {{ color: var(--accent); }}
body.book-{slug} .chapter-source {{
  color: var(--muted);
  font-size: 0.72rem;
  margin: 0.35rem 0 1rem;
}}
body.book-{slug} .chapter-source a {{
  color: inherit;
  text-decoration: none;
}}
body.book-{slug} .chapter-source a:hover,
body.book-{slug} .chapter-source a:focus-visible {{
  color: var(--accent);
  text-decoration: underline;
}}
body.book-{slug} img {{ max-width: 100%; height: auto; }}
body.book-{slug} figure {{ max-width: 100%; margin-left: 0; margin-right: 0; }}
body.book-{slug} iframe,
body.book-{slug} video,
body.book-{slug} svg {{ max-width: 100%; }}
body.book-{slug} pre {{
  max-width: 100%;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}}
body.book-{slug} code {{ overflow-wrap: anywhere; }}
body.book-{slug} table {{
  width: 100%;
  max-width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
}}
body.book-{slug} th,
body.book-{slug} td {{ overflow-wrap: anywhere; }}
@media print {{
  body.book-{slug} {{ font-size: 0.92rem; line-height: 1.48; }}
  body.book-{slug} h1 {{ font-size: 1.85rem; }}
  body.book-{slug} h2 {{ font-size: 1.25rem; }}
  body.book-{slug} h1 + p::first-letter {{
    float: none;
    font: inherit;
    padding: 0;
    color: inherit;
  }}
  body.book-{slug} .book-body > #attribution ~ p,
  body.book-{slug} .book-body > #attribution ~ ul,
  body.book-{slug} .book-body > #attribution ~ ol {{ font-size: 0.8rem; line-height: 1.38; }}
}}
body.book-{slug} #title-block-header {{ display: none; }}
body.book-{slug} .visually-hidden {{
  position: absolute;
  width: 1px; height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}}
body.book-{slug} nav#TOC {{
  border: 1px solid var(--rule);
  padding: 0.85rem 1rem 1.1rem;
  margin: 1.5rem 0 2.5rem;
  max-height: min(38rem, calc(100vh - var(--banner) - 1.5rem));
  overflow: auto;
  font-size: 0.92rem;
  line-height: 1.35;
  font-style: normal;
  background: var(--bg);
  -webkit-overflow-scrolling: touch;
}}
body.book-{slug} nav#TOC .toc-chrome {{
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg);
  padding: 0 0 0.35rem;
  margin: 0 0 0.15rem;
}}
body.book-{slug} nav#TOC .toc-title {{
  font-size: 1.15rem;
  margin: 0 0 0.4rem;
  font-style: normal;
}}
body.book-{slug} nav#TOC .toc-filter {{
  width: 100%;
  box-sizing: border-box;
  margin: 0.35rem 0 0.45rem;
  padding: 0.4rem 0.55rem;
  border: 1px solid var(--rule);
  background: var(--bg);
  color: var(--fg);
  font: inherit;
}}
body.book-{slug} nav#TOC .toc-empty {{
  color: var(--muted);
  margin: 0 0 0.6rem;
}}
body.book-{slug} nav#TOC .toc-parts {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 0.85rem;
  margin: 0 0 0.35rem;
  font-size: 0.88rem;
  font-weight: 600;
}}
body.book-{slug} nav#TOC .toc-parts a {{ color: var(--accent); }}
body.book-{slug} nav#TOC ul {{
  list-style: none;
  margin: 0;
  padding: 0;
}}
body.book-{slug} nav#TOC li {{ margin: 0.12rem 0; }}
body.book-{slug} nav#TOC .toc-az,
body.book-{slug} nav#TOC .toc-regions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.7rem;
  margin: 0.2rem 0 0.6rem;
  font-size: 0.92em;
}}
body.book-{slug} nav#TOC details.toc-region {{
  margin: 0.25rem 0 0.45rem;
}}
body.book-{slug} nav#TOC details.toc-subsection {{
  margin: 0.3rem 0 0.5rem 0.7rem;
}}
body.book-{slug} nav#TOC details.toc-subsection > ul {{
  margin: 0.15rem 0 0.35rem 1rem;
}}
body.book-{slug} nav#TOC details.toc-region summary {{
  font-weight: 600;
}}
body.book-{slug} nav#TOC li.toc-country > a {{ font-weight: 600; }}
body.book-{slug} nav#TOC .toc-orphan {{
  color: var(--muted);
  font-weight: 600;
}}
body.book-{slug} nav#TOC ul.toc-cities {{
  margin: 0.15rem 0 0.4rem 0.9rem;
  padding: 0;
}}
body.book-{slug} nav#TOC ul.toc-cities li {{
  margin: 0.06rem 0;
  font-weight: 400;
}}
body.book-{slug} nav#TOC a {{
  color: inherit;
  text-decoration: none;
}}
body.book-{slug} nav#TOC a:hover {{ color: var(--accent); }}
body.book-{slug} nav#TOC a.is-current {{
  color: var(--accent);
  font-weight: 700;
}}
body.book-{slug} nav#TOC details.toc-part {{ margin: 0.35rem 0 0.55rem; }}
body.book-{slug} nav#TOC summary {{
  cursor: pointer;
  font-weight: 600;
  color: var(--accent2);
  font-style: normal;
}}
body.book-{slug} nav#TOC summary a {{
  color: inherit;
  text-decoration: none;
}}
body.book-{slug} nav#TOC .toc-solo {{
  margin: 0.45rem 0;
  font-weight: 600;
}}
body.book-{slug} .book-body h1[id],
body.book-{slug} nav#TOC {{
  scroll-margin-top: calc(var(--banner) + 0.5rem);
}}
body.book-{slug} nav#TOC .toc-count {{
  color: var(--muted);
  font-weight: 400;
  font-size: 0.82em;
}}
body.book-{slug} nav#TOC .toc-az {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.15rem 0.45rem;
  margin: 0.45rem 0 0.55rem;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
}}
body.book-{slug} nav#TOC .toc-az a {{ color: var(--accent); }}
body.book-{slug} .toc-jump {{
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 6;
  background: var(--cover-bg);
  color: var(--cover-fg);
  border: 1px solid currentColor;
  padding: 0.35rem 0.7rem;
  text-decoration: none;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-family: {t["fallback"]};
}}
body.book-{slug} .book-banner {{
  position: sticky;
  top: 0;
  z-index: 20;
  background: {t["cover_bg"]};
  color: {t["cover_fg"]};
  margin: 0 -1.25rem 0;
  padding: 0.75rem 1.25rem 0.8rem;
  font-size: 0.78rem;
  letter-spacing: 0.03em;
}}
body.book-{slug} .book-banner-inner {{
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  min-height: 2.7rem;
}}
body.book-{slug} .book-banner-title {{
  display: flex;
  align-items: baseline;
  flex: 1 1 auto;
  min-width: 0;
  gap: 0.7rem;
  line-height: 1.15;
}}
body.book-{slug} .book-banner-site {{
  flex: 0 0 auto;
  color: inherit;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  opacity: 0.72;
  text-decoration: none;
  text-transform: uppercase;
}}
body.book-{slug} .book-banner-book-title {{
  flex: 1 1 auto;
  min-width: 0;
  overflow: visible;
  color: inherit;
  font-family: "{t["display"]}", {t["fallback"]};
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-style: normal;
  font-weight: 700;
  letter-spacing: -0.015em;
  overflow-wrap: normal;
  text-overflow: clip;
  white-space: normal;
}}
body.book-{slug} .book-banner-version {{
  flex: 0 0 auto;
  color: inherit;
  font-size: 0.55rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  opacity: 0.42;
}}
body.book-{slug} .book-banner-actions {{
  display: flex;
  align-items: baseline;
  flex: 0 0 auto;
  gap: 1rem;
  min-width: 0;
  white-space: nowrap;
}}
body.book-{slug} .book-banner-contents {{ flex: 0 0 auto; }}
body.book-{slug} .book-banner-utility {{
  display: flex;
  flex: 0 0 auto;
  flex-direction: column;
  gap: 0.25rem;
  margin-left: auto;
}}
body.book-{slug} .book-banner-project,
body.book-{slug} .book-banner-downloads {{
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
  white-space: nowrap;
}}
body.book-{slug} .book-banner-actions a {{
  color: inherit;
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  opacity: 0.62;
  text-decoration: none;
  text-transform: uppercase;
}}
body.book-{slug} .book-banner-actions a:hover,
body.book-{slug} .book-banner-actions a:focus-visible {{
  opacity: 1;
  text-decoration: underline;
}}
body.book-{slug} .book-banner a {{ color: inherit; }}
body.book-{slug} .book-banner a.github {{
  display: inline-flex;
  align-items: center;
  vertical-align: -0.15em;
  text-decoration: none;
}}
body.book-{slug} .book-banner a.github svg {{ width: 1.1em; height: 1.1em; display: block; }}
@media (max-width: 56rem) {{
  body.book-{slug} .book-banner-inner {{
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 0.55rem 1rem;
  }}
  body.book-{slug} .book-banner-title {{ width: 100%; }}
  body.book-{slug} .book-banner-site,
  body.book-{slug} .book-banner-version {{ flex-shrink: 1; }}
  body.book-{slug} .book-banner-actions {{ width: 100%; max-width: 100%; }}
}}
@media (min-width: 56rem) {{
  body.book-{slug} {{
    max-width: min(100%, calc(var(--toc) + var(--measure) + 5.5rem));
    padding-bottom: 0;
  }}
  body.book-{slug} .book-layout {{
    display: grid;
    grid-template-columns: var(--toc) minmax(0, var(--measure));
    column-gap: 2rem;
    align-items: start;
  }}
  body.book-{slug} nav#TOC {{
    position: sticky;
    top: var(--banner);
    z-index: 15;
    align-self: start;
    height: calc(100vh - var(--banner));
    max-height: calc(100vh - var(--banner));
    margin: 0;
    overflow: auto;
  }}
  body.book-{slug} .book-body {{
    min-width: 0;
    padding-bottom: 5rem;
  }}
  body.book-{slug} .toc-jump {{ display: none; }}
}}
@media (min-width: 78rem) {{
  body.book-{slug} {{ --toc: 22rem; }}
}}
{extra}
{drop}

body.book-{slug} .cover-page {{
  margin: 0 -1.25rem 3rem;
  min-height: 22rem;
  padding: 2.2rem 1.8rem 1.8rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: var(--cover-bg);
  color: var(--cover-fg);
  position: relative;
  overflow: hidden;
}}
body.book-{slug} .cover-logo-wrap {{
  margin: 0 0 1.2rem;
  position: relative;
  z-index: 2;
}}
body.book-{slug} .cover-logo-title {{
  align-items: flex-start;
  display: flex;
  gap: 0.5rem;
}}
body.book-{slug} .cover-logo {{
  display: block;
  max-height: {logo_max_h};
  max-width: {logo_max};
  width: auto;
  height: auto;
  object-fit: contain;
}}
body.book-{slug} .cover-kicker {{
  font-family: "{t["body"]}", {t["fallback"]};
  font-style: normal;
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  margin: 0;
  opacity: 0.86;
}}
body.book-{slug} .cover-title {{
  font-size: 3.4rem;
  margin: 0 0 0.6rem;
  color: inherit;
  font-style: {cover_italic};
}}
body.book-{slug} .cover-version {{
  font-family: "{t["body"]}", {t["fallback"]};
  font-size: 0.24em;
  font-style: normal;
  font-weight: 600;
  letter-spacing: 0.04em;
  vertical-align: top;
  white-space: nowrap;
}}
body.book-{slug} .cover-logo-title .cover-version {{
  font-size: 0.78rem;
}}
body.book-{slug} .cover-sub {{
  margin: 0;
  font-size: 1.05rem;
  max-width: 22rem;
  opacity: 0.9;
}}
body.book-{slug} .cover-foot {{
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
{photo_css}
@media print {{
  @page {{ margin: 1.4cm; }}
  @page:first {{ margin: 0; }}
  body.book-{slug} {{
    max-width: none;
    background: white;
    display: block;
    padding: 0;
  }}
  body.book-{slug} h1 + p::first-letter {{
    float: none;
    font: inherit;
    padding: 0;
    color: inherit;
  }}
  body.book-{slug} .book-banner,
  body.book-{slug} .toc-jump,
  body.book-{slug} .chapter-edit,
  body.book-{slug} nav#TOC .toc-filter-wrap,
  body.book-{slug} nav#TOC .toc-empty {{ display: none; }}
  body.book-{slug} .book-layout {{ display: block; }}
  body.book-{slug} nav#TOC {{
    position: static;
    max-height: none;
    height: auto;
    overflow: visible;
    break-after: page;
    margin: 0 0 2rem;
  }}
  body.book-{slug} .cover-page {{
    width: 100%;
    height: 100vh;
    min-height: 100vh;
    break-after: page;
    margin: 0;
  }}
}}
"""


def catalog_css() -> str:
    cards = []
    for slug, t in THEMES.items():
        cards.append(
            f"""article.card-{slug} {{
  background: {t["bg"]};
  color: {t["fg"]};
  border-color: {t["accent"]};
}}
article.card-{slug} a {{ color: {t["accent"]}; }}
article.card-{slug} .badge {{ border-color: {t["accent"]}; }}
"""
        )
    return (f"""
@font-face {{
  font-family: "Source Serif 4";
  src: url("fonts/SourceSerif4-Regular.ttf") format("truetype");
  font-weight: 400;
  font-display: swap;
}}
@font-face {{
  font-family: "Source Serif 4";
  src: url("fonts/SourceSerif4-Semibold.ttf") format("truetype");
  font-weight: 600;
  font-display: swap;
}}
@font-face {{
  font-family: "Oswald";
  src: url("fonts/Oswald-Bold.ttf") format("truetype");
  font-weight: 700;
  font-display: swap;
}}
html {{ overflow-x: clip; }}
html, body {{
  margin: 0;
  background: #fbf7e9;
  color: #5b2b08;
  font-family: "Source Serif 4", Palatino, Georgia, serif;
}}
body.catalog {{
  box-sizing: border-box;
  width: 100%;
  max-width: 72rem;
  margin: 0 auto;
  padding: 1.75rem clamp(1rem, 5vw, 2.5rem) 2.5rem;
  overflow-wrap: anywhere;
}}
body.catalog * {{ box-sizing: border-box; }}
body.catalog h1 {{
  display: flex;
  align-items: flex-start;
  gap: 0.25rem;
  font-family: "Oswald", Impact, "Arial Narrow", sans-serif;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  font-weight: 700;
  letter-spacing: 0.025em;
  margin: 0 0 1.5rem;
  color: #6e3100;
  position: relative;
  height: 6.5rem;
  z-index: 0;
}}
body.catalog .masthead-logo {{
  display: block;
  flex: none;
  height: 6.5rem;
  position: relative;
  width: 13.25rem;
}}
body.catalog .masthead-logo img {{
  display: block;
  height: 14rem;
  max-width: none;
  position: absolute;
  inset: 0 auto auto 0;
  width: auto;
  -webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 30%, transparent 88%);
  mask-image: linear-gradient(to bottom, #000 0%, #000 30%, transparent 88%);
}}
body.catalog .masthead-title {{
  line-height: 1;
  margin-top: 0.85rem;
  position: relative;
  z-index: 1;
}}
body.catalog .masthead-version {{
  align-self: flex-start;
  font-size: 0.45em;
  line-height: 1;
  margin-top: 0.95rem;
  position: relative;
  z-index: 1;
}}
body.catalog .lang {{
  position: relative;
  z-index: 1;
}}
.nostr-action {{
  max-width: 46rem;
  margin: 2.5rem 0 0;
  padding: 1rem 1.1rem;
  border: 1px solid #d8c7ac;
  background: #fffdf8;
}}
.nostr-action h2 {{ margin: 0 0 0.3rem; font-size: 1.2rem; }}
.nostr-action p {{ margin: 0.45rem 0 0; color: #76563c; line-height: 1.45; }}
.nostr-controls {{
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.65rem;
  margin-top: 0.75rem;
}}
.nostr-controls label {{
  display: grid;
  gap: 0.2rem;
  color: #76563c;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.nostr-controls select {{
  min-height: 2.55rem;
  padding: 0.55rem 1.9rem 0.55rem 0.65rem;
  border: 1px solid #d8c7ac;
  background: #fffdf8;
  color: #2e2119;
  font: inherit;
}}
.nostr-action button {{
  padding: 0.62rem 0.78rem;
  border: 1px solid #6e3100;
  border-radius: 0;
  background: #6e3100;
  color: #fffdf8;
  font: inherit;
  cursor: pointer;
}}
.nostr-action button:disabled {{ cursor: wait; opacity: 0.65; }}
.nostr-action button:focus {{ outline: 3px solid #d8a96b; outline-offset: 2px; }}
.nostr-action a {{ color: #6e3100; }}
.nostr-status,.nostr-reader {{ font-size: 0.8rem; }}
body.catalog .lede {{
  color: #76563c;
  line-height: 1.5;
  margin: 1.5rem 0 0;
  white-space: nowrap;
}}
@media (max-width: 40rem) {{
  body.catalog h1 {{ height: 5.25rem; }}
  body.catalog .masthead-logo {{ height: 5.25rem; width: 10.25rem; }}
  body.catalog .masthead-logo img {{ height: 10.85rem; }}
  body.catalog .masthead-title {{ margin-top: 0.55rem; }}
  body.catalog .masthead-version {{ margin-top: 0.65rem; }}
  body.catalog .lede {{ white-space: normal; }}
}}
body.catalog .lang + .lang {{
  margin-top: 2.5rem;
}}
body.catalog .lang-label {{
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 1rem;
  color: #6e3100;
}}
.grid {{
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}}
@media (min-width: 720px) {{
  .grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
}}
.card {{
  border: 2px solid;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  overflow: hidden;
  position: relative;
}}
.card .open {{
  position: absolute;
  inset: 0;
  z-index: 1;
}}
.card .formats,
.card .wiki-book {{ position: relative; z-index: 2; }}
.card .formats a,
.card .wiki-book a {{ position: relative; z-index: 2; }}
.card > a.cover {{
  display: block;
  flex: none;
  aspect-ratio: 148 / 210;
  overflow: hidden;
  line-height: 0;
  background: #222;
}}
.card .cover img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.card .card-body {{ padding: 0.75rem 0.85rem 0.9rem; }}
.card h2 {{ font-size: 1.05rem; margin: 0 0 0.3rem; line-height: 1.2; }}
.card h2 a {{ text-decoration: none; }}
.card .kicker {{
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 0 0 0.25rem;
  opacity: 0.75;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.card .site-logo {{
  display: block;
  max-height: 2.4rem;
  max-width: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  margin: 0 0 0.45rem;
  background: transparent;
  aspect-ratio: auto;
}}
.badge {{
  display: inline-block;
  border: 1px solid;
  padding: 0.1rem 0.35rem;
  font-size: 0.62rem;
  letter-spacing: 0.04em;
}}
.card .formats {{ margin: 0; font-size: 0.75rem; text-align: center; }}
.card .wiki-book {{ margin: 0.4rem 0 0; font-size: 0.72rem; text-align: center; }}
.foot {{ margin-top: 1.5rem; color: #76563c; font-size: 0.75rem; text-align: right; }}
.foot a {{ color: #6e3100; }}
.foot .github {{
  display: inline-flex;
  align-items: center;
  vertical-align: -0.15em;
  margin: 0 0.15em;
  color: #6e3100;
  text-decoration: none;
}}
.foot .github svg {{ width: 1em; height: 1em; display: block; }}
{"".join(cards)}
""".strip() + "\n")


def write_css_files() -> None:
    themes = ROOT / "assets" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    for slug in THEMES:
        (themes / f"{slug}.css").write_text(book_css(slug), encoding="utf-8")
    (ROOT / "assets" / "catalog.css").write_text(catalog_css(), encoding="utf-8")
    epub_bits = []
    for slug, t in THEMES.items():
        epub_bits.append(
            f"body.book-{slug} {{ font-family: {t['fallback']}; color: {t['fg']}; }}\n"
            f"body.book-{slug} h1, body.book-{slug} h2 {{ font-family: {t['fallback']}; }}\n"
        )
    (ROOT / "assets" / "epub.css").write_text(
        "img { max-width: 100%; height: auto; }\n" + "\n".join(epub_bits),
        encoding="utf-8",
    )

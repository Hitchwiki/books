"""Per-book visual identity: color, type, cover motif.

CSS and JPEG covers are generated from this file (scripts/render_covers.py).
"""

from __future__ import annotations

from pathlib import Path

from common import ROOT

THEMES: dict[str, dict] = {
    "hitchhikers-guide": {
        "motif": "horizon",
        "bg": "#f3ead7",
        "fg": "#1c1710",
        "muted": "#5c5348",
        "accent": "#c45c26",
        "accent2": "#1e3a5f",
        "rule": "#c9bba3",
        "cover_fg": "#f3ead7",
        "cover_bg": "#1e3a5f",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": 'Palatino, "Palatino Linotype", Georgia, serif',
        "measure": "38rem",
        "kicker": "A hitchhiker’s handbook",
    },
    "dumpster-diving": {
        "motif": "hazard",
        "bg": "#14160f",
        "fg": "#ece9d8",
        "muted": "#a39e88",
        "accent": "#e2c93a",
        "accent2": "#ece9d8",
        "rule": "#3a3c32",
        "cover_fg": "#14160f",
        "cover_bg": "#e2c93a",
        "display": "Oswald",
        "display_file": "Oswald-Bold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "40rem",
        "kicker": "From Trashwiki",
    },
    "random-roads": {
        "motif": "masthead",
        "bg": "#f6efe2",
        "fg": "#261c14",
        "muted": "#6b5748",
        "accent": "#8b2e1f",
        "accent2": "#261c14",
        "rule": "#d7c4a8",
        "cover_fg": "#261c14",
        "cover_bg": "#f6efe2",
        "display": "Playfair Display",
        "display_file": "PlayfairDisplay-Bold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": 'Georgia, "Times New Roman", serif',
        "measure": "36rem",
        "kicker": "A magazine of independent travel",
    },
    "dumpsterdam": {
        "motif": "slab",
        "bg": "#fff6ea",
        "fg": "#1a120c",
        "muted": "#6a5344",
        "accent": "#e05915",
        "accent2": "#1f4d3a",
        "rule": "#ead7c2",
        "cover_fg": "#fff6ea",
        "cover_bg": "#e05915",
        "display": "Oswald",
        "display_file": "Oswald-Bold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "40rem",
        "kicker": "Voedselactivisme uit Amsterdam",
    },
    "hospitality-exchange": {
        "motif": "door",
        "bg": "#fbf6ef",
        "fg": "#2c241c",
        "muted": "#6e6258",
        "accent": "#3d6b66",
        "accent2": "#c4785a",
        "rule": "#e4d8c8",
        "cover_fg": "#fbf6ef",
        "cover_bg": "#3d6b66",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Serif 4",
        "body_file": "SourceSerif4-Regular.ttf",
        "body_bold": "SourceSerif4-Bold.ttf",
        "fallback": "Georgia, Palatino, serif",
        "measure": "38rem",
        "kicker": "Networks of hosts and guests",
    },
    "moneyless": {
        "motif": "spare",
        "bg": "#f7f7f5",
        "fg": "#161616",
        "muted": "#5c5c5c",
        "accent": "#b42318",
        "accent2": "#161616",
        "rule": "#ddddd8",
        "cover_fg": "#161616",
        "cover_bg": "#f7f7f5",
        "display": "IBM Plex Serif",
        "display_file": "IBMPlexSerif-Regular.ttf",
        "body": "IBM Plex Sans",
        "body_file": "IBMPlexSans-Regular.ttf",
        "body_bold": "IBMPlexSans-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "34rem",
        "kicker": "Life without money",
    },
    "shoestring-nomad": {
        "motif": "grid",
        "bg": "#efe6d4",
        "fg": "#2a261c",
        "muted": "#6a6456",
        "accent": "#3d5a73",
        "accent2": "#8a5a32",
        "rule": "#d4c8b0",
        "cover_fg": "#efe6d4",
        "cover_bg": "#3d5a73",
        "display": "Source Serif 4",
        "display_file": "SourceSerif4-Semibold.ttf",
        "body": "Source Sans 3",
        "body_file": "SourceSans3-Regular.ttf",
        "body_bold": "SourceSans3-Bold.ttf",
        "fallback": '"Helvetica Neue", Helvetica, Arial, sans-serif',
        "measure": "40rem",
        "kicker": "From Nomadwiki",
    },
}

FONT_URLS = {
    "SourceSans3-Regular.ttf": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-sans@3.052R/release/TTF/SourceSans3-Regular.ttf",
    "SourceSans3-Bold.ttf": "https://cdn.jsdelivr.net/gh/adobe-fonts/source-sans@3.052R/release/TTF/SourceSans3-Bold.ttf",
    "Oswald-Bold.ttf": "https://github.com/googlefonts/OswaldFont/raw/main/fonts/ttf/Oswald-Bold.ttf",
    "PlayfairDisplay-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "IBMPlexSerif-Regular.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-serif/fonts/complete/ttf/IBMPlexSerif-Regular.ttf",
    "IBMPlexSans-Regular.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Regular.ttf",
    "IBMPlexSans-Bold.ttf": "https://github.com/IBM/plex/raw/master/packages/plex-sans/fonts/complete/ttf/IBMPlexSans-Bold.ttf",
}

FONT_URL_FALLBACKS = {
    "Oswald-Bold.ttf": ["https://github.com/google/fonts/raw/main/ofl/oswald/Oswald%5Bwght%5D.ttf"],
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


def cover_html(slug: str, meta: dict) -> str:
    t = THEMES[slug]
    title = meta.get("title", slug)
    sub = meta.get("subtitle", "")
    license_id = meta.get("license", "")
    return f"""<section class="cover-page" aria-label="Cover">
  <p class="cover-kicker">{t["kicker"]}</p>
  <div class="cover-main">
    <h1 class="cover-title">{title}</h1>
    <p class="cover-sub">{sub}</p>
    <p class="cover-read"><a href="#TOC">Read the book</a></p>
  </div>
  <p class="cover-foot">books.hitchwiki.org · {license_id}</p>
</section>
"""


def _font_faces(t: dict, prefix: str) -> str:
    faces = []
    seen: set[tuple[str, str]] = set()
    for family, name, weight in (
        (t["display"], t.get("display_file"), "600"),
        (t["body"], t.get("body_file"), "400"),
        (t["body"], t.get("body_bold"), "700"),
    ):
        if not name or (family, name) in seen:
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
    "horizon": """
body.book-SLUG .cover-page::before {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 38%;
  height: 3px;
  background: var(--accent);
}
body.book-SLUG .cover-page::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 38%;
  background: #c45c26;
  opacity: 0.92;
}
body.book-SLUG .cover-foot { position: relative; z-index: 1; }
body.book-SLUG .cover-main { position: relative; z-index: 1; margin-bottom: 42%; }
""",
    "hazard": """
body.book-SLUG .cover-page {
  background: repeating-linear-gradient(-45deg, #e2c93a, #e2c93a 18px, #14160f 18px, #14160f 36px);
}
body.book-SLUG .cover-main {
  background: #14160f;
  color: #e2c93a;
  padding: 1.4rem 1.2rem;
}
body.book-SLUG .cover-title { color: #e2c93a; font-style: normal; text-transform: uppercase; }
body.book-SLUG .cover-kicker, body.book-SLUG .cover-foot {
  background: #14160f;
  color: #e2c93a;
  display: inline-block;
  padding: 0.3rem 0.5rem;
}
""",
    "masthead": """
body.book-SLUG .cover-page {
  border-top: 14px solid var(--accent);
  border-bottom: 14px solid var(--accent);
}
body.book-SLUG .cover-title {
  font-style: italic;
  border-bottom: 1px solid var(--fg);
  padding-bottom: 0.6rem;
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
  background:
    linear-gradient(#1f4d3a, #1f4d3a) left / 12px 100% no-repeat,
    var(--cover-bg);
}
""",
    "door": """
body.book-SLUG .cover-page {
  box-shadow: inset 0 0 0 14px var(--bg), inset 0 0 0 22px var(--accent2);
}
body.book-SLUG .cover-main { text-align: center; }
body.book-SLUG .cover-sub { margin-left: auto; margin-right: auto; }
body.book-SLUG .cover-kicker, body.book-SLUG .cover-foot { text-align: center; }
""",
    "spare": """
body.book-SLUG .cover-page { justify-content: flex-end; }
body.book-SLUG .cover-kicker { position: absolute; top: 2.2rem; left: 1.8rem; }
body.book-SLUG .cover-kicker::before {
  content: "";
  display: block;
  width: 2.2rem;
  height: 2.2rem;
  background: var(--accent);
  margin-bottom: 1.4rem;
}
body.book-SLUG .cover-title { font-style: normal; font-weight: 400; font-size: 2.6rem; }
""",
    "grid": """
body.book-SLUG .cover-page {
  background-image:
    linear-gradient(rgba(239,230,212,0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(239,230,212,0.08) 1px, transparent 1px);
  background-size: 28px 28px;
}
body.book-SLUG .cover-title { font-style: italic; }
body.book-SLUG .cover-page::after {
  content: "";
  position: absolute;
  left: 10%;
  right: 18%;
  top: 28%;
  height: 0;
  border-top: 2px dashed rgba(239,230,212,0.55);
  transform: rotate(-12deg);
}
""",
}


def book_css(slug: str, *, font_prefix: str = "fonts/") -> str:
    t = THEMES[slug]
    italic = "italic" if slug in {"hitchhikers-guide", "hospitality-exchange", "random-roads"} else "normal"
    dark = slug == "dumpster-diving"
    banner_bg = t["cover_bg"] if slug != "moneyless" else t["bg"]
    banner_fg = t["cover_fg"] if slug != "moneyless" else t["fg"]
    extra = MOTIF_CSS[t["motif"]].replace("SLUG", slug)
    drop = ""
    if slug == "random-roads":
        drop = """
body.book-random-roads h1 + p::first-letter {
  float: left;
  font-family: "Playfair Display", Georgia, serif;
  font-size: 3.4rem;
  line-height: 0.85;
  padding-right: 0.35rem;
  color: var(--accent);
}"""
    dark_extra = (
        f"body.book-{slug} {{ font-size: 1.02rem; letter-spacing: 0.01em; }}" if dark else ""
    )
    return f"""{_font_faces(t, font_prefix)}

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
  --toc: 22rem;
  background: var(--bg);
  color: var(--fg);
  font-family: "{t["body"]}", {t["fallback"]};
  max-width: var(--measure);
  margin: 0 auto;
  padding: 0 1.25rem 5rem;
  line-height: 1.58;
  font-size: 1.06rem;
  min-height: 100vh;
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
body.book-{slug} a {{ color: var(--accent); }}
body.book-{slug} hr {{ border: 0; border-top: 1px solid var(--rule); }}
body.book-{slug} img {{ max-width: 100%; height: auto; }}
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
  max-height: min(38rem, 78vh);
  overflow: auto;
  font-size: 0.92rem;
  line-height: 1.35;
  font-style: normal;
}}
body.book-{slug} nav#TOC .toc-title {{
  font-size: 1.15rem;
  margin: 0 0 0.4rem;
  font-style: normal;
}}
body.book-{slug} nav#TOC .toc-filter {{
  width: 100%;
  box-sizing: border-box;
  margin: 0.35rem 0 0.7rem;
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
body.book-{slug} nav#TOC ul {{
  list-style: none;
  margin: 0;
  padding: 0;
}}
body.book-{slug} nav#TOC li {{ margin: 0.12rem 0; }}
body.book-{slug} nav#TOC li.toc-letter {{ margin-top: 0.7rem; }}
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
body.book-{slug} .book-body h1[id] {{ scroll-margin-top: 0.8rem; }}
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
@media (min-width: 78rem) {{
  body.book-{slug} {{
    max-width: min(100%, calc(var(--toc) + var(--measure) + 3rem));
    display: grid;
    grid-template-columns: var(--toc) minmax(0, var(--measure));
    column-gap: 2.25rem;
    padding-bottom: 0;
  }}
  body.book-{slug} .book-banner,
  body.book-{slug} .cover-page {{
    grid-column: 1 / -1;
  }}
  body.book-{slug} nav#TOC {{
    position: sticky;
    top: 0;
    align-self: start;
    height: 100vh;
    max-height: 100vh;
    margin: 0;
    overflow: auto;
  }}
  body.book-{slug} .book-body {{
    min-width: 0;
    padding-bottom: 5rem;
  }}
  body.book-{slug} .toc-jump {{ display: none; }}
}}
body.book-{slug} .book-banner {{
  background: {banner_bg};
  color: {banner_fg};
  margin: 0 -1.25rem 0;
  padding: 0.85rem 1.25rem;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
}}
body.book-{slug} .book-banner a {{ color: inherit; text-decoration: underline; }}
{dark_extra}
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
body.book-{slug} .cover-read {{
  margin: 1.4rem 0 0;
  position: relative;
  z-index: 2;
}}
body.book-{slug} .cover-read a {{
  color: inherit;
  border: 1px solid currentColor;
  padding: 0.35rem 0.75rem;
  text-decoration: none;
  display: inline-block;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-style: normal;
  font-family: {t["fallback"]};
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
  font-style: {italic};
}}
body.book-{slug} .cover-sub {{
  margin: 0;
  font-size: 1.05rem;
  max-width: 22rem;
  opacity: 0.9;
}}
body.book-{slug} .cover-foot {{
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}
@media print {{
  body.book-{slug} {{ max-width: none; background: white; display: block; }}
  body.book-{slug} .book-banner,
  body.book-{slug} .toc-jump,
  body.book-{slug} nav#TOC .toc-filter-wrap,
  body.book-{slug} nav#TOC .toc-empty {{ display: none; }}
  body.book-{slug} nav#TOC {{
    position: static;
    max-height: none;
    height: auto;
    overflow: visible;
    break-after: page;
    margin: 0 0 2rem;
  }}
  body.book-{slug} .cover-page {{
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
article.card-{slug} .badge {{ border-color: {t["accent"]}; }}"""
        )
    serif = THEMES["hitchhikers-guide"]
    return f"""
@font-face {{
  font-family: "Source Serif 4";
  src: url("fonts/{serif["body_file"]}") format("truetype");
  font-weight: 400;
  font-display: swap;
}}
@font-face {{
  font-family: "Source Serif 4";
  src: url("fonts/{serif["display_file"]}") format("truetype");
  font-weight: 600;
  font-display: swap;
}}
html, body {{
  margin: 0;
  background: white;
  color: #1c1710;
  font-family: "Source Serif 4", Palatino, Georgia, serif;
}}
body.catalog {{
  max-width: 72rem;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 2rem;
}}
body.catalog h1 {{
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  font-weight: 600;
  margin: 0 0 0.4rem;
}}
body.catalog .lede {{
  max-width: 36rem;
  color: #5c564c;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}}
.grid {{
  display: grid;
  gap: 0.85rem;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
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
.card .formats {{ position: relative; z-index: 2; }}
.card .formats a {{ position: relative; z-index: 2; }}
.card img {{
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  display: block;
  background: #222;
}}
.card .card-body {{ padding: 0.65rem 0.7rem 0.75rem; }}
.card h2 {{ font-size: 0.95rem; margin: 0 0 0.25rem; line-height: 1.2; }}
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
.badge {{
  display: inline-block;
  border: 1px solid;
  padding: 0.1rem 0.35rem;
  font-size: 0.62rem;
  letter-spacing: 0.04em;
}}
.card .formats {{ margin: 0.45rem 0 0; font-size: 0.75rem; }}
.foot {{ margin-top: 1.5rem; color: #8a8680; font-size: 0.75rem; text-align: right; }}
.foot a {{ color: #6e6a64; }}
.foot .github {{
  display: inline-flex;
  align-items: center;
  vertical-align: -0.15em;
  margin: 0 0.15em;
  color: #6e6a64;
  text-decoration: none;
}}
.foot .github svg {{ width: 1em; height: 1em; display: block; }}
{"".join(cards)}
"""


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

"""Usable HTML table of contents: parts, search, A–Z, sticky nav."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

PART_LABELS = {
    "01-practice": "Practice",
    "02-countries": "Countries",
    "03-cities": "Cities",
    "03-history": "History",
    "03-software": "Software",
    "03-stories": "Stories",
    "04-outlook": "Outlook",
    "casa-robino": "Casa Robino",
    "en": "English",
    "nl": "Nederlands",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

GAZETTEER = {
    "02-countries",
    "03-cities",
    "03-stories",
    "casa-robino",
    "en",
    "nl",
    "es",
    "fr",
    "de",
}
HEADING = re.compile(r"^# (.+)$", re.M)
INTRO_STEM = re.compile(r"^\d{2}-")
ATTR = re.compile(r"\s*\{[^}]*\}\s*$")
H1_RE = re.compile(r"<h1\b([^>]*)>(.*?)</h1>", re.I | re.S)
NAV_RE = re.compile(r"<nav id=\"TOC\"[^>]*>.*?</nav>\s*", re.I | re.S)
QUOTES = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
    }
)


def normalize(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").translate(QUOTES)
    text = re.sub(r"[-–—−]+", "-", text)
    text = re.sub(r"\s+", " ", text).strip().casefold()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s-]+", " ", text).strip()


def chapter_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = HEADING.search(text)
    title = m.group(1).strip() if m else path.stem.replace("-", " ").title()
    return ATTR.sub("", title).strip()


def is_part_intro(src: Path, path: Path) -> bool:
    rel = path.relative_to(src)
    return len(rel.parts) == 1 and bool(INTRO_STEM.match(path.stem))


def chapter_part(src: Path, path: Path) -> str:
    rel = path.relative_to(src)
    if len(rel.parts) == 1:
        return path.stem if INTRO_STEM.match(path.stem) else ""
    return rel.parts[0]


def part_label(part: str) -> str:
    if not part:
        return "This edition"
    if part in PART_LABELS:
        return PART_LABELS[part]
    return part.replace("-", " ").strip("0123456789 ").title() or part


def letter_key(title: str) -> str:
    for ch in title.strip():
        if ch.isalpha():
            return ch.upper()
    return "0"


def html_h1s(doc: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in H1_RE.finditer(doc):
        attrs, inner = m.group(1), m.group(2)
        if "cover-title" in attrs or re.search(r'\bclass="[^"]*\btitle\b', attrs):
            continue
        idm = re.search(r'\bid="([^"]+)"', attrs)
        if not idm:
            continue
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", inner))).strip()
        if text:
            out.append((idm.group(1), text))
    return out


def toc_entries(chapters: list[Path], doc: str, src: Path) -> list[dict]:
    headings = html_h1s(doc)
    i = 0
    entries: list[dict] = []
    for path in chapters:
        part = chapter_part(src, path)
        title = chapter_title(path)
        want = normalize(title)
        if path.name.startswith("00-frontmatter"):
            while i < len(headings) and normalize(headings[i][1]) == want:
                i += 1
            continue
        found = None
        j = i
        while j < len(headings):
            if normalize(headings[j][1]) == want:
                found = headings[j]
                i = j + 1
                break
            j += 1
        if found is None:
            continue
        hid, heading = found
        entries.append(
            {
                "part": part,
                "title": heading,
                "href": hid,
                "intro": is_part_intro(src, path),
            }
        )
    return entries


def _az_links(part: str, items: list[dict]) -> str:
    letters = []
    seen: set[str] = set()
    for item in items:
        key = letter_key(item["title"])
        if key not in seen:
            seen.add(key)
            letters.append(key)
    bits = []
    slug = html.escape(part or "part")
    for key in letters:
        letter = html.escape(key)
        bits.append(f'<a href="#toc-{slug}-{letter}">{letter}</a>')
    return f'<p class="toc-az">{"".join(bits)}</p>'


def _item_list(part: str, items: list[dict], *, az: bool) -> str:
    rows = []
    last = None
    slug = html.escape(part or "part")
    for item in items:
        key = letter_key(item["title"])
        extra = ""
        if az and key != last:
            extra = f' id="toc-{slug}-{html.escape(key)}" class="toc-letter"'
            last = key
        href = html.escape(item["href"], quote=True)
        title = html.escape(item["title"])
        rows.append(f'<li{extra}><a href="#{href}">{title}</a></li>')
    return "<ul>\n" + "\n".join(rows) + "\n</ul>"


def render_toc(entries: list[dict]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    order: list[str] = []
    for item in entries:
        part = item["part"]
        if part not in groups:
            order.append(part)
        groups[part].append(item)
    chunks = [
        '<nav id="TOC" role="doc-toc" aria-label="Table of contents">',
        '<h2 class="toc-title">Contents</h2>',
        '<label class="toc-filter-wrap"><span class="visually-hidden">Filter chapters</span>',
        '<input class="toc-filter" type="search" placeholder="Find a chapter…" autocomplete="off"></label>',
        '<p class="toc-empty" hidden>No matching chapters.</p>',
    ]
    for part in order:
        items = groups[part]
        intro = next((x for x in items if x.get("intro")), None)
        chapters = [x for x in items if not x.get("intro")]
        n = len(chapters)
        label = html.escape((intro["title"] if intro else part_label(part)))
        if intro and not chapters:
            href = html.escape(intro["href"], quote=True)
            chunks.append(f'<p class="toc-solo"><a href="#{href}">{label}</a></p>')
            continue
        collapse = ""
        if part in GAZETTEER and n >= 20:
            collapse = ' data-collapse="true"'
        elif n >= 80:
            collapse = ' data-collapse="true"'
        az = n >= (24 if part in GAZETTEER else 80)
        pid = html.escape(part or "front")
        summary = label
        if intro:
            href = html.escape(intro["href"], quote=True)
            summary = f'<a href="#{href}">{label}</a>'
        chunks.append(
            f'<details class="toc-part" data-part="{pid}"{collapse} open>'
            f'<summary>{summary} <span class="toc-count">{n}</span></summary>'
        )
        if az:
            chunks.append(_az_links(part or "front", chapters))
        chunks.append(_item_list(part or "front", chapters, az=az))
        chunks.append("</details>")
    chunks.append("</nav>")
    return "\n".join(chunks)


def wrap_body(html_doc: str, toc: str) -> str:
    html_doc = NAV_RE.sub("", html_doc, count=1)
    already = 'class="book-body"' in html_doc
    insertion = toc + '\n<article class="book-body">\n'
    if not already:
        if re.search(r'<header id="title-block-header">', html_doc):
            html_doc = re.sub(
                r'(<header id="title-block-header">.*?</header>\s*)',
                lambda m: m.group(1) + insertion,
                html_doc,
                count=1,
                flags=re.S,
            )
        elif "</section>" in html_doc:
            html_doc = html_doc.replace("</section>", "</section>\n" + insertion, 1)
        else:
            html_doc = re.sub(r"(<body[^>]*>)", r"\1\n" + insertion, html_doc, count=1)
        html_doc = html_doc.replace(
            "</body>",
            '</article>\n<a class="toc-jump" href="#TOC">Contents</a>\n'
            '<script src="book.js"></script>\n</body>',
            1,
        )
    else:
        html_doc = re.sub(
            r'(<header id="title-block-header">.*?</header>\s*)',
            lambda m: m.group(1) + toc + "\n",
            html_doc,
            count=1,
            flags=re.S,
        )
        if "book.js" not in html_doc:
            html_doc = html_doc.replace(
                "</body>",
                '<script src="book.js"></script>\n</body>',
                1,
            )
    banner = re.search(r'<header class="book-banner">.*?</header>', html_doc, flags=re.S)
    if banner and 'href="#TOC">Contents</a>' not in banner.group(0):
        html_doc = html_doc.replace(
            banner.group(0),
            banner.group(0).replace("</p></header>", ' · <a href="#TOC">Contents</a></p></header>', 1),
            1,
        )
    return html_doc


def enhance_html(html_doc: str, chapters: list[Path], src: Path) -> str:
    entries = toc_entries(chapters, html_doc, src)
    expected = sum(1 for p in chapters if not p.name.startswith("00-frontmatter"))
    if len(entries) != expected:
        print(f"  toc: matched {len(entries)}/{expected} chapters", flush=True)
    return wrap_body(html_doc, render_toc(entries))

"""Usable HTML table of contents: parts, search, A–Z, sticky nav."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

from common import github_icon_link, wiki_edit_url
from ui_strings import ui_strings

PART_LABELS = {
    "01-practice": "Practice",
    "02-countries": "Places",
    "02-networks": "Networks",
    "03-countries": "Places",
    "03-history": "History",
    "03-resources": "Resources",
    "03-software": "Software",
    "03-stories": "Stories",
    "04-future": "Future",
    "04-outlook": "Outlook",
    "en": "English",
    "nl": "Nederlands",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
}

GAZETTEER = {
    "02-countries",
    "03-countries",
    "03-stories",
    "en",
    "nl",
    "es",
    "fr",
    "de",
}
LANGUAGE_PARTS = {"en", "nl", "es", "fr", "de"}
HEADING = re.compile(r"^# (.+)$", re.M)
INTRO_STEM = re.compile(r"^\d{2}-")
ATTR = re.compile(r"\s*\{[^}]*\}\s*$")
SOURCE_LINK = re.compile(
    r"^Source:\s*(?:\[[^]]+\]\((https?://[^)\s]+)\)|<?(https?://[^>\s]+)>?)",
    re.I | re.M,
)
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


def chapter_edit_url(path: Path) -> str | None:
    match = SOURCE_LINK.search(path.read_text(encoding="utf-8"))
    if not match:
        return None
    return wiki_edit_url(match.group(1) or match.group(2))


def is_part_intro(src: Path, path: Path) -> bool:
    rel = path.relative_to(src)
    return len(rel.parts) == 1 and bool(INTRO_STEM.match(path.stem))


def chapter_part(src: Path, path: Path) -> str:
    rel = path.relative_to(src)
    if len(rel.parts) == 1:
        return path.stem if INTRO_STEM.match(path.stem) else ""
    return rel.parts[0]


def editorial_parts(src: Path) -> dict[str, tuple[str, str]]:
    """Optional [Part name] sections in editorial/order.txt."""
    order = src.parent / "editorial" / "order.txt"
    if not order.exists():
        return {}
    out: dict[str, tuple[str, str]] = {}
    part_id = part_name = ""
    for raw in order.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        section = re.fullmatch(r"\[([^]]+)\]", line)
        if section:
            part_name = section.group(1).strip()
            part_id = re.sub(r"[^a-z0-9]+", "-", part_name.casefold()).strip("-")
        elif line and not line.startswith("#") and part_id:
            out[line] = (part_id, part_name)
    return out


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
    custom_parts = editorial_parts(src)
    i = 0
    entries: list[dict] = []
    for path in chapters:
        rel = path.relative_to(src)
        custom_part = custom_parts.get(rel.as_posix())
        part = custom_part[0] if custom_part else chapter_part(src, path)
        part_name = custom_part[1] if custom_part else part_label(part)
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
        parent = rel.parts[1] if len(rel.parts) >= 3 else None
        entries.append(
            {
                "part": part,
                "part_name": part_name,
                "path": rel.as_posix(),
                "title": heading,
                "href": hid,
                "intro": is_part_intro(src, path),
                "region": path.stem.startswith("_"),
                "parent": parent,
                "slug": path.stem,
                "edit_url": chapter_edit_url(path),
            }
        )
    return entries


def _region_links(items: list[dict]) -> str:
    bits = []
    for item in items:
        if not item.get("region"):
            continue
        href = html.escape(item["href"], quote=True)
        title = html.escape(item["title"])
        bits.append(f'<a href="#{href}">{title}</a>')
    if not bits:
        return ""
    return f'<p class="toc-regions">{"".join(bits)}</p>'


def _region_blocks(part: str, items: list[dict]) -> str:
    chunks = [_region_links(items)]
    current = None
    buf: list[dict] = []

    def flush() -> None:
        if current is None and not buf:
            return
        label = html.escape(current["title"]) if current else "Places"
        href = html.escape(current["href"], quote=True) if current else ""
        summary = f'<a href="#{href}">{label}</a>' if href else label
        collapse = ' data-collapse="true"'
        n = sum(1 for x in buf if not x.get("parent"))
        chunks.append(
            f'<details class="toc-region" data-part="{html.escape(part)}" {collapse} open>'
            f'<summary>{summary} <span class="toc-count">{n}</span></summary>'
        )
        if buf:
            chunks.append(_item_list(part, buf, az=False))
        chunks.append("</details>")

    for item in items:
        if item.get("region"):
            if current is not None or buf:
                flush()
            current = item
            buf = []
            continue
        buf.append(item)
    flush()
    return "\n".join(c for c in chunks if c)


def _az_links(part: str, items: list[dict]) -> str:
    letters = []
    seen: set[str] = set()
    for item in items:
        if item.get("parent") and item.get("parent") != item.get("slug"):
            continue
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


def _li_open(item: dict, extra: str = "") -> str:
    href = html.escape(item["href"], quote=True)
    title = html.escape(item["title"])
    return f'<li{extra}><a href="#{href}">{title}</a>'


def _city_items(cities: list[dict]) -> str:
    rows = []
    for city in cities:
        href = html.escape(city["href"], quote=True)
        title = html.escape(city["title"])
        rows.append(f'<li><a href="#{href}">{title}</a></li>')
    return '<ul class="toc-cities">\n' + "\n".join(rows) + "\n</ul>"


def _item_list(part: str, items: list[dict], *, az: bool) -> str:
    rows = []
    last = None
    slug = html.escape(part or "part")
    i = 0

    def letter_attrs(title: str) -> tuple[str, list[str]]:
        nonlocal last
        classes: list[str] = []
        extra_id = ""
        if az:
            key = letter_key(title)
            if key != last:
                extra_id = f' id="toc-{slug}-{html.escape(key)}"'
                classes.append("toc-letter")
                last = key
        return extra_id, classes

    while i < len(items):
        item = items[i]
        parent = item.get("parent")
        if parent and parent != item.get("slug"):
            group = [item]
            j = i + 1
            while j < len(items) and items[j].get("parent") == parent:
                group.append(items[j])
                j += 1
            label = parent.replace("-", " ").title()
            extra_id, classes = letter_attrs(label)
            cls = " ".join(["toc-country", *classes]).strip()
            rows.append(
                f'<li{extra_id} class="{html.escape(cls)}">'
                f'<span class="toc-orphan">{html.escape(label)}</span>'
                + _city_items(group)
                + "</li>"
            )
            i = j
            continue
        extra_id, classes = letter_attrs(item["title"])
        cities = []
        j = i + 1
        while j < len(items) and items[j].get("parent") == item.get("slug"):
            cities.append(items[j])
            j += 1
        if cities:
            classes.append("toc-country")
        cls = f' class="{" ".join(classes)}"' if classes else ""
        row = _li_open(item, f"{extra_id}{cls}")
        if cities:
            row += _city_items(cities)
        rows.append(row + "</li>")
        i = j if cities else i + 1
    return "<ul>\n" + "\n".join(rows) + "\n</ul>"


def render_toc(entries: list[dict], labels: dict[str, str]) -> str:
    groups: dict[str, list[dict]] = defaultdict(list)
    order: list[str] = []
    for item in entries:
        part = item["part"]
        if part not in groups:
            order.append(part)
        groups[part].append(item)
    chunks = [
        f'<nav id="TOC" role="doc-toc" aria-label="{labels["table_of_contents"]}">',
        '<div class="toc-chrome">',
        f'<h2 class="toc-title">{labels["contents"]}</h2>',
        f'<label class="toc-filter-wrap"><span class="visually-hidden">{labels["filter_chapters"]}</span>',
        f'<input class="toc-filter" type="search" placeholder="{labels["find_chapter"]}" autocomplete="off"></label>',
        f'<p class="toc-empty" hidden>{labels["no_matching_chapters"]}</p>',
    ]
    single_language = len(order) == 1 and order[0] in LANGUAGE_PARTS
    if not single_language:
        jumps = []
        for part in order:
            items = groups[part]
            intro = next((x for x in items if x.get("intro")), None)
            first = intro or (items[0] if items else None)
            if not first:
                continue
            raw = intro["title"] if intro else items[0].get("part_name", part_label(part))
            m = re.match(r"^(Part [IVXLCDM]+)(?:\s+[—–-]\s+.+)?$", raw)
            short = m.group(1) if m else part_label(part)
            href = html.escape(first["href"], quote=True)
            pid = html.escape(part or "front")
            jumps.append(
                f'<a href="#{href}" data-part="{pid}">{html.escape(short)}</a>'
            )
        if jumps:
            chunks.append(f'<p class="toc-parts">{"".join(jumps)}</p>')
    chunks.append("</div>")
    for part in order:
        items = groups[part]
        intro = next((x for x in items if x.get("intro")), None)
        chapters = [x for x in items if not x.get("intro")]
        n = len([x for x in chapters if not x.get("region")])
        label = html.escape(
            intro["title"] if intro else items[0].get("part_name", part_label(part))
        )
        if intro and not chapters:
            href = html.escape(intro["href"], quote=True)
            chunks.append(f'<p class="toc-solo"><a href="#{href}">{label}</a></p>')
            continue
        collapse = ' data-collapse="true"' if n >= 12 else ""
        by_region = any(x.get("region") for x in chapters)
        az = (not by_region) and n >= (24 if part in GAZETTEER else 80)
        pid = html.escape(part or "front")
        if single_language:
            if az:
                chunks.append(_az_links(part or "front", chapters))
            chunks.append(_item_list(part or "front", chapters, az=az))
            continue
        summary = label
        if intro:
            href = html.escape(intro["href"], quote=True)
            summary = f'<a href="#{href}">{label}</a>'
        chunks.append(
            f'<details class="toc-part" id="toc-part-{pid}" data-part="{pid}"{collapse} open>'
            f'<summary>{summary} <span class="toc-count">{n}</span></summary>'
        )
        if by_region:
            chunks.append(_region_blocks(part or "front", chapters))
        else:
            if az:
                chunks.append(_az_links(part or "front", chapters))
            chunks.append(_item_list(part or "front", chapters, az=az))
        chunks.append("</details>")
    chunks.append("</nav>")
    return "\n".join(chunks)


def wrap_body(html_doc: str, toc: str, labels: dict[str, str]) -> str:
    html_doc = NAV_RE.sub("", html_doc, count=1)
    html_doc = html_doc.replace('<div class="book-layout">', "")
    html_doc = re.sub(
        r"</article>\s*</div>\s*(?=<a class=\"toc-jump\"|<script src=\"book.js\")",
        "</article>\n",
        html_doc,
        count=1,
    )
    layout = f'<div class="book-layout">\n{toc}\n'
    if 'class="book-body"' in html_doc:
        html_doc = html_doc.replace(
            '<article class="book-body">',
            layout + '<article class="book-body">',
            1,
        )
    else:
        insertion = layout + '<article class="book-body">\n'
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
            f'</article>\n<a class="toc-jump" href="#TOC">{labels["contents"]}</a>\n'
            '<script src="book.js"></script>\n</body>',
            1,
        )
    html_doc = re.sub(
        r"</article>(\s*)(?=<a class=\"toc-jump\"|<script src=\"book.js\"|</body>)",
        "</article>\n</div>\n",
        html_doc,
        count=1,
    )
    if "book.js" not in html_doc:
        html_doc = html_doc.replace(
            "</body>",
            '<script src="book.js"></script>\n</body>',
            1,
        )
    banner = re.search(r'<header class="book-banner">.*?</header>', html_doc, flags=re.S)
    if banner:
        text = banner.group(0)
        if 'href="#TOC"' not in text:
            text = text.replace(
                "</p></header>",
                f' · <a href="#TOC">{labels["contents"]}</a></p></header>',
                1,
            )
        if ">EPUB</a>" not in text:
            slug_m = re.search(r'class="book book-([a-z0-9-]+)"', html_doc)
            if slug_m:
                slug = slug_m.group(1)
                extra = (
                    f' · <a href="../downloads/{slug}.epub">EPUB</a>'
                    f' · <a href="../downloads/{slug}.pdf">PDF</a>'
                )
                text = text.replace("</p></header>", extra + "</p></header>", 1)
        if 'class="github"' not in text:
            text = text.replace(
                "</p></header>",
                f" · {github_icon_link(labels['source_on_github'])}</p></header>",
                1,
            )
        if text != banner.group(0):
            html_doc = html_doc.replace(banner.group(0), text, 1)
    return html_doc


def add_chapter_edit_links(
    html_doc: str, entries: list[dict], labels: dict[str, str]
) -> str:
    for entry in entries:
        edit_url = entry.get("edit_url")
        if not edit_url:
            continue
        heading_id = re.escape(entry["href"])
        pattern = re.compile(
            rf'<h1(?P<attrs>\b[^>]*\bid="{heading_id}"[^>]*)>(?P<body>.*?)</h1>',
            re.I | re.S,
        )
        href = html.escape(edit_url, quote=True)
        title = html.escape(entry["title"], quote=True)
        replacement = (
            '<div class="chapter-heading">'
            r'<h1\g<attrs>>\g<body></h1>'
            f'<a class="chapter-edit" href="{href}" '
            f'aria-label="{labels["edit_on_wiki_aria"].format(title=title)}">'
            f'{labels["edit_on_wiki"]}</a>'
            '</div>'
        )
        html_doc = pattern.sub(replacement, html_doc, count=1)
    return html_doc


def add_missing_drupal_source_links(
    html_doc: str,
    entries: list[dict],
    sources: dict[str, dict[str, str]],
) -> str:
    """Add node references to preserved Drupal chapters that lack attribution."""
    insertions: list[tuple[int, str]] = []
    for entry in entries:
        source = sources.get(entry.get("path", ""))
        if not source:
            continue
        heading = re.search(
            rf'<h1\b[^>]*\bid="{re.escape(entry["href"])}"[^>]*>.*?</h1>',
            html_doc,
            re.I | re.S,
        )
        if not heading:
            continue
        next_heading = re.search(r"<h1\b", html_doc[heading.end() :], re.I)
        end = heading.end() + next_heading.start() if next_heading else html_doc.find("</article>", heading.end())
        if end < 0:
            continue
        section = html_doc[heading.end() : end]
        if 'class="chapter-source"' in section or re.search(r"<p>Source:", section, re.I):
            continue
        url = html.escape(str(source.get("url", "")), quote=True)
        label = html.escape(str(source.get("label", "")))
        if url and label:
            insertions.append(
                (end, f'<p class="chapter-source"><a href="{url}">{label}</a></p>\n')
            )
    for position, markup in reversed(insertions):
        html_doc = html_doc[:position] + markup + html_doc[position:]
    return html_doc


def enhance_html(
    html_doc: str,
    chapters: list[Path],
    src: Path,
    lang: str = "en",
    drupal_sources: dict[str, dict[str, str]] | None = None,
) -> str:
    labels = ui_strings(lang)
    entries = toc_entries(chapters, html_doc, src)
    expected = sum(1 for p in chapters if not p.name.startswith("00-frontmatter"))
    if len(entries) != expected:
        print(f"  toc: matched {len(entries)}/{expected} chapters", flush=True)
    html_doc = add_missing_drupal_source_links(html_doc, entries, drupal_sources or {})
    html_doc = add_chapter_edit_links(html_doc, entries, labels)
    return wrap_body(html_doc, render_toc(entries, labels), labels)

#!/usr/bin/env python3
"""Fetch Hitchwiki / Trashwiki / Nomadwiki / Trustroots Wiki pages into book src/."""

from __future__ import annotations

import argparse
import gzip
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CACHE, ROOT, category_members, download, get, mw_api, slugify
from editorial import write_generated
from images import license_ok, save_image, write_manifest
from titles import (
    CITY_ALIASES,
    CITY_MAP_LINKS,
    CITY_SELECTION,
    HOWTO_FALLBACK,
    WIKIS,
    city_part,
    country_slug_for_city,
)
from wiki_links import (
    strip_category_markdown,
    strip_category_wikitext,
    strip_interwiki_markdown,
    strip_interwiki_wikitext,
)
from wiki_contributors import write_manifest as write_contributor_manifest

FILE_RE = re.compile(r"\[\[\s*(?:File|Image|file|image)\s*:\s*([^|\]]+)", re.I)
NS = {"mw": "http://www.mediawiki.org/xml/export-0.11/"}


def local(el, name: str):
    tag = el.tag
    if tag.endswith("}" + name) or tag == name:
        return True
    return False


def find_child(el, name: str):
    for c in el:
        if local(c, name):
            return c
    return None


def parse_dump_pages(path: Path) -> dict[str, str]:
    import xml.etree.ElementTree as ET

    opener = gzip.open if path.suffix == ".gz" or path.name.endswith(".xml.gz") else open
    pages: dict[str, str] = {}
    with opener(path, "rb") as fh:
        context = ET.iterparse(fh, events=("end",))
        for _, el in context:
            if not local(el, "page"):
                continue
            title_el = find_child(el, "title")
            rev = find_child(el, "revision")
            text_el = find_child(rev, "text") if rev is not None else None
            if title_el is not None and text_el is not None and text_el.text:
                pages[title_el.text] = text_el.text
            el.clear()
    return pages


def api_revisions(api: str, titles: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i in range(0, len(titles), 20):
        chunk = titles[i : i + 20]
        data = mw_api(
            api,
            {
                "action": "query",
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "titles": "|".join(chunk),
            },
        )
        for page in data.get("query", {}).get("pages", {}).values():
            title = page.get("title")
            revs = page.get("revisions") or []
            if not title or not revs:
                continue
            slot = revs[0].get("slots", {}).get("main", {})
            text = slot.get("*") or revs[0].get("*")
            if text:
                out[title] = text
    return out


def strip_templates(wikitext: str) -> str:
    out = []
    i = 0
    n = len(wikitext)
    while i < n:
        if wikitext.startswith("{{", i):
            depth = 2
            j = i + 2
            while j < n and depth:
                if wikitext.startswith("{{", j):
                    depth += 2
                    j += 2
                    continue
                if wikitext.startswith("}}", j):
                    depth -= 2
                    j += 2
                    continue
                j += 1
            i = j
            continue
        out.append(wikitext[i])
        i += 1
    return "".join(out)


HEADING_RE = re.compile(r"^(={2,4})\s*([^=]+?)\s*\1\s*$", re.M)
SPOT_HEAD_RE = re.compile(
    r"""^(
        hitchhiking\s+(in|out|spots)|
        hitching\s+(in|out)|
        hitch\s+out|
        getting\s+(in|out|north|south|east|west)|
        option\b|
        bonus\s+tip|
        personal\s+experiences?|
        north|south|east|west|northeast|northwest|southeast|southwest|
        .*\btowards\b|
        .*\bmotorway\b|
        .*\bpetrol\b|
        .*\bgas\s+station|
        .*\bservice\s+station|
        aire\s+de\b|
        raststätte|
        p[ée]age|
        dumpsters?\b|
        specific\s+spots|
        hitch\s+spots|
        on-ramps?|
        off-ramps?|
        slip-?road|
        exact\s+location|
        coordinates|
        inside\b|
        in\s+the\s+suburbs|
        free\s+shops?|
        free\s+stuff|
        medical\s+assistance
    )""",
    re.I | re.X,
)
GOOGLEMAP_RE = re.compile(r"<googlemap[\s\S]*?</googlemap>", re.I)
HTML_MAP_RE = re.compile(r"<div[^>]*>\s*<googlemap[\s\S]*?</div>", re.I)
REDIRECT_RE = re.compile(r"#\s*redirect\s*\[\[([^\]|#]+)", re.I)
COORDS_RE = re.compile(r"\b-?\d{1,3}\.\d{3,},\s*-?\d{1,3}\.\d{3,}\b")


def strip_spot_sections(wikitext: str) -> str:
    """Drop pin-level sections; keep intro and evergreen headings."""
    wikitext = GOOGLEMAP_RE.sub("", wikitext)
    wikitext = re.sub(r"<div[^>]*>\s*</div>", "", wikitext, flags=re.I)
    matches = list(HEADING_RE.finditer(wikitext))
    if not matches:
        return COORDS_RE.sub("", wikitext)
    parts = [wikitext[: matches[0].start()]]
    for i, m in enumerate(matches):
        title = re.sub(r"\[\[([^|\]]+\|)?([^\]]+)\]\]", r"\2", m.group(2))
        title = re.sub(r"\{\{[^}]+\}\}", "", title).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(wikitext)
        if SPOT_HEAD_RE.match(title):
            continue
        parts.append(wikitext[m.start() : end])
    return COORDS_RE.sub("", "".join(parts))


def city_candidates(name: str) -> tuple[str, ...]:
    return CITY_ALIASES.get(name, (name,))


def page_text(pages: dict[str, str], title: str) -> str | None:
    if title in pages:
        return pages[title]
    spaced = title.replace("_", " ")
    if spaced in pages:
        return pages[spaced]
    return pages.get(title.replace(" ", "_"))


def follow_redirect(title: str, pages: dict[str, str]) -> tuple[str, str] | None:
    """Return (title, wikitext), or None if this is a redirect with no usable target."""
    text = page_text(pages, title)
    if not text:
        return None
    m = REDIRECT_RE.match(text.strip())
    if not m:
        return title, text
    tgt = m.group(1).strip().replace("_", " ")
    text = page_text(pages, tgt)
    if not text or REDIRECT_RE.match(text.strip()):
        return None
    return tgt, text


def resolve_page(title: str, pages: dict[str, str]) -> tuple[str, str] | None:
    followed = follow_redirect(title, pages)
    if not followed:
        return None
    title, text = followed
    if len(text) < 400:
        return None
    return title, text


def wikitext_to_markdown(wikitext: str, *, strip_spots: bool = False) -> str:
    wikitext = strip_templates(wikitext)
    wikitext = strip_category_wikitext(wikitext)
    wikitext = strip_interwiki_wikitext(wikitext)
    if strip_spots:
        wikitext = strip_spot_sections(wikitext)
    try:
        proc = subprocess.run(
            ["pandoc", "-f", "mediawiki", "-t", "markdown", "--wrap=none"],
            input=wikitext,
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return strip_category_markdown(strip_interwiki_markdown(proc.stdout))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    text = re.sub(r"\{\{[^}]+\}\}", "", wikitext)
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'''(.+?)'''", r"**\1**", text)
    text = re.sub(r"''(.+?)''", r"*\1*", text)
    return strip_category_markdown(strip_interwiki_markdown(text))


def collect_titles(wiki: str, cfg: dict) -> tuple[list[str], list[str]]:
    howto, countries = [], []
    for cat in cfg.get("howto_categories") or []:
        try:
            howto.extend(category_members(cfg["api"], cat))
        except Exception as exc:
            print(f"  category {cat} failed: {exc}", file=sys.stderr)
    for title in cfg.get("howto_titles") or []:
        howto.append(title)
    for title in HOWTO_FALLBACK.get(wiki, []):
        if title not in howto:
            howto.append(title)
    for cat in cfg.get("country_categories") or []:
        try:
            countries.extend(category_members(cfg["api"], cat))
        except Exception as exc:
            print(f"  category {cat} failed: {exc}", file=sys.stderr)
    for title in cfg.get("country_titles") or []:
        countries.append(title)
    prefixes = cfg.get("skip_title_prefixes") or ()
    skip_titles = set(cfg.get("skip_titles") or ())
    def keep(t: str) -> bool:
        return t and not t.startswith(prefixes) and t not in skip_titles
    howto = [t for t in dict.fromkeys(howto) if keep(t)]
    countries = [t for t in dict.fromkeys(countries) if keep(t)]
    # Country category on hitchwiki is actual countries; on trashwiki Europe
    # includes cities — drop titles that look like city-only if they also
    # appear as non-country stubs later. Keep all category members for now
    # except obvious talk/files already filtered.
    return howto, countries


def imageinfo(api: str, filename: str) -> dict | None:
    title = filename if filename.startswith("File:") else f"File:{filename}"
    data = mw_api(
        api,
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|user|extmetadata|mime",
        },
    )
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = (page.get("imageinfo") or [None])[0]
        if info:
            return info
    return None


def fetch_page_images(
    api: str,
    wikitext: str,
    img_dir: Path,
    manifest: list,
    limit: int = 3,
    *,
    chapter_path: Path | None = None,
) -> str:
    names = []
    for m in FILE_RE.finditer(wikitext):
        name = m.group(1).strip()
        if name not in names:
            names.append(name)
    md_extra = []
    prefix = "../../images"
    if chapter_path is not None:
        prefix = Path(os.path.relpath(img_dir, chapter_path.parent)).as_posix()
    for name in names[:limit]:
        try:
            info = imageinfo(api, name)
        except Exception:
            continue
        if not info:
            continue
        meta = info.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value") or (meta.get("License") or {}).get("value")
        artist = (meta.get("Artist") or {}).get("value") or info.get("user") or ""
        artist = re.sub("<[^>]+>", "", artist)
        if not license_ok(lic) or not license_ok(artist):
            continue
        url = info.get("url")
        if not url:
            continue
        path = save_image(url, img_dir, name)
        if not path:
            continue
        rel = f"{prefix}/{path.name}"
        cap = f"{name} — {artist}".strip(" —")
        if lic:
            cap += f" ({lic})"
        md_extra.append(f"![{name}]({rel})\n\n*{cap}*\n")
        manifest.append(
            {
                "file": path.name,
                "source": url,
                "author": artist,
                "license": lic,
                "caption": cap,
            }
        )
    return "\n".join(md_extra)


def chapter_dest(book: Path, part: str, slug: str) -> Path:
    """Keep an editorial move: if this slug already lives in another part, write there."""
    default = book / "src" / part / f"{slug}.md"
    if default.exists():
        return default
    src = book / "src"
    if not src.exists():
        return default
    matches = [p for p in src.rglob(f"{slug}.md") if p.is_file()]
    if len(matches) == 1:
        return matches[0]
    return default


def write_chapter(
    book: Path,
    part: str,
    title: str,
    body: str,
    source_url: str,
    extra_md: str,
    license_spdx: str,
    *,
    strip_spots: bool = False,
    notice: str = "",
    show_license: bool = True,
) -> str:
    dest = chapter_dest(book, part, slugify(title))
    md = wikitext_to_markdown(body, strip_spots=strip_spots)
    if strip_spots and len(re.sub(r"\s+", " ", md).strip()) < 280:
        md = (
            "This book does not reprint named ramps, dumpsters, hostels, or other pins. "
            "They go out of date. Follow the note above to the live map or wiki.\n"
        )
    banner = f"> {notice}\n\n" if notice else ""
    license_line = f"  \nLicense: {license_spdx}" if show_license else ""
    footer = f"\n\n---\n\nSource: [{title}]({source_url}){license_line}\n"
    generated = f"# {title}\n\n{banner}{md}\n\n{extra_md}{footer}"
    return write_generated(book, dest, generated, title=title)


def fetch_wiki(
    wiki: str,
    *,
    max_howto: int | None,
    max_countries: int | None,
    skip_images: bool = False,
    cities_only: bool = False,
) -> None:
    cfg = WIKIS[wiki]
    print(f"== {wiki} ==", flush=True)
    if cities_only:
        howto, countries = [], []
    else:
        howto, countries = collect_titles(wiki, cfg)
        if max_howto is not None:
            howto = howto[:max_howto]
        if max_countries is not None:
            countries = countries[:max_countries]
    city_names: list[str] = []
    for name in CITY_SELECTION.get(wiki) or []:
        city_names.extend(city_candidates(name))
    city_names = list(dict.fromkeys(city_names))
    print(f"  howto={len(howto)} countries={len(countries)} city_titles={len(city_names)}", flush=True)
    wanted = howto + countries + city_names
    pages: dict[str, str] = {}
    dump_url = cfg.get("dump")
    if dump_url:
        dest = CACHE / Path(dump_url).name
        print(f"  dump {dump_url}", flush=True)
        download(dump_url, dest)
        pages = parse_dump_pages(dest)
        print(f"  dump pages={len(pages)}", flush=True)
    missing = [t for t in wanted if t not in pages]
    if missing:
        print(f"  api revisions for {len(missing)} titles", flush=True)
        try:
            pages.update(api_revisions(cfg["api"], missing))
        except Exception as exc:
            print(f"  api revisions failed: {exc}", file=sys.stderr, flush=True)
    book = ROOT / "books" / cfg["book"]
    img_dir = book / "images"
    manifest: list[dict] = []
    license_spdx = {
        "hitchwiki": "CC-BY-SA-4.0",
        "trashwiki": "CC-BY-NC-SA-4.0",
        "nomadwiki": "CC-BY-SA-4.0",
        "trustroots": "CC-BY-SA-4.0",
    }[wiki]
    stubs = tuple(s.lower() for s in cfg.get("stub_if_title_contains") or ())
    counts = {"wrote": 0, "skip-lock": 0, "skip-omit": 0, "skip-redirect": 0, "conflict": 0}

    def record(result: str) -> None:
        counts[result] = counts.get(result, 0) + 1

    def compile_titles(
        titles: list[str], part: str, image_limit: int, *, apply_stubs: bool = False
    ) -> None:
        seen: set[str] = set()
        for original in titles:
            followed = follow_redirect(original, pages)
            if followed is None:
                raw = page_text(pages, original)
                if raw and REDIRECT_RE.match(raw.strip()):
                    record("skip-redirect")
                continue
            title, text = followed
            slug = slugify(title)
            if slug in seen:
                if slugify(original) != slug:
                    record("skip-redirect")
                continue
            seen.add(slug)
            if apply_stubs and stubs and any(s in title.lower() for s in stubs):
                text = (
                    f"This topic is covered in another book in this catalog "
                    f"(hitchhiking, dumpster diving, or hospitality exchange). "
                    f"See the live wiki: {cfg['origin']}{title.replace(' ', '_')}\n"
                )
            dest = chapter_dest(book, part, slug)
            extra_md = (
                ""
                if skip_images
                else fetch_page_images(
                    cfg["api"], text, img_dir, manifest, limit=image_limit, chapter_path=dest
                )
            )
            url = cfg["origin"] + title.replace(" ", "_")
            record(
                write_chapter(
                    book,
                    part,
                    title,
                    text,
                    url,
                    extra_md,
                    license_spdx,
                    show_license=cfg.get("chapter_license_footers", True),
                )
            )

    compile_titles(howto, cfg["part_howto"], 3, apply_stubs=True)
    compile_titles(countries, cfg["part_country"], 2)
    if wiki in CITY_MAP_LINKS:
        notice = CITY_MAP_LINKS[wiki]
        seen_cities: set[str] = set()
        for name in CITY_SELECTION.get(wiki) or []:
            chosen = None
            for cand in city_candidates(name):
                chosen = resolve_page(cand, pages)
                if chosen:
                    break
            if not chosen:
                continue
            title, text = chosen
            if title in seen_cities:
                continue
            seen_cities.add(title)
            part = city_part(wiki, title)
            city_slug = slugify(title)
            country_slug = country_slug_for_city(wiki, title)
            country_file = book / "src" / cfg["part_country"] / f"{country_slug}.md"
            if country_slug and city_slug == country_slug and country_file.exists():
                print(f"  skip city {title} (same page as country)", flush=True)
                continue
            dest = book / "src" / part / f"{city_slug}.md"
            extra = (
                ""
                if skip_images
                else fetch_page_images(cfg["api"], text, img_dir, manifest, limit=2, chapter_path=dest)
            )
            url = cfg["origin"] + title.replace(" ", "_")
            record(
                write_chapter(
                    book,
                    part,
                    title,
                    text,
                    url,
                    extra,
                    license_spdx,
                    strip_spots=True,
                    notice=notice,
                    show_license=cfg.get("chapter_license_footers", True),
                )
            )
        print(f"  cities={len(seen_cities)}", flush=True)
    if manifest:
        write_manifest(img_dir / "images.json", manifest)
    try:
        write_contributor_manifest(wiki)
    except Exception as exc:
        # Keep the previous manifest when contributor-history lookup is temporarily
        # unavailable; chapter fetching itself can still complete from a dump.
        print(f"  contributor attribution failed: {exc}", file=sys.stderr, flush=True)
    extra = []
    for key in ("skip-lock", "skip-omit", "skip-redirect", "conflict"):
        if counts[key]:
            extra.append(f"{key}={counts[key]}")
    suffix = f" ({', '.join(extra)})" if extra else ""
    print(f"  wrote {counts['wrote']} chapters{suffix}", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--wiki", choices=list(WIKIS), action="append")
    p.add_argument("--all", action="store_true")
    p.add_argument("--max-howto", type=int, default=None)
    p.add_argument("--max-countries", type=int, default=None)
    p.add_argument("--skip-images", action="store_true")
    p.add_argument("--cities-only", action="store_true")
    args = p.parse_args()
    wikis = list(WIKIS) if args.all or not args.wiki else args.wiki
    CACHE.mkdir(exist_ok=True)
    for w in wikis:
        fetch_wiki(
            w,
            max_howto=args.max_howto,
            max_countries=args.max_countries,
            skip_images=args.skip_images,
            cities_only=args.cities_only,
        )


if __name__ == "__main__":
    main()

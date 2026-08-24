#!/usr/bin/env python3
"""Fetch Hitchwiki / Trashwiki / Nomadwiki / Trustroots Wiki pages into book src/."""

from __future__ import annotations

import argparse
import gzip
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import CACHE, ROOT, category_members, download, get, mw_api, slugify
from images import license_ok, save_image, write_manifest
from titles import HOWTO_FALLBACK, WIKIS

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


def wikitext_to_markdown(wikitext: str) -> str:
    wikitext = strip_templates(wikitext)
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
            return proc.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    text = re.sub(r"\{\{[^}]+\}\}", "", wikitext)
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'''(.+?)'''", r"**\1**", text)
    text = re.sub(r"''(.+?)''", r"*\1*", text)
    return text


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


def fetch_page_images(api: str, wikitext: str, img_dir: Path, manifest: list, limit: int = 3) -> str:
    names = []
    for m in FILE_RE.finditer(wikitext):
        name = m.group(1).strip()
        if name not in names:
            names.append(name)
    md_extra = []
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
        rel = f"../../images/{path.name}"
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


def write_chapter(book: Path, part: str, title: str, body: str, source_url: str, extra_md: str, license_spdx: str) -> None:
    dest = book / "src" / part / f"{slugify(title)}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    md = wikitext_to_markdown(body)
    footer = (
        f"\n\n---\n\nSource: [{title}]({source_url})  \n"
        f"License: {license_spdx}\n"
    )
    dest.write_text(f"# {title}\n\n{md}\n\n{extra_md}{footer}", encoding="utf-8")


def fetch_wiki(wiki: str, *, max_howto: int | None, max_countries: int | None, skip_images: bool = False) -> None:
    cfg = WIKIS[wiki]
    print(f"== {wiki} ==", flush=True)
    howto, countries = collect_titles(wiki, cfg)
    if max_howto is not None:
        howto = howto[:max_howto]
    if max_countries is not None:
        countries = countries[:max_countries]
    print(f"  howto={len(howto)} countries={len(countries)}", flush=True)
    wanted = howto + countries
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
        "trashwiki": "CC-BY-NC-SA-3.0",
        "nomadwiki": "CC-BY-SA-4.0",
        "trustroots": "CC-BY-SA-4.0",
    }[wiki]
    stubs = tuple(s.lower() for s in cfg.get("stub_if_title_contains") or ())
    n = 0
    for title in howto:
        text = pages.get(title)
        if not text:
            continue
        if stubs and any(s in title.lower() for s in stubs):
            text = (
                f"This topic is covered in another book in this catalog "
                f"(hitchhiking, dumpster diving, or hospitality exchange). "
                f"See the live wiki: {cfg['origin']}{title.replace(' ', '_')}\n"
            )
        extra = "" if skip_images else fetch_page_images(cfg["api"], pages.get(title, ""), img_dir, manifest, limit=3)
        url = cfg["origin"] + title.replace(" ", "_")
        write_chapter(book, cfg["part_howto"], title, text, url, extra, license_spdx)
        n += 1
    for title in countries:
        text = pages.get(title)
        if not text:
            continue
        extra = "" if skip_images else fetch_page_images(cfg["api"], text, img_dir, manifest, limit=2)
        url = cfg["origin"] + title.replace(" ", "_")
        write_chapter(book, cfg["part_country"], title, text, url, extra, license_spdx)
        n += 1
    if manifest:
        write_manifest(img_dir / "images.json", manifest)
    print(f"  wrote {n} chapters", flush=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--wiki", choices=list(WIKIS), action="append")
    p.add_argument("--all", action="store_true")
    p.add_argument("--max-howto", type=int, default=None)
    p.add_argument("--max-countries", type=int, default=None)
    p.add_argument("--skip-images", action="store_true")
    args = p.parse_args()
    wikis = list(WIKIS) if args.all or not args.wiki else args.wiki
    CACHE.mkdir(exist_ok=True)
    for w in wikis:
        fetch_wiki(
            w,
            max_howto=args.max_howto,
            max_countries=args.max_countries,
            skip_images=args.skip_images,
        )


if __name__ == "__main__":
    main()

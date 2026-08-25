#!/usr/bin/env python3
"""Collect wiki contributors from local full-history dumps."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT
from titles import WIKIS


MARKDOWN_SOURCE_RE = re.compile(
    r"^Source:\s*\[([^]]+)\]\((https?://[^)]+)\)", re.I | re.M
)

FULL_XML_DUMPS = {
    "hitchwiki": "hitchwiki-full-en.xml.gz",
    "nomadwiki": "nomadwiki-full.xml.gz",
    "trustroots": "trustroots-full.xml.gz",
}
TRASHWIKI_SQL = ROOT / "dumps" / "sql" / "trashwiki.sql.gz"
MYSQL_STRING_RE = r"((?:\\.|[^'])*)"
ACTOR_ROW_RE = re.compile(
    rf"\((\d+),(\d+|NULL),_binary '{MYSQL_STRING_RE}'\)"
)
PAGE_ROW_RE = re.compile(
    rf"\((\d+),(\d+),_binary '{MYSQL_STRING_RE}',"
)
REVISION_ROW_RE = re.compile(r"\((\d+),(\d+),(\d+),(\d+),")


def contributor_sort_key(name: str) -> tuple[str, str]:
    return (name.casefold(), name)


def source_titles(book: Path, origin: str) -> list[str]:
    """Find wiki page titles from the canonical source notes in compiled chapters."""
    origin_url = urlparse(origin)
    origin_host = (origin_url.hostname or "").lower().removeprefix("www.")
    origin_path = origin_url.path.rstrip("/") + "/"
    titles: list[str] = []
    for chapter in (book / "src").rglob("*.md"):
        for label, raw_url in MARKDOWN_SOURCE_RE.findall(
            chapter.read_text(encoding="utf-8")
        ):
            url = urlparse(raw_url)
            host = (url.hostname or "").lower().removeprefix("www.")
            if host != origin_host or not url.path.startswith(origin_path):
                continue
            title = unquote(url.path[len(origin_path) :]).replace("_", " ").strip("/")
            titles.append(title or label.strip())
    return list(dict.fromkeys(titles))


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize_title(title: str) -> str:
    return title.replace("_", " ").strip().casefold()


def xml_contributors(path: Path, titles: list[str]) -> tuple[list[str], bool]:
    """Read contributors to selected pages from a full-history MediaWiki XML dump."""
    wanted = {normalize_title(title) for title in titles}
    names: set[str] = set()
    has_anonymous = False
    with gzip.open(path, "rb") as source:
        for _, page in ET.iterparse(source, events=("end",)):
            if local_name(page.tag) != "page":
                continue
            title = next(
                (child.text or "" for child in page if local_name(child.tag) == "title"),
                "",
            )
            if normalize_title(title) in wanted:
                for contributor in page.iter():
                    if local_name(contributor.tag) != "contributor":
                        continue
                    username = next(
                        (
                            child.text or ""
                            for child in contributor
                            if local_name(child.tag) == "username"
                        ),
                        "",
                    ).strip()
                    if username:
                        names.add(username)
                    elif any(local_name(child.tag) == "ip" for child in contributor):
                        has_anonymous = True
            page.clear()
    return sorted(names, key=contributor_sort_key), has_anonymous


def mysql_unescape(value: str) -> str:
    escapes = {
        "0": "\0",
        "b": "\b",
        "n": "\n",
        "r": "\r",
        "t": "\t",
        "Z": "\x1a",
        "\\": "\\",
        "'": "'",
        '"': '"',
    }
    return re.sub(r"\\(.)", lambda match: escapes.get(match.group(1), match.group(1)), value)


def trashwiki_contributors(path: Path, titles: list[str]) -> tuple[list[str], bool]:
    """Join page, revision, and actor rows from a local MediaWiki SQL dump."""
    wanted = {normalize_title(title) for title in titles}
    actors: dict[int, tuple[int | None, str]] = {}
    page_ids: set[int] = set()
    revision_actors: set[int] = set()
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as source:
        for line in source:
            if line.startswith("INSERT INTO `actor`"):
                for actor_id, user_id, raw_name in ACTOR_ROW_RE.findall(line):
                    actors[int(actor_id)] = (
                        None if user_id == "NULL" else int(user_id),
                        mysql_unescape(raw_name),
                    )
            elif line.startswith("INSERT INTO `page`"):
                for page_id, namespace, raw_title in PAGE_ROW_RE.findall(line):
                    if namespace == "0" and normalize_title(mysql_unescape(raw_title)) in wanted:
                        page_ids.add(int(page_id))
            elif line.startswith("INSERT INTO `revision`"):
                for _revision_id, page_id, _comment_id, actor_id in REVISION_ROW_RE.findall(line):
                    if int(page_id) in page_ids:
                        revision_actors.add(int(actor_id))
    names = {
        name
        for actor_id in revision_actors
        if actor_id in actors
        for user_id, name in [actors[actor_id]]
        if user_id is not None and name
    }
    has_anonymous = any(
        actor_id in actors and actors[actor_id][0] is None for actor_id in revision_actors
    )
    return sorted(names, key=contributor_sort_key), has_anonymous


def write_manifest(wiki: str) -> Path:
    cfg = WIKIS[wiki]
    book = ROOT / "books" / cfg["book"]
    titles = source_titles(book, cfg["origin"])
    if not titles:
        raise RuntimeError(f"{wiki}: no source pages found in {book / 'src'}")
    if wiki == "trashwiki":
        dump_path = TRASHWIKI_SQL
        if not dump_path.exists():
            raise FileNotFoundError(f"missing full-history dump: {dump_path}")
        contributors, has_anonymous = trashwiki_contributors(dump_path, titles)
    else:
        dump_path = ROOT / "dumps" / FULL_XML_DUMPS[wiki]
        if not dump_path.exists():
            raise FileNotFoundError(f"missing full-history dump: {dump_path}; run make dumps")
        contributors, has_anonymous = xml_contributors(dump_path, titles)
    manifest = {
        "wiki": wiki,
        "source": cfg["origin"],
        "dump": dump_path.name,
        "pages": len(titles),
        "contributors": contributors,
        "anonymous_contributors": has_anonymous,
    }
    path = book / "editorial" / "wiki-contributors.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{wiki}: {len(contributors)} registered contributors across {len(titles)} pages")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki", choices=list(WIKIS), action="append")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    wikis = list(WIKIS) if args.all or not args.wiki else args.wiki
    for wiki in wikis:
        write_manifest(wiki)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Merge wiki/Drupal compiles with in-chapter editorial edits.

Generated chapters can be refreshed. Local work survives if it is marked
(before/after), locked, omitted, or (after stamping) if the generated
middle was edited — that last case is a conflict, not a silent overwrite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ROOT

BOOKS = [
    "hitchhikers-guide",
    "dumpster-diving",
    "random-roads",
    "dumpsterdam",
    "hospitality-exchange",
    "moneyless",
    "shoestring-nomad",
]

BEFORE_RE = re.compile(
    r"<!--\s*editorial:before\s*-->\s*(.*?)\s*<!--\s*/editorial:before\s*-->",
    re.S | re.I,
)
AFTER_RE = re.compile(
    r"<!--\s*editorial:after\s*-->\s*(.*?)\s*<!--\s*/editorial:after\s*-->",
    re.S | re.I,
)
LOCK_RE = re.compile(r"<!--\s*editorial:lock\s*-->", re.I)
OMIT_RE = re.compile(r"<!--\s*editorial:omit\s*-->", re.I)
META_RE = re.compile(r"<!--\s*books-upstream\b[^>]*-->\s*", re.I)


@dataclass
class Overlay:
    lock: bool = False
    omit: bool = False
    dirty: bool = False
    before: str = ""
    after: str = ""
    stored_sha: str | None = None
    current_sha: str | None = None


def book_dir(slug: str) -> Path:
    return ROOT / "books" / slug


def editorial_dir(book: Path) -> Path:
    return book / "editorial"


def src_rel(book: Path, dest: Path) -> str:
    return dest.relative_to(book / "src").as_posix()


def sha256_text(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n"


def load_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def load_upstream(book: Path) -> dict[str, str]:
    path = editorial_dir(book) / "upstream.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save_upstream(book: Path, data: dict[str, str]) -> None:
    path = editorial_dir(book)
    path.mkdir(parents=True, exist_ok=True)
    dest = path / "upstream.json"
    dest.write_text(
        json.dumps(dict(sorted(data.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def listed(path: Path, *candidates: str) -> bool:
    wanted = {c.strip() for c in candidates if c and c.strip()}
    for line in load_lines(path):
        if line in wanted:
            return True
    return False


def generated_body(text: str) -> str:
    text = META_RE.sub("", text)
    text = LOCK_RE.sub("", text)
    text = OMIT_RE.sub("", text)
    text = BEFORE_RE.sub("", text)
    text = AFTER_RE.sub("", text)
    return normalize(text)


def parse_overlay(book: Path, dest: Path, title: str = "") -> Overlay:
    ov = Overlay()
    try:
        rel = src_rel(book, dest)
    except ValueError:
        rel = dest.name
    slug = dest.stem
    ed = editorial_dir(book)
    ov.lock = listed(ed / "lock.txt", rel, slug, title)
    ov.omit = listed(ed / "omit.txt", rel, slug, title)
    text = dest.read_text(encoding="utf-8") if dest.exists() else ""
    if text:
        ov.lock = ov.lock or bool(LOCK_RE.search(text))
        ov.omit = ov.omit or bool(OMIT_RE.search(text))
        before = BEFORE_RE.search(text)
        after = AFTER_RE.search(text)
        ov.before = before.group(1).strip() if before else ""
        ov.after = after.group(1).strip() if after else ""
        ov.current_sha = sha256_text(generated_body(text))
    upstream = load_upstream(book)
    ov.stored_sha = upstream.get(rel)
    if ov.stored_sha and ov.current_sha and ov.current_sha != ov.stored_sha:
        ov.dirty = True
    return ov


def assemble(generated: str, ov: Overlay) -> str:
    parts: list[str] = []
    if ov.before:
        parts.append(
            "<!-- editorial:before -->\n"
            + ov.before.strip()
            + "\n<!-- /editorial:before -->\n"
        )
    parts.append(normalize(generated).rstrip() + "\n")
    if ov.after:
        parts.append(
            "\n<!-- editorial:after -->\n"
            + ov.after.strip()
            + "\n<!-- /editorial:after -->\n"
        )
    return "".join(parts)


def conflict_path(book: Path, dest: Path) -> Path:
    rel = src_rel(book, dest)
    return ROOT / "build" / "editorial-conflicts" / book.name / rel


def write_generated(
    book: Path,
    dest: Path,
    generated: str,
    *,
    title: str = "",
) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    ov = parse_overlay(book, dest, title=title)
    if ov.omit:
        return "skip-omit"
    if ov.lock:
        return "skip-lock"
    if ov.dirty:
        proposed = conflict_path(book, dest)
        proposed.parent.mkdir(parents=True, exist_ok=True)
        proposed.write_text(assemble(generated, ov), encoding="utf-8")
        print(
            f"  CONFLICT {src_rel(book, dest)} "
            f"(local generated body changed; not overwritten)",
            file=sys.stderr,
        )
        return "conflict"
    dest.write_text(assemble(generated, ov), encoding="utf-8")
    rel = src_rel(book, dest)
    upstream = load_upstream(book)
    upstream[rel] = sha256_text(generated_body(dest.read_text(encoding="utf-8")))
    save_upstream(book, upstream)
    return "wrote"


def is_omitted_chapter(book: Path, path: Path) -> bool:
    return parse_overlay(book, path).omit


def stamp_book(book: Path) -> tuple[int, int]:
    src = book / "src"
    if not src.exists():
        return 0, 0
    upstream = load_upstream(book)
    stamped = 0
    locked = 0
    for path in sorted(src.rglob("*.md")):
        ov = parse_overlay(book, path)
        if ov.lock or ov.omit:
            locked += 1
            upstream.pop(src_rel(book, path), None)
            continue
        upstream[src_rel(book, path)] = sha256_text(
            generated_body(path.read_text(encoding="utf-8"))
        )
        stamped += 1
    save_upstream(book, upstream)
    return stamped, locked


def status_book(book: Path) -> None:
    src = book / "src"
    if not src.exists():
        return
    print(f"== {book.name} ==")
    n_lock = n_omit = n_dirty = n_edit = n_gen = 0
    for path in sorted(src.rglob("*.md")):
        ov = parse_overlay(book, path)
        rel = src_rel(book, path)
        if ov.omit:
            print(f"  omit  {rel}")
            n_omit += 1
        elif ov.lock:
            print(f"  lock  {rel}")
            n_lock += 1
        elif ov.dirty:
            print(f"  dirty {rel}")
            n_dirty += 1
        elif ov.before or ov.after:
            print(f"  edit  {rel}")
            n_edit += 1
        else:
            n_gen += 1
    print(
        f"  summary generated={n_gen} overlays={n_edit} "
        f"lock={n_lock} omit={n_omit} dirty={n_dirty}"
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("stamp", "status"))
    p.add_argument("--book", action="append")
    args = p.parse_args()
    slugs = args.book or BOOKS
    if args.command == "stamp":
        for slug in slugs:
            book = book_dir(slug)
            n, locked = stamp_book(book)
            print(f"{slug}: stamped {n} generated, {locked} lock/omit skipped")
        return
    for slug in slugs:
        status_book(book_dir(slug))


if __name__ == "__main__":
    main()

"""Drop MediaWiki interwiki links. They do not resolve in the book."""

from __future__ import annotations

import re
from pathlib import Path

# http(s) etc. stay. Wiki namespaces stay (Category:/User:/File:).
# Everything else with a scheme-like prefix (hitch:, trash:, wikipedia:) goes.
_KEEP_SCHEMES = frozenset(
    {"http", "https", "mailto", "ftp", "ftps", "irc", "geo", "tel"}
)
_KEEP_NAMESPACES = frozenset(
    {
        "category",
        "file",
        "image",
        "media",
        "special",
        "talk",
        "user",
        "template",
        "help",
        "module",
        "mediawiki",
        "project",
    }
)

_PREFIX = re.compile(r"^:?([A-Za-z][A-Za-z0-9]*):")
_WIKITEXT_IW = re.compile(
    r"\[\[:?([A-Za-z][A-Za-z0-9]*):([^\]|]+)(?:\|([^\]]+))?\]\]"
)
_MD_IW = re.compile(
    r"\[([^\]]*)\]\("
    r"(:?[A-Za-z][A-Za-z0-9]*:[^)\s]*)"
    r"(?:\s+\"[^\"]*\")?"
    r"\)(?:\{\.wikilink\})?",
    re.I,
)
_HTML_IW = re.compile(
    r"<a\s+([^>]*href=\"(:?[A-Za-z][A-Za-z0-9]*:[^\"]*)\"[^>]*)>"
    r"(.*?)</a>",
    re.I | re.S,
)


def is_interwiki_prefix(prefix: str) -> bool:
    p = prefix.lower().lstrip(":")
    if p in _KEEP_SCHEMES or p in _KEEP_NAMESPACES:
        return False
    return bool(re.fullmatch(r"[a-z][a-z0-9]{0,31}", p))


def is_interwiki_target(target: str) -> bool:
    m = _PREFIX.match(target.strip())
    return bool(m and is_interwiki_prefix(m.group(1)))


def _keep_label(label: str, target: str) -> str:
    label = re.sub(r"\s+", " ", (label or "").strip())
    if not label:
        return ""
    if is_interwiki_target(label):
        return ""
    rest = _PREFIX.sub("", target).replace("_", " ").strip(" :")
    folded = label.casefold()
    if folded in {
        target.casefold(),
        target.replace("_", " ").casefold(),
        rest.casefold(),
    }:
        return ""
    return label


def strip_interwiki_wikitext(text: str) -> str:
    def repl(m: re.Match) -> str:
        if not is_interwiki_prefix(m.group(1)):
            return m.group(0)
        return (m.group(3) or "").strip()

    return _tidy(_WIKITEXT_IW.sub(repl, text))


def strip_interwiki_markdown(text: str) -> str:
    def repl(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if not is_interwiki_target(target):
            return m.group(0)
        return _keep_label(label, target)

    return _tidy(_MD_IW.sub(repl, text))


def strip_interwiki_html(text: str) -> str:
    def repl(m: re.Match) -> str:
        target, body = m.group(2), m.group(3)
        if not is_interwiki_target(target):
            return m.group(0)
        inner = re.sub(r"<[^>]+>", "", body)
        return _keep_label(inner, target)

    return _HTML_IW.sub(repl, text)


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n- +\n", "\n", text)
    text = re.sub(r"(?<=\S) {2,}(?=\S)", " ", text)
    text = re.sub(r" +([.,;:!?])", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def rewrite_markdown_tree(root: Path) -> int:
    n = 0
    for path in sorted(root.rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        updated = strip_interwiki_markdown(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            n += 1
    return n

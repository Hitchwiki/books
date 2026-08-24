#!/usr/bin/env python3
"""Serve the local catalog and open it in a browser."""

from __future__ import annotations

import argparse
import http.server
import json
import sys
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "build" / "site"
_BIDI = str.maketrans("", "", "\u200e\u200f\u202a\u202b\u202c\u202d\u202e")


def clean_path(path: str) -> str:
    return unquote(urlparse(path).path).translate(_BIDI)


def load_aliases(site: Path) -> dict[str, Path]:
    """Wiki filenames in HTML → saved JPEGs under each book's images/."""
    aliases: dict[str, Path] = {}
    for book_dir in site.iterdir():
        img_dir = book_dir / "images"
        manifest = img_dir / "images.json"
        if not book_dir.is_dir() or not manifest.is_file():
            continue
        try:
            entries = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for entry in entries:
            dest_name = entry.get("file") or ""
            dest = img_dir / dest_name
            if not dest_name or not dest.is_file():
                continue
            names = {dest_name}
            source = entry.get("source") or ""
            if source:
                names.add(unquote(urlparse(source).path.rsplit("/", 1)[-1]))
            for name in names:
                name = name.strip().strip("\u200e\u200f")
                if not name:
                    continue
                for key in {name, name.replace(" ", "_")}:
                    aliases[f"/{book_dir.name}/{key}"] = dest
                    aliases[f"/{book_dir.name}/images/{key}"] = dest
            aliases[f"/{book_dir.name}/images/{dest_name}"] = dest
    return aliases


def open_browser(url: str) -> None:
    time.sleep(0.2)
    if sys.platform == "darwin":
        import subprocess

        subprocess.run(["open", url], check=False)
    else:
        webbrowser.open(url, new=1, autoraise=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    aliases: dict[str, Path] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def translate_path(self, path: str) -> str:
        dest = self.aliases.get(clean_path(path))
        if dest is not None:
            return str(dest)
        return super().translate_path(path)

    def _favicon(self) -> bool:
        if clean_path(self.path) != "/favicon.ico":
            return False
        self.send_response(204)
        self.end_headers()
        return True

    def do_GET(self) -> None:
        if self._favicon():
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._favicon():
            return
        super().do_HEAD()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


class Server(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    p = argparse.ArgumentParser(description="Serve the local book catalog.")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = p.parse_args()
    if not (SITE / "index.html").is_file():
        print("no local site yet — run: make all", file=sys.stderr)
        sys.exit(1)
    Handler.aliases = load_aliases(SITE)
    try:
        httpd = Server(("127.0.0.1", args.port), Handler)
    except OSError:
        print(f"port {args.port} in use — try --port 8001", file=sys.stderr)
        sys.exit(1)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"serving {SITE} at {url}", flush=True)
    if not args.no_open:
        threading.Thread(target=open_browser, args=(url,), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(flush=True)
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()

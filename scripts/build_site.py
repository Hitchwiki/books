#!/usr/bin/env python3
"""Write the books.hitchwiki.org catalog homepage."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import github_icon_link
from themes import THEMES, fonts_dir, logos_dir

BOOKS = list(THEMES)
LANG_ORDER = ["en", "nl", "es"]
LANG_LABELS = {"en": "English", "nl": "Nederlands", "es": "Español"}


def nostr_reading_list(edition: str) -> list[dict[str, str]]:
    entries = []
    for slug in BOOKS:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        entries.append(
            {
                "id": f"books.hitchwiki.org:{slug}",
                "title": str(meta.get("title") or slug),
                "author": str(meta.get("author") or ""),
                "language": str(meta.get("lang") or ""),
                "format": "epub",
                "url": f"https://books.hitchwiki.org/downloads/{slug}-{edition}.epub",
            }
        )
    return entries


def version_stamp(raw: str | None) -> str:
    if raw:
        return raw
    return "0.1-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")


def build_when(version: str) -> dt.datetime:
    parts = version.rsplit("-", 2)
    if len(parts) >= 2:
        date_part, time_part = parts[-2], parts[-1]
        if len(date_part) == 8 and date_part.isdigit() and len(time_part) == 4 and time_part.isdigit():
            return dt.datetime.strptime(date_part + time_part, "%Y%m%d%H%M").replace(
                tzinfo=dt.timezone.utc
            )
    return dt.datetime.now(dt.timezone.utc)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--version", default="")
    p.add_argument("--out", default="build/site")
    args = p.parse_args()
    version = version_stamp(args.version or None)
    when = build_when(version)
    built = when.strftime("%Y-%m-%d %H:%M")
    built_iso = when.strftime("%Y-%m-%dT%H:%M:00Z")
    edition = version.split("-", 1)[0]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"
    assets.mkdir(exist_ok=True)
    covers_src = ROOT / "assets" / "covers"
    covers_dest = assets / "covers"
    covers_dest.mkdir(exist_ok=True)
    catalog_css = ROOT / "assets" / "catalog.css"
    if catalog_css.exists():
        shutil.copy2(catalog_css, assets / "catalog.css")
    favicon = ROOT / "assets" / "favicon.ico"
    if favicon.exists():
        shutil.copy2(favicon, out / "favicon.ico")
    font_dest = assets / "fonts"
    font_dest.mkdir(exist_ok=True)
    if fonts_dir().exists():
        for ttf in fonts_dir().glob("*.ttf"):
            shutil.copy2(ttf, font_dest / ttf.name)
    logos_dest = assets / "logos"
    logos_dest.mkdir(exist_ok=True)
    masthead_logo = ROOT / "assets" / "logos" / "hitchhikers-guide.png"
    if masthead_logo.exists():
        shutil.copy2(masthead_logo, logos_dest / "hitchhikers-guide.png")

    def card_html(slug: str) -> str:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {"title": slug}
        title = meta.get("title", slug)
        pdf = out / "downloads" / f"{slug}-{edition}.pdf"
        epub = f'<a href="./downloads/{slug}-{edition}.epub">EPUB</a>'
        pdf_link = f' · <a href="./downloads/{slug}-{edition}.pdf">PDF</a>' if pdf.exists() else ""
        cover = covers_src / f"{slug}.jpg"
        cover_html = ""
        if cover.exists():
            shutil.copy2(cover, covers_dest / f"{slug}.jpg")
            cover_html = f'<a class="cover" href="./{slug}/"><img src="./assets/covers/{slug}.jpg" alt=""></a>'
        logo_name = THEMES[slug].get("logo")
        if logo_name:
            src_logo = logos_dir() / logo_name
            if src_logo.exists():
                shutil.copy2(src_logo, logos_dest / logo_name)
        return f"""<article class="card card-{slug}">
  <a class="open" href="./{slug}/" aria-label="Read {title}"></a>
  {cover_html}
  <div class="card-body">
    <p class="formats">
      {epub}{pdf_link}
    </p>
  </div>
</article>"""

    by_lang: dict[str, list[str]] = {}
    for slug in BOOKS:
        meta_path = ROOT / "books" / slug / "metadata.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        lang = meta.get("lang") or "en"
        by_lang.setdefault(lang, []).append(slug)
    sections = []
    seen = set()
    for lang in [*LANG_ORDER, *by_lang]:
        if lang in seen or lang not in by_lang:
            continue
        seen.add(lang)
        label = LANG_LABELS.get(lang, lang)
        heading = f'    <h2 class="lang-label">{label}</h2>\n' if lang != "en" else ""
        cards = "".join(card_html(slug) for slug in by_lang[lang])
        sections.append(
            f'''  <section class="lang" lang="{lang}">
{heading}    <div class="grid">
    {cards}
    </div>
  </section>'''
        )
    nostr_books = json.dumps(nostr_reading_list(edition), ensure_ascii=False).replace("</", "<\\/")
    nostr_script = """  <script>
    const readingList=__NOSTR_BOOKS__,nostrAction=document.querySelector('#nostr-action'),nostrSave=document.querySelector('#nostr-save'),nostrStatus=document.querySelector('#nostr-status'),nostrVisibility=document.querySelector('#nostr-visibility'),nostrCopy=document.querySelector('#nostr-copy'),relay='wss://relay.nomadwiki.org';
    function publish(event){return new Promise((resolve,reject)=>{let socket,done=false;const finish=error=>{if(done)return;done=true;clearTimeout(timer);try{socket?.close()}catch{}error?reject(error):resolve()};const timer=setTimeout(()=>finish(new Error('Relay timed out.')),8000);try{socket=new WebSocket(relay);socket.addEventListener('open',()=>socket.send(JSON.stringify(['EVENT',event])));socket.addEventListener('message',message=>{try{const packet=JSON.parse(message.data);if(packet[0]==='OK'&&packet[1]===event.id)packet[2]?finish():finish(new Error(packet[3]||'Relay rejected the list.'))}catch{}});socket.addEventListener('error',()=>finish(new Error('Could not connect to the Nostr relay.')))}catch(error){finish(error)}})}
    async function saveToNostr(){if(!window.nostr?.getPublicKey||!window.nostr?.signEvent)throw new Error('No NIP-07 signer found.');const pubkey=await window.nostr.getPublicKey(),now=Math.floor(Date.now()/1000),privateList=nostrVisibility.value==='private',listTags=[['title','Hitchwiki Books'],['description','All EPUB editions from books.hitchwiki.org.'],['r','https://books.hitchwiki.org/'],...readingList.flatMap(book=>[['r',book.url],['book','bookstr',book.id,String(now),book.url],['bookstr-book',book.id,book.title,book.author,'epub','0','',book.url,book.language,'books.hitchwiki.org']])];let tags=[['d','hitchwiki-books']],content='';if(privateList){if(typeof window.nostr?.nip44?.encrypt!=='function')throw new Error('Private lists require NIP-44 support from your signer.');content=await window.nostr.nip44.encrypt(pubkey,JSON.stringify(listTags))}else{tags.push(...listTags)}const event=await window.nostr.signEvent({kind:30003,created_at:now,tags,content});await publish(event);return privateList}
    async function handleSave(){nostrSave.disabled=true;nostrStatus.textContent='Waiting for your signer…';try{const privateList=await saveToNostr();nostrStatus.textContent=`Saved ${readingList.length} EPUBs as a ${privateList?'private':'public'} Nostr list.`}catch(error){nostrStatus.textContent=error?.message||String(error)}finally{nostrSave.disabled=false}}
    function updateVisibilityCopy(){nostrCopy.textContent=nostrVisibility.value==='private'?'Save the EPUB entries encrypted for your own Nostr key. The list identifier remains visible on relays.':"Publish all Hitchwiki Books EPUBs as a public NIP-51 list using your browser's NIP-07 signer."}
    function revealNostr(){if(window.nostr?.getPublicKey&&window.nostr?.signEvent)nostrAction.hidden=false}
    nostrSave.addEventListener('click',handleSave);nostrVisibility.addEventListener('change',updateVisibilityCopy);updateVisibilityCopy();revealNostr();setTimeout(revealNostr,500);setTimeout(revealNostr,1500);
  </script>""".replace("__NOSTR_BOOKS__", nostr_books)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hitchwiki Books</title>
  <link rel="icon" href="./favicon.ico?v={version}" sizes="any">
  <link rel="stylesheet" href="./assets/catalog.css?v={version}">
</head>
<body class="catalog">
  <header>
    <h1><span class="masthead-logo"><img src="./assets/logos/hitchhikers-guide.png?v={version}" alt="Hitchwiki" width="144" height="152"></span><span class="masthead-title">BOOKS</span><span class="masthead-version">0.1</span></h1>
  </header>
{chr(10).join(sections)}
  <section id="nostr-action" class="nostr-action" hidden>
    <h2>Keep this EPUB collection</h2>
    <p id="nostr-copy">Publish all Hitchwiki Books EPUBs as a public NIP-51 list using your browser's NIP-07 signer.</p>
    <div class="nostr-controls">
      <label for="nostr-visibility">Visibility
        <select id="nostr-visibility"><option value="public">Public</option><option value="private">Private</option></select>
      </label>
      <button id="nostr-save" type="button">Save “Hitchwiki Books” to Nostr</button>
    </div>
    <p id="nostr-status" class="nostr-status" aria-live="polite"></p>
    <p class="nostr-reader">Suggested reader: <a href="https://books.guaka.org/">Bookstr at books.guaka.org</a>.</p>
  </section>
  <p class="lede">A growing collection of freely licensed books. Created by thousands of people over two decades.</p>
  <p class="foot">© 2004–2026 respective contributors. Content licenses live with each book. {github_icon_link()} Built <time datetime="{built_iso}">{built}</time>.</p>
{nostr_script}
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(f"catalog {version} -> {out}")


if __name__ == "__main__":
    main()

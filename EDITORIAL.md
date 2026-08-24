# Editorial guidelines

These books are compiled editions of living wikis and sites, plus a little original writing. Wikis stay the source of truth for facts that change. This repo shapes a book: order, cuts, notes, original chapters, versioned snapshot, cover and type.

These guidelines apply to every book in the repository. A book may add more specific guidance in `books/<slug>/EDITORIAL.md`; that guidance supplements this file and takes precedence for that book if the two conflict.

## AI-assisted text

Do not use AI to generate, rewrite, or edit book text unless the user specifically requests that work.

## How a build works

```
dumps/  →  make fetch  →  books/<slug>/src/*.md  →  make covers && make all
```

`make fetch` must not wipe local work. It rewrites the generated middle of a chapter only when that middle still matches the last compile (`editorial/upstream.json`). Locked/original files are left alone.

| Layer | Where | Refresh from wiki? |
| --- | --- | --- |
| Generated | most of `src/` from dumps | yes, unless dirty/locked |
| Overlay | `<!-- editorial:before -->` / `after` | kept on fetch |
| Locked | `<!-- editorial:lock -->` or `editorial/lock.txt` | never |
| Omitted | `<!-- editorial:omit -->` or `editorial/omit.txt` | not in the book |

```sh
make fetch
.venv/bin/python scripts/editorial.py stamp
.venv/bin/python scripts/editorial.py status
make covers   # per-book JPEG + CSS
make all
```

## Which pages to use

Allowlists live in `scripts/titles.py` and Drupal skip-types in `scripts/compile_drupal_sql.py`.

**Book shape (Hitchwiki, Trashwiki, Nomadwiki):** generic practice first (`01-practice`), then a geo section (`02-countries`, Europe first, then North America and the rest of the Americas, then other regions; curated cities nested under the matching country with capitals and the main cities first), then original outlook (`04-outlook`) that sends people out to try it and to edit the live wiki.

**Use:** evergreen how-to; country overviews; Drupal stories/tips; locked originals (front matter, part intros, outlook, history commentary, software described-not-dumped, granted forewords). A curated city set is optional and must strip pin lists.

**Do not use:** `User:`/`Talk:`/`File:`/`Template:` chrome; continent hubs as empty chapters; named ramps/dumpsters/hostels/GPS; supermarket brand pages; shoplifting; member PII; CS.com / Couchers brand; WikiLeaks reprint; software source; Drupal polls/ads/forums; Random Roads third-party book reviews; Nomadwiki pages that belong in another book (stub + pointer); NC text in a BY-SA book; wiki news/news-archive pages (stale the day they are compiled); interwiki sister links (`hitch:`, `trash:`, `nomad:`, `wikipedia:`, and the rest — they do not resolve in the book).

## Prefer the wiki when

A fact should live on Hitchwiki / Trashwiki / Nomadwiki / Trustroots Wiki. Pins go stale — point at maps.hitchwiki.org / dumpstermap.org / the live wiki.

## Prefer the book when

Front matter, part order, outlook, edition cuts, cross-book pointers, original chapters, licensed summaries. If both: wiki first, then a short `editorial:before` note. Facts that change (visas, pins, which bins are locked) stay on the wiki. The invitation to go do this, and to write the next page, lives in the book.

## How to edit a generated chapter

```markdown
<!-- editorial:before -->
> Edition note (2026): check the live wiki for visa rules.
<!-- /editorial:before -->
```

Take over a whole chapter with `<!-- editorial:lock -->`. Drop one with omit. Do not silently rewrite the generated middle after `editorial.py stamp` — fetch will conflict into `build/editorial-conflicts/`.

## Design

Each book has its own cover, type, and colors in `scripts/themes.py`. Do not share one stylesheet across titles.

Do not use AI-generated images anywhere in these books, including covers, chapter art, illustrations, or promotional assets. Use real photographs, archival images, or human-made artwork with a traceable source and a compatible license, and preserve the required attribution.

Do not use the same image twice in a book. The exception is a cover image that also appears inside (for example on the title page or as a chapter opener). A wiki dump that repeats a photo across chapters should keep one placement and drop the rest.

## Originals and forewords

Lock originals so compile cannot clobber them. Forewords, when granted, go in `src/00-foreword.md`. Log license in `SOURCES.md`.

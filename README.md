# Freely licensed books

Catalog currently at **[guaka.github.io/books](https://guaka.github.io/books/)**. Custom domain [books.hitchwiki.org](https://books.hitchwiki.org/) later. Source: [github.com/guaka/books](https://github.com/guaka/books).

Each book has **its own license**. There is no repo-wide content license. Scripts in this repository are MIT (see [LICENSE](LICENSE)). Two content licenses:

| [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](https://creativecommons.org/licenses/by-sa/4.0/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| --- | --- |
| Hitchwiki, Trustroots Wiki, Nomadwiki | Trashwiki, Random Roads, Dumpsterdam, Geldloos, Moneyless, Sin Dinero |

| Book | License | Sources |
| --- | --- | --- |
| [The Hitchhiker's Guide to Hitchhiking](https://guaka.github.io/books/hitchhikers-guide/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/hitchhikers-guide/LICENSE) | Hitchwiki |
| [Dumpster Diving](https://guaka.github.io/books/dumpster-diving/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/dumpster-diving/LICENSE) | Trashwiki |
| [Random Roads](https://guaka.github.io/books/random-roads/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/random-roads/LICENSE) | randomroads.org |
| [Dumpsterdam](https://guaka.github.io/books/dumpsterdam/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/dumpsterdam/LICENSE) | dumpsterdam.nl |
| [Geldloos](https://guaka.github.io/books/geldloos/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/geldloos/LICENSE) | geldloos.nl |
| [Hospitality Exchange](https://guaka.github.io/books/hospitality-exchange/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/hospitality-exchange/LICENSE) | Trustroots Wiki and related |
| [Moneyless](https://guaka.github.io/books/moneyless/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/moneyless/LICENSE) | moneyless.org |
| [Sin Dinero](https://guaka.github.io/books/sin-dinero/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/sin-dinero/LICENSE) | sindinero.net |
| [Shoestring Nomad](https://guaka.github.io/books/shoestring-nomad/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/shoestring-nomad/LICENSE) | Nomadwiki, Casa Robino |

See [SOURCES.md](SOURCES.md) for adjacent sites, permission notes, and titles wanted later (philosophy / free software / abundance / AI / wikis). See [EDITORIAL.md](EDITORIAL.md) for how to edit chapters so wiki updates do not wipe them. See [PUBLISH.md](PUBLISH.md) for print and stores (KDP, Lulu, Ingram, D2D, itch.io, Internet Archive). NC-SA stays off paid stores.

Each book has its own cover, type, and colors from the related website (`make covers`, `scripts/themes.py`). See each book’s `DESIGN.md` for logos and hex values.

Wiki XML/ZIM dumps belong in `dumps/` (gitignored). Resized JPEGs in `books/*/images/` are also gitignored; keep `images.json`. Restore with `make images` (disk, then the `images` GitHub Release, then the live site, then wiki). Refresh the archive with `make images-release`.

Server copies (gitignored under `dumps/`):

- Hitchwiki/Nomadwiki/Trustroots/Trashwiki XML+ZIM from [dumps.hitchwiki.org](https://dumps.hitchwiki.org/)
- Optional private SQL / Drupal node dumps via `scripts/pull_server_dumps.sh` (SSH hosts in gitignored `local/hosts.env`; page content only, no user tables)

```sh
cp local/hosts.env.example local/hosts.env   # then set the SSH hosts
scripts/pull_server_dumps.sh
python3 scripts/compile_drupal_sql.py
```

Builds are versioned `0.1-yyyymmdd-hhmm` (UTC).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
make fetch   # dumps into dumps/, then compile chapters (keeps locks / editorial notes)
make images  # disk, GitHub release `images`, live site, then wiki URLs
make images-release  # pack JPEGs and upload/update the `images` release
make         # open the catalog at http://127.0.0.1:8000/
make all     # EPUB, PDF (if a PDF engine exists), HTML
```

Do not mix chapters across books. CC-BY-SA and CC-BY-NC-SA are not one work.

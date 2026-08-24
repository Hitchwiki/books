# Freely licensed books

Catalog currently at **[guaka.github.io/books](https://guaka.github.io/books/)**. Custom domain [books.hitchwiki.org](https://books.hitchwiki.org/) later. Source: [github.com/guaka/books](https://github.com/guaka/books).

Each book has **its own license**. There is no repo-wide content license. Scripts in this repository are MIT (see [LICENSE](LICENSE)). Two content licenses:

| [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](https://creativecommons.org/licenses/by-sa/4.0/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| --- | --- |
| Hitchwiki, Trustroots Wiki, Nomadwiki | Trashwiki, Random Roads, Dumpsterdam, Moneyless |

| Book | License | Sources |
| --- | --- | --- |
| [The Hitchhiker's Guide to Hitchhiking](books/hitchhikers-guide/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/hitchhikers-guide/LICENSE) | Hitchwiki |
| [Dumpster Diving](books/dumpster-diving/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/dumpster-diving/LICENSE) | Trashwiki |
| [Random Roads](books/random-roads/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/random-roads/LICENSE) | randomroads.org |
| [Dumpsterdam](books/dumpsterdam/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/dumpsterdam/LICENSE) | dumpsterdam.nl |
| [Hospitality Exchange](books/hospitality-exchange/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/hospitality-exchange/LICENSE) | Trustroots Wiki and related |
| [Moneyless](books/moneyless/) | [![CC BY-NC-SA 4.0](assets/cc-by-nc-sa-4.0.png)](books/moneyless/LICENSE) | moneyless.org, geldloos.nl, sindinero.net |
| [Shoestring Nomad](books/shoestring-nomad/) | [![CC BY-SA 4.0](assets/cc-by-sa-4.0.png)](books/shoestring-nomad/LICENSE) | Nomadwiki, Casa Robino |

See [SOURCES.md](SOURCES.md) for adjacent sites, permission notes, and titles wanted later (philosophy / free software / abundance / AI / wikis). See [EDITORIAL.md](EDITORIAL.md) for how to edit chapters so wiki updates do not wipe them.

Wiki XML/ZIM dumps belong in `dumps/` (gitignored). Resized JPEGs in `books/*/images/` are also gitignored; keep `images.json` and restore with `make images`.

Server copies (also gitignored):

- Hitchwiki/Nomadwiki/Trustroots/Trashwiki XML+ZIM from [dumps.hitchwiki.org](https://dumps.hitchwiki.org/)
- Trashwiki MySQL from `h.bfr.ee:/var/backups/mysql/sqldump/` (page content only used)
- Drupal node dumps from `d7.bfr.ee` (randomroads, dumpsterdam, moneyless, geldloos, sindinero, casarobino). User tables are not copied.

```sh
scripts/pull_server_dumps.sh   # SSH to h.bfr.ee and d7.bfr.ee
python3 scripts/compile_drupal_sql.py
```

Builds are versioned `0.1-yyyymmdd-hhmm` (UTC).

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
make fetch   # dumps into dumps/, then compile chapters (keeps locks / editorial notes)
make images  # JPEGs already on disk, else live site, else wiki URLs
make all     # EPUB, PDF (if a PDF engine exists), HTML
```

Do not mix chapters across books. CC-BY-SA and CC-BY-NC-SA are not one work.

# Freely licensed books

Catalog currently at **[guaka.github.io/books](https://guaka.github.io/books/)**. Custom domain [books.hitchwiki.org](https://books.hitchwiki.org/) later. Source: [github.com/guaka/books](https://github.com/guaka/books).

Each book has **its own license**. There is no repo-wide content license. Scripts in this repository are MIT (see [LICENSE](LICENSE)).

| Book | License | Sources |
| --- | --- | --- |
| [The Hitchhiker's Guide to Hitchhiking](books/hitchhikers-guide/) | [CC-BY-SA-4.0](books/hitchhikers-guide/LICENSE) | Hitchwiki |
| [Dumpster Diving](books/dumpster-diving/) | [CC-BY-NC-SA-3.0](books/dumpster-diving/LICENSE) | Trashwiki |
| [Random Roads](books/random-roads/) | [CC-BY-NC-SA-4.0](books/random-roads/LICENSE) | randomroads.org |
| [Dumpsterdam](books/dumpsterdam/) | [CC-BY-NC-SA-4.0](books/dumpsterdam/LICENSE) | dumpsterdam.nl |
| [Hospitality Exchange](books/hospitality-exchange/) | [CC-BY-SA-4.0](books/hospitality-exchange/LICENSE) | Trustroots Wiki and related |
| [Moneyless](books/moneyless/) | [CC-BY-NC-SA-4.0](books/moneyless/LICENSE) | moneyless.org, geldloos.nl, sindinero.net |
| [Shoestring Nomad](books/shoestring-nomad/) | [CC-BY-SA-4.0](books/shoestring-nomad/LICENSE) | Nomadwiki, Casa Robino |

See [SOURCES.md](SOURCES.md) for adjacent sites and permission notes.

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
make fetch   # dumps into dumps/, then compile chapters
make images  # re-download JPEGs listed in images.json
make all     # EPUB, PDF (if a PDF engine exists), HTML
```

Do not mix chapters across books. CC-BY-SA and CC-BY-NC-SA are not one work.

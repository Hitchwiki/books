VERSION ?= 0.1-$(shell date -u +%Y%m%d-%H%M)
PYTHON  ?= $(firstword $(wildcard $(CURDIR)/.venv/bin/python3) python3)
PANDOC  ?= pandoc
BOOKS   := hitchhikers-guide dumpster-diving random-roads dumpsterdam hospitality-exchange moneyless shoestring-nomad
OUT     := build
SITE    := $(OUT)/site

.PHONY: all books dumps fetch images site html epub pdf clean $(BOOKS)

all: books site

books: $(BOOKS)

html epub pdf: books

dumps:
	mkdir -p dumps/zim dumps/sql
	test -s dumps/hitchwiki-current-en.xml.gz || curl -fL --retry 3 -o dumps/hitchwiki-current-en.xml.gz https://dumps.hitchwiki.org/hitchwiki-current-en.xml.gz
	test -s dumps/nomadwiki-current.xml.gz || curl -fL --retry 3 -o dumps/nomadwiki-current.xml.gz https://dumps.hitchwiki.org/nomadwiki-current.xml.gz
	test -s dumps/trustroots-current.xml.gz || curl -fL --retry 3 -o dumps/trustroots-current.xml.gz https://dumps.hitchwiki.org/trustroots-current.xml.gz
	test -s dumps/zim/trashwiki-zim.latest.zim || curl -fL --retry 3 -o dumps/zim/trashwiki-zim.latest.zim https://dumps.hitchwiki.org/zim/trashwiki-zim.latest.zim

fetch: dumps
	$(PYTHON) scripts/fetch_mediawiki.py --all
	$(PYTHON) scripts/compile_drupal_sql.py

images:
	$(PYTHON) scripts/fetch_images.py

$(BOOKS):
	$(PYTHON) scripts/build_book.py --book $@ --version $(VERSION) --formats html,epub,pdf --out $(OUT)

site:
	$(PYTHON) scripts/build_site.py --version $(VERSION) --out $(SITE)
	cp CNAME $(SITE)/CNAME

clean:
	rm -rf $(OUT)

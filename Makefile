VERSION ?= 0.1-$(shell date -u +%Y%m%d-%H%M)
PYTHON  ?= $(firstword $(wildcard $(CURDIR)/.venv/bin/python3) python3)
PANDOC  ?= pandoc
BOOKS   := hitchhikers-guide dumpster-diving random-roads dumpsterdam geldloos hospitality-exchange moneyless sin-dinero shoestring-nomad
FORMATS ?= html,epub,pdf
OUT     := build
SITE    := $(OUT)/site

.DEFAULT_GOAL := serve

.PHONY: all covers books dumps fetch images pack-images images-release site catalog html epub pdf pages serve clean editorial-status $(BOOKS)

all: books site

books: $(BOOKS)

html epub pdf: books

pages: FORMATS := html,epub,pdf
pages: all

dumps:
	mkdir -p dumps/zim dumps/sql
	test -s dumps/hitchwiki-current-en.xml.gz || curl -fL --retry 3 -o dumps/hitchwiki-current-en.xml.gz https://dumps.hitchwiki.org/hitchwiki-current-en.xml.gz
	test -s dumps/nomadwiki-current.xml.gz || curl -fL --retry 3 -o dumps/nomadwiki-current.xml.gz https://dumps.hitchwiki.org/nomadwiki-current.xml.gz
	test -s dumps/trustroots-current.xml.gz || curl -fL --retry 3 -o dumps/trustroots-current.xml.gz https://dumps.hitchwiki.org/trustroots-current.xml.gz
	test -s dumps/zim/trashwiki-zim.latest.zim || curl -fL --retry 3 -o dumps/zim/trashwiki-zim.latest.zim https://dumps.hitchwiki.org/zim/trashwiki-zim.latest.zim

fetch: dumps
	$(PYTHON) scripts/fetch_mediawiki.py --all
	$(PYTHON) scripts/compile_drupal_sql.py

covers:
	$(PYTHON) scripts/render_covers.py

images:
	$(PYTHON) scripts/fetch_images.py

pack-images:
	$(PYTHON) scripts/pack_images.py

images-release:
	$(PYTHON) scripts/pack_images.py --upload

editorial-status:
	$(PYTHON) scripts/editorial.py status

$(BOOKS):
	$(PYTHON) scripts/build_book.py --book $@ --version $(VERSION) --formats $(FORMATS) --out $(OUT)

site: books
	$(PYTHON) scripts/build_site.py --version $(VERSION) --out $(SITE)

catalog:
	$(PYTHON) scripts/build_site.py --version $(VERSION) --out $(SITE)

serve:
	$(PYTHON) scripts/serve.py

clean:
	rm -rf $(OUT)

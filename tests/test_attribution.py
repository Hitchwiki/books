import json
import gzip
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_book import attribution_markdown
from wiki_contributors import contributor_sort_key, source_titles, xml_contributors


class AttributionTests(unittest.TestCase):
    def test_wiki_usernames_are_rendered_alphabetically_from_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp)
            (book / "editorial").mkdir()
            (book / "editorial" / "wiki-contributors.json").write_text(
                json.dumps(
                    {
                        "contributors": ["alice", "Bob", "Zoë"],
                        "anonymous_contributors": True,
                    }
                ),
                encoding="utf-8",
            )
            output = attribution_markdown(
                book,
                {
                    "lang": "en",
                    "author": "Wiki contributors",
                    "source": "https://example.org/",
                    "license": "CC-BY-SA-4.0",
                },
                [],
            )

        self.assertIn("alice, Bob, Zoë", output)
        self.assertIn("Anonymous contributors", output)
        self.assertTrue(output.startswith("# Attribution\n"))

    def test_non_wiki_book_still_has_an_attribution_section(self):
        output = attribution_markdown(
            Path("/does/not/exist"),
            {"lang": "es", "author": "Ana", "source": "https://example.org/"},
            [],
        )
        self.assertIn("# Atribución", output)
        self.assertIn("**Ana**", output)

    def test_source_titles_only_uses_matching_wiki(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp)
            (book / "src").mkdir()
            (book / "src" / "one.md").write_text(
                "Source: [São Paulo](https://wiki.example/en/S%C3%A3o_Paulo)\n"
                "Source: [Elsewhere](https://other.example/en/Elsewhere)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                source_titles(book, "https://wiki.example/en/"), ["São Paulo"]
            )

    def test_contributor_sort_is_case_insensitive(self):
        self.assertEqual(
            sorted(["zoe", "Alice", "bob"], key=contributor_sort_key),
            ["Alice", "bob", "zoe"],
        )

    def test_full_xml_collects_all_registered_revisions_without_ips(self):
        xml = b'''<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/">
          <page><title>Included Page</title>
            <revision><contributor><username>Zo\xc3\xab</username></contributor></revision>
            <revision><contributor><ip>192.0.2.1</ip></contributor></revision>
            <revision><contributor><username>alice</username></contributor></revision>
          </page>
          <page><title>Other Page</title>
            <revision><contributor><username>Ignored</username></contributor></revision>
          </page>
        </mediawiki>'''
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "full.xml.gz"
            with gzip.open(dump, "wb") as stream:
                stream.write(xml)
            names, anonymous = xml_contributors(dump, ["Included Page"])

        self.assertEqual(names, ["alice", "Zo\u00eb"])
        self.assertTrue(anonymous)


if __name__ == "__main__":
    unittest.main()

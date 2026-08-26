import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILTER = ROOT / "scripts" / "reader_links.lua"


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
class ReaderLinkFilterTests(unittest.TestCase):
    def render(self, markdown: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.md"
            source.write_text(markdown, encoding="utf-8")
            return subprocess.run(
                ["pandoc", "-f", "markdown", "-t", "html5", "--lua-filter", str(FILTER), str(source)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout

    def test_unwraps_wikilinks_and_preserves_inline_formatting(self):
        rendered = self.render('[**Hosts**](Host "Host"){.wikilink}')
        self.assertEqual(rendered.strip(), "<p><strong>Hosts</strong></p>")

    def test_unwraps_relative_and_root_relative_links(self):
        rendered = self.render("[relative](another-page) [root](/old/path)")
        self.assertEqual(rendered.strip(), "<p>relative root</p>")

    def test_unwraps_cms_navigation_but_keeps_resources(self):
        rendered = self.render(
            "[tag](https://example.org/tags/food) "
            "[profile](https://example.org/user/alice) "
            "[search](https://example.org/search?q=hosts) "
            "[edit](https://example.org/wiki/Page?action=edit) "
            "[history](https://example.org/wiki/Page?action=history) "
            "[map](https://maps.hitchwiki.org/)"
        )
        self.assertNotIn('href="https://example.org/tags/food"', rendered)
        self.assertNotIn('href="https://example.org/user/alice"', rendered)
        self.assertNotIn('href="https://example.org/search?q=hosts"', rendered)
        self.assertNotIn('href="https://example.org/wiki/Page?action=edit"', rendered)
        self.assertIn('href="https://example.org/wiki/Page?action=history"', rendered)
        self.assertIn('href="https://maps.hitchwiki.org/"', rendered)

    def test_keeps_sources_citations_mail_and_fragments(self):
        rendered = self.render(
            "[source](https://wiki.trustroots.org/en/Safety) "
            "[paper](https://example.org/paper.pdf) "
            "[mail](mailto:bookbot@guaka.org) [contents](#contents)"
        )
        self.assertIn('href="https://wiki.trustroots.org/en/Safety"', rendered)
        self.assertIn('href="https://example.org/paper.pdf"', rendered)
        self.assertIn('href="mailto:bookbot@guaka.org"', rendered)
        self.assertIn('href="#contents"', rendered)

    def test_filter_is_idempotent(self):
        once = self.render("[Hosts](Host){.wikilink} [map](https://maps.hitchwiki.org/)")
        twice = self.render(once)
        self.assertIn("Hosts", twice)
        self.assertEqual(twice.count('href="https://maps.hitchwiki.org/"'), 1)


if __name__ == "__main__":
    unittest.main()

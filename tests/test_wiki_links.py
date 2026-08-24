import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from wiki_links import strip_category_markdown, strip_category_wikitext


class CategoryRemovalTests(unittest.TestCase):
    def test_removes_wikitext_category_assignments(self):
        source = "Text.\n[[Category:General info]] [[category:Travel|T]]\n"
        self.assertEqual(strip_category_wikitext(source), "Text.\n \n")

    def test_preserves_deliberate_wikitext_category_links(self):
        source = "See [[:Category:Europe|Europe]] for the regional index."
        self.assertEqual(strip_category_wikitext(source), source)

    def test_removes_pandoc_category_links(self):
        source = (
            "Text.\n\n"
            '[Category:General info](Category:General_info "Category:General info")'
            "{.wikilink} "
            '[*](Category:Europe_(region) "*"){.wikilink}\n'
        )
        self.assertEqual(strip_category_markdown(source), "Text.\n\n\n")

    def test_preserves_deliberate_markdown_category_links(self):
        source = (
            '[Europe](:Category:Europe "Europe"){.wikilink}\n'
            "A normal Category:General info mention.\n"
        )
        self.assertEqual(strip_category_markdown(source), source)


if __name__ == "__main__":
    unittest.main()

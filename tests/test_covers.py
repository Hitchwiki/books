import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from themes import cover_html, cover_rights


class CoverRightsTests(unittest.TestCase):
    def setUp(self):
        self.meta = {
            "title": "Example Book",
            "license": "CC-BY-SA-4.0",
            "rights": "© 2004–2026 respective contributors. CC-BY-SA-4.0.",
        }

    def test_combines_license_and_copyright_years(self):
        self.assertEqual(cover_rights(self.meta), "CC-BY-SA-4.0 🄯 2004–2026")

    def test_html_cover_places_years_with_license(self):
        self.assertIn(
            "<span>CC-BY-SA-4.0 🄯 2004–2026</span>",
            cover_html("hitchhikers-guide", self.meta),
        )

    def test_html_cover_places_version_with_title(self):
        html = cover_html("hitchhikers-guide", self.meta)

        self.assertIn('<span class="cover-version">0.1</span></h1>', html)
        self.assertIn('<span>books.hitchwiki.org</span>', html)
        self.assertNotIn("0.1 · books.hitchwiki.org", html)


if __name__ == "__main__":
    unittest.main()

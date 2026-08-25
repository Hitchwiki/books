import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from common import rewrite_html_images, unwrap_broken_fragment_links, wiki_image_map


class HtmlImageTests(unittest.TestCase):
    def test_wiki_mapping_is_case_insensitive_and_requires_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp)
            (images / "saved.jpg").write_bytes(b"jpeg")
            (images / "images.json").write_text(
                json.dumps(
                    [
                        {
                            "file": "saved.jpg",
                            "source": "https://example.test/Tramprennen_romania.JPG",
                        },
                        {
                            "file": "absent.jpg",
                            "source": "https://example.test/Absent.png",
                        },
                    ]
                ),
                encoding="utf-8",
            )

            mapping = wiki_image_map(images)

            self.assertEqual(mapping["tramprennen_romania.jpg"], "images/saved.jpg")
            self.assertNotIn("absent.png", mapping)

    def test_rewrites_known_image_and_removes_unavailable_figure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "covers").mkdir()
            (root / "covers" / "photo.jpg").write_bytes(b"jpeg")
            html = (
                '<p><img src="tramprennen_romania.JPG"></p>'
                '<figure><img src="Missing.jpg\u200e"><figcaption>Missing</figcaption></figure>'
                '<img src="covers/photo.jpg">'
                '<img src="https://example.test/remote.jpg">'
                '<img src="/sites/old.example/missing.jpg">'
            )

            rewritten = rewrite_html_images(
                html,
                {"tramprennen_romania.jpg": "images/saved.jpg"},
                image_root=root,
            )

            self.assertIn('src="images/saved.jpg"', rewritten)
            self.assertNotIn("Missing.jpg", rewritten)
            self.assertNotIn("<figcaption", rewritten)
            self.assertIn('src="covers/photo.jpg"', rewritten)
            self.assertNotIn("remote.jpg", rewritten)
            self.assertNotIn("old.example", rewritten)

    def test_unwraps_only_fragment_links_without_a_destination(self):
        html = (
            '<h2 id="kept">Heading</h2>'
            '<a href="#kept">working</a>'
            '<a class="wikilink" href="#missing"><em>broken</em></a>'
        )
        rewritten = unwrap_broken_fragment_links(html)
        self.assertIn('<a href="#kept">working</a>', rewritten)
        self.assertIn('<em>broken</em>', rewritten)
        self.assertNotIn('href="#missing"', rewritten)


if __name__ == "__main__":
    unittest.main()

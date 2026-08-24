import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_site import BOOKS, nostr_reading_list


class NostrReadingListTests(unittest.TestCase):
    def test_contains_every_book_as_an_epub_only(self):
        entries = nostr_reading_list("0.1")

        self.assertEqual(len(entries), len(BOOKS))
        self.assertEqual(len({entry["id"] for entry in entries}), len(BOOKS))
        self.assertTrue(all(entry["format"] == "epub" for entry in entries))
        self.assertTrue(all(entry["url"].endswith("-0.1.epub") for entry in entries))
        self.assertFalse(any(".pdf" in entry["url"].lower() for entry in entries))


if __name__ == "__main__":
    unittest.main()

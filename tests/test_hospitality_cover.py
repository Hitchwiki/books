import sys
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from themes import THEMES


class HospitalityCoverTests(unittest.TestCase):
    def test_shared_meal_photo_has_complete_compatible_credit(self):
        photo = THEMES["hospitality-exchange"]["cover_photo"]

        self.assertEqual(photo["commons"], "CS Headquarters in SF .jpg")
        self.assertEqual(photo["author"], "Torrmal")
        self.assertEqual(photo["license"], "CC BY-SA 4.0")
        self.assertEqual(
            photo["page"],
            "https://commons.wikimedia.org/wiki/File:CS_Headquarters_in_SF_.jpg",
        )

    def test_cover_assets_exist_and_are_not_reused_inside_the_book(self):
        rendered_cover = ROOT / "assets" / "covers" / "hospitality-exchange.jpg"
        source_photo = ROOT / "assets" / "covers" / "photos" / "hospitality-exchange.jpg"

        self.assertGreater(rendered_cover.stat().st_size, 20_000)
        self.assertGreater(
            source_photo.stat().st_size,
            20_000,
        )
        with Image.open(rendered_cover) as cover:
            self.assertEqual(cover.size, (1480, 2100))
        with Image.open(source_photo) as photo:
            self.assertEqual(photo.size, (2048, 1536))

        image_manifest = ROOT / "books" / "hospitality-exchange" / "images" / "images.json"
        if image_manifest.exists():
            self.assertNotIn("CS_Headquarters_in_SF", image_manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

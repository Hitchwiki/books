import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_book import chapter_files
from editorial import is_omitted_chapter, is_redirect_chapter
from titles import WIKIS
from toc import editorial_subsections


BOOK = ROOT / "books" / "hospitality-exchange"
SRC = BOOK / "src"
ORDER = BOOK / "editorial" / "order.txt"
GRANDFATHERED_SHORT_GEOGRAPHY = {
    "Eastern Europe",
    "Russia",
    "Southern Europe",
    "Turkey",
    # Explicitly requested country overview; useful cities/regions follow it.
    "Ukraine",
}


def ordered_paths() -> list[str]:
    return [
        line.strip()
        for line in ORDER.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "["))
    ]


class HospitalityStructureTests(unittest.TestCase):
    def test_practice_starts_with_the_priority_reading_order(self):
        actual = [
            path.relative_to(SRC).as_posix()
            for path in chapter_files(BOOK)
            if path.relative_to(SRC).as_posix().startswith("01-practice/")
        ]
        expected = [
            "01-practice/how-to-write-a-hosting-request.md",
            "01-practice/how-to-write-a-request.md",
            "01-practice/searching-and-requesting-a-couch.md",
            "01-practice/how-to-create-a-good-profile.md",
            "01-practice/safety.md",
            "01-practice/host.md",
            "01-practice/profiles.md",
            "01-practice/hospitality-exchange.md",
            "01-practice/how-to-handle-freeloaders.md",
            "01-practice/how-to-handle-couchscroogers.md",
            "01-practice/how-to-organize-a-camp.md",
            "01-practice/how-to-add-my-place.md",
        ]
        self.assertEqual(actual[: len(expected)], expected)

    def test_order_lists_every_geography_chapter_exactly_once(self):
        ordered = [path for path in ordered_paths() if path.startswith("03-countries/")]
        actual = sorted(
            path.relative_to(SRC).as_posix()
            for path in (SRC / "03-countries").glob("*.md")
            if not is_omitted_chapter(BOOK, path) and not is_redirect_chapter(BOOK, path)
        )

        self.assertEqual(sorted(ordered), actual)
        self.assertEqual(len(ordered), len(set(ordered)))

    def test_explicit_geography_manifest_has_no_duplicates_and_resolves(self):
        titles = WIKIS["trustroots"]["country_titles"]
        self.assertEqual(len(titles), len(set(titles)))

        chapter_titles = {
            line.removeprefix("# ").strip()
            for path in (SRC / "03-countries").glob("*.md")
            for line in path.read_text(encoding="utf-8").splitlines()[:1]
        }
        self.assertTrue(set(titles).issubset(chapter_titles))
        self.assertFalse(
            {
                "Ljubljana",
                "French CS Newsletter",
                "100 things to do in Utrecht",
                "Toronto Cheap Eats",
            }
            & set(titles)
        )

    def test_geography_meets_size_language_and_source_rules(self):
        explicit_titles = set(WIKIS["trustroots"]["country_titles"])
        resolved = {}
        for path in (SRC / "03-countries").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            title = text.splitlines()[0].removeprefix("# ").strip()
            if title in explicit_titles:
                resolved[title] = (path, text)

        self.assertEqual(set(resolved), explicit_titles)
        for title, (path, text) in resolved.items():
            with self.subTest(title=title):
                self.assertIn("https://wiki.trustroots.org/en/", text)
                self.assertFalse(is_redirect_chapter(BOOK, path))
                self.assertFalse(is_omitted_chapter(BOOK, path))
                if title not in GRANDFATHERED_SHORT_GEOGRAPHY:
                    self.assertGreaterEqual(len(text.encode("utf-8")), 1_000)

    def test_country_overviews_precede_alphabetized_local_pages(self):
        paths = ordered_paths()
        france = paths[paths.index("03-countries/france.md") : paths.index("03-countries/germany.md")]
        germany = paths[paths.index("03-countries/germany.md") : paths.index("03-countries/budapest.md")]

        self.assertEqual(france[0], "03-countries/france.md")
        self.assertEqual(france[1:], sorted(france[1:]))
        self.assertEqual(germany[0], "03-countries/germany.md")
        self.assertEqual(germany[1:], sorted(germany[1:]))

    def test_geography_subsections_are_collapsible_country_groups(self):
        subsections = editorial_subsections(SRC)
        self.assertEqual(
            subsections["03-countries/france.md"][1],
            "Europe — France",
        )
        self.assertEqual(
            subsections["03-countries/australia.md"][1],
            "Oceania — Australia",
        )
        self.assertEqual(
            subsections["03-countries/rural-hospitality.md"][1],
            "Rural hospitality",
        )


if __name__ == "__main__":
    unittest.main()

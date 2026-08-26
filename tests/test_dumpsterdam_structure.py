import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_book import chapter_files
from toc import chapter_title, editorial_parts, editorial_subsections, render_toc


BOOK = ROOT / "books" / "dumpsterdam"
SRC = BOOK / "src"


def ordered_paths() -> list[str]:
    return [
        line.strip()
        for line in (BOOK / "editorial" / "order.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "["))
    ]


class DumpsterdamStructureTests(unittest.TestCase):
    def test_order_lists_every_included_content_chapter_once(self):
        actual = [path.relative_to(SRC).as_posix() for path in chapter_files(BOOK, "nl")]
        content = [path for path in actual if path != "00-frontmatter.md"]

        self.assertEqual(content, ordered_paths())
        self.assertEqual(len(content), len(set(content)))

    def test_named_parts_and_nested_archive_subsections_coexist(self):
        parts = editorial_parts(SRC)
        subsections = editorial_subsections(SRC)
        part_names = list(dict.fromkeys(parts[path][1] for path in ordered_paths()))

        self.assertEqual(
            part_names,
            [
                "Deel I — Waarom Dumpsterdam",
                "Deel II — Zelf dumpsterdiven",
                "Deel III — Van vondst naar maaltijd",
                "Deel IV — Delen en organiseren",
                "Deel V — Van actie naar verandering",
                "Archief",
                "Engelse selectie",
            ],
        )
        archive_groups = list(
            dict.fromkeys(
                subsections[path][1]
                for path in ordered_paths()
                if path in subsections
            )
        )
        self.assertEqual(
            archive_groups,
            [
                "Verhalen en portretten",
                "Media",
                "Evenementen en projecten",
                "Nieuws en internationale voorbeelden",
            ],
        )
        self.assertFalse(any(path.startswith("en/") for path in subsections))

    def test_duplicate_imports_are_omitted(self):
        included = set(ordered_paths())
        upstream = json.loads(
            (BOOK / "editorial" / "upstream.json").read_text(encoding="utf-8")
        )
        included_hashes = [upstream[path] for path in included if path in upstream]

        self.assertEqual(len(included_hashes), len(set(included_hashes)))
        self.assertIn("nl/dumpsterdam-missie-41.md", included)
        self.assertNotIn("nl/dumpsterdam-missie.md", included)
        self.assertIn("en/the-gleaners-kitchen.md", included)
        self.assertNotIn("en/gleaners-kitchen.md", included)

        for language in ("nl/", "en/"):
            titles = [
                chapter_title(SRC / path)
                for path in ordered_paths()
                if path.startswith(language)
            ]
            self.assertEqual(len(titles), len(set(titles)))

    def test_custom_part_jump_preserves_editorial_capitalization(self):
        toc = render_toc(
            [
                {
                    "part": "deel-ii-zelf-dumpsterdiven",
                    "part_name": "Deel II — Zelf dumpsterdiven",
                    "title": "Dumpster Diving in Nederland",
                    "href": "chapter",
                    "intro": False,
                    "region": False,
                    "subsection": "",
                },
                {
                    "part": "engelse-selectie",
                    "part_name": "Engelse selectie",
                    "title": "Dumpsterdam Mission",
                    "href": "english",
                    "intro": False,
                    "region": False,
                    "subsection": "",
                },
            ],
            {
                "table_of_contents": "Inhoudsopgave",
                "contents": "Inhoud",
                "filter_chapters": "Filter",
                "find_chapter": "Zoek",
                "no_matching_chapters": "Geen hoofdstukken",
            },
        )

        self.assertIn(">Deel II — Zelf dumpsterdiven</a>", toc)
        self.assertIn(">Engelse selectie</a>", toc)


if __name__ == "__main__":
    unittest.main()

"""Small translations for the generated book interface."""

from __future__ import annotations


EN = {
    "book_links": "Book links",
    "contents": "Contents",
    "table_of_contents": "Table of contents",
    "filter_chapters": "Filter chapters",
    "find_chapter": "Find a chapter…",
    "no_matching_chapters": "No matching chapters.",
    "edit_on_wiki": "Edit on wiki",
    "edit_on_wiki_aria": "Edit {title} on the wiki",
    "cover": "Cover",
    "read_book": "Read the book",
    "source_on_github": "Source on GitHub",
}

TRANSLATIONS = {
    "nl": {
        "book_links": "Boeklinks",
        "contents": "Inhoud",
        "table_of_contents": "Inhoudsopgave",
        "filter_chapters": "Hoofdstukken filteren",
        "find_chapter": "Zoek een hoofdstuk…",
        "no_matching_chapters": "Geen overeenkomende hoofdstukken.",
        "edit_on_wiki": "Bewerken op de wiki",
        "edit_on_wiki_aria": "Bewerk {title} op de wiki",
        "cover": "Omslag",
        "read_book": "Lees het boek",
        "source_on_github": "Broncode op GitHub",
    },
    "es": {
        "book_links": "Enlaces del libro",
        "contents": "Índice",
        "table_of_contents": "Índice",
        "filter_chapters": "Filtrar capítulos",
        "find_chapter": "Buscar un capítulo…",
        "no_matching_chapters": "No hay capítulos coincidentes.",
        "edit_on_wiki": "Editar en la wiki",
        "edit_on_wiki_aria": "Editar {title} en la wiki",
        "cover": "Portada",
        "read_book": "Leer el libro",
        "source_on_github": "Código fuente en GitHub",
    },
}


def ui_strings(lang: str | None) -> dict[str, str]:
    """Return interface strings, falling back to English per string."""
    strings = EN.copy()
    strings.update(TRANSLATIONS.get((lang or "en").split("-", 1)[0].lower(), {}))
    return strings

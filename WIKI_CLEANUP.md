# Wiki cleanup ledger

This file tracks source-wiki problems discovered while compiling the books. Book-side filters may keep these defects out of published editions, but the underlying wiki pages still need a separate, authenticated editorial pass. Before editing, compare each live page with its current revision history; imported snapshots can be older than the wiki.

## Open reference cleanup

- [Trashwiki: Laws](https://trashwiki.org/en/Laws) — imported chapter `books/dumpster-diving/src/01-practice/laws.md` contains a literal `<references />` marker and empty definitions 5, 7, and 8.
- [Trashwiki: Recycling](https://trashwiki.org/en/Recycling) — imported chapter `books/dumpster-diving/src/01-practice/recycling.md` contains many cited footnotes with empty definitions, plus unused definitions 9, 10, and 12. Restore reliable citations where possible; otherwise remove the corresponding citation markers and claims that cannot be sourced.
- [Trashwiki: Residential Food Diving](https://trashwiki.org/en/Residential_Food_Diving) — imported chapter `books/dumpster-diving/src/01-practice/residential-food-diving.md` contains a literal `<references />` marker.
- [Trashwiki: Waste](https://trashwiki.org/en/Waste) — imported chapter `books/dumpster-diving/src/01-practice/waste.md` has empty definitions 6 and 7.
- [Trustroots Wiki: Hospitality Club](https://wiki.trustroots.org/en/Hospitality_Club) — imported chapter `books/hospitality-exchange/src/02-networks/hospitality-club.md` has empty definitions 10 and 11.

## Import-only cleanup

- Contributor values with an `unknown>` prefix are dump/import artifacts, not public wiki names. The renderer strips the prefix; do not rename wiki accounts from this evidence alone.
- `QuÃ©SÃ©Yo2` is repaired to `QuéSéYo2` during import/rendering. Verify the live revision history before proposing an upstream account or attribution change.

## Rights and licensing cleanup

- [Hitchwiki: *Hitch-Hiking by Mario Rinvolucri*](https://hitchwiki.org/en/Hitch-Hiking_by_Mario_Rinvolucri) and all of its subpages reproduce a pre-existing 1974 book. The introduction documents Mario Rinvolucri's permission for Bernd Wechner to republish it on the World Wide Web in 1997, but it does not document a Creative Commons grant for the underlying book. Create a dedicated template, such as `Template:Web publication permission`, stating: **“This pre-existing work is excluded from Hitchwiki's Creative Commons license. It is reproduced online with the author's permission; no permission for further reuse, adaptation, print publication, or relicensing has been documented.”** Apply it to the parent page, Introduction, chapters 1–11, and appendices 1–2. Ensure the template is visible on every page and categorizes them for rights review. The cartoons credited to David O'Docherty and Lola Rinvolucri require their own rights clarification. Do not replace this notice with a CC license unless the relevant rightsholder supplies a written grant.

## Editing checklist

- Confirm the defect still exists on the live page.
- Prefer restoring the intended reliable source over merely deleting an empty note.
- Preserve page licensing and attribution requirements.
- Record the edited revision URL here and mark the item complete.

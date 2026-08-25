# BookBot guidelines

BookBot helps maintain wiki pages that connect each wiki to its published books. It must behave like a careful wiki editor, not like a deployment process.

## Scope and authorship

- Edit only the wiki and page explicitly requested. Creating an account does not authorize publishing pages on the other wikis.
- Use the `BookBot` account, mark automated edits as bot edits, and write a specific edit summary.
- Keep Book pages useful to editors: link the current edition, explain how wiki changes reach a later edition, and list concrete work for the next edition.
- Prefer the wiki for durable source material and the repository for book structure, production, and reader bugs.

## Preserve human edits

- Fetch the latest live page and revision ID immediately before preparing an edit. Never publish a cached local draft as the source of truth.
- Make the smallest possible change to that live text. Preserve unfamiliar prose, formatting, templates, links, and categories.
- Submit with MediaWiki's edit-conflict protection (`baserevid` and `starttimestamp`, or an equivalent conditional update). If the revision changed, stop, fetch again, and reapply the intended change to the new text.
- Never resolve an edit conflict by deleting, replacing, or recreating the page.
- Review the proposed diff before publishing and fetch the saved revision afterward to verify it.

## Credentials and local files

- Keep passwords, cookies, tokens, server details, fetched page text, and working drafts under ignored local paths. Never commit or print credentials.
- Restrict credential files to the local user (for example, mode `0600`).
- Do not place secrets in command arguments, edit summaries, logs, issues, or CI configuration.

## Content hygiene

- State dates, versions, download links, and project status only after checking the repository or published edition.
- Suggest actions that materially improve a future book edition. Avoid red links presented as established workflows and tasks that only collect transient data.
- Link invitations to a real contact route, such as the repository issue tracker.
- Recheck links and page rendering after every published edit.

# Content Hub

A single-page workspace for capturing content ideas, writing scripts, and tracking progress.

## Features

- Create cards with a handle/project, headline, status, and a single expandable notes/script area.
- Edit the notes in place, cycle status between `Draft → In Progress → Completed`, or delete cards; completed work automatically sinks to the bottom.
- Filter the list by status to focus on what's next.
- Notes support line breaks, blank lines, simple bullet lists (lines starting with `-`), and bold text via `**bold**`. Each card collapses/expands with a `Show more` toggle so the grid stays tidy by default.
- Cards sit in a tidy two-column grid on larger screens so you can scan multiple projects at once without overwhelming the page.
- Data lives in your browser via `localStorage`, so there is no external dependency or setup.

## Usage

1. Open `index.html` in any modern browser.
2. Fill in the form to add a new card. Handle, headline, and notes are required to keep every card intentional.
3. Format notes using bullets, blank lines, and `**bold**`. Collapse or expand long sections with **Show more**, use **Edit** to switch the same content box into an editor, **Next Status** to advance the workflow, and the dropdown on the Cards panel to filter.

On first load, an example card for `@lana_yaps` is seeded to demonstrate the workflow—delete or replace it once you add real work.

## Storage Strategy

- Cards are stored as JSON under the key `content-hub.cards` in `localStorage`.
- Each card includes `id`, `handle`, `title`, `status`, `notes`, and `updatedAt`.
- Because data is local to the browser, exporting/backing up is as simple as copying the JSON via the browser devtools or saving the rendered notes.

If you need to sync across devices later, you can swap `localStorage` for a lightweight backend (e.g., a hosted SQLite or Supabase table) without changing the front-end structure.

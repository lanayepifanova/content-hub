# Content Hub

A single-page workspace for capturing content ideas, writing scripts, and tracking progress.

## Features

- Create cards with a handle/project, headline, status, and as many idea boxes as you need—each box can be renamed per hook/topic and reordered within the card.
- Cards stay compact in the grid; hit **Open** (or click the card) to pop a focused workspace for deep editing.
- Edit handle, headline, status, and every idea box in place; add/remove boxes, cycle status between `Draft → In Progress → Completed`, or delete cards. Completed work automatically sinks to the bottom.
- Drag cards to reorder priorities; drop onto the list background to send a card to the end.
- Filter the list by status to focus on what's next.
- Idea boxes support line breaks, blank lines, simple bullet lists (lines starting with `-`), and bold text via `**bold**`. Each subcard collapses/expands with its own `Show more` toggle so the grid stays tidy by default.
- Skip anything you don’t need yet—empty handles, idea titles, or copy show `n/a` placeholders until you fill them in.
- Cards sit in a tidy two-column grid on larger screens so you can scan multiple projects at once without overwhelming the page.
- Data lives in your browser via `localStorage`, so there is no external dependency or setup.

## Usage

1. Open `index.html` in any modern browser.
2. Fill in the form to add a new card. Only the headline/title is required—blank fields display `n/a` until you fill them in.
3. Format idea boxes using bullets, blank lines, and `**bold**`. Collapse or expand long sections with **Show more**, use **Edit** to switch the card into edit mode (handle, headline, status, idea titles, and content), add/remove boxes with **Add Idea**, **Next Status** to advance the workflow, drag cards to reorder, and filter via the dropdown.

On first load, an example card for `@lana_yaps` is seeded to demonstrate the workflow—delete or replace it once you add real work.

## Storage Strategy

- Cards are stored as JSON under the key `content-hub.cards` in `localStorage`.
- Each card includes `id`, `handle`, `title`, `status`, `sections`, and `updatedAt`.
- Because data is local to the browser, exporting/backing up is as simple as copying the JSON via the browser devtools or saving the rendered notes.

If you need to sync across devices later, you can swap `localStorage` for a lightweight backend (e.g., a hosted SQLite or Supabase table) without changing the front-end structure.

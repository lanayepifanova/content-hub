# Content Hub (React + Vite)

A minimalist two-board workspace (one stack for @lana_yaps, one for UGC briefs) built with React + Vite and backed by Firebase Firestore.

## Features

- Add ideas with a single textarea per board; cards render in a compact fixed-height grid for fast scanning.
- Drag cards to reorder priorities or move them between the @lana_yaps and UGC stacks.
- Click **Open** on any card to launch a pop-up rich-text editor (headings, bold/italic/underline, bullet/numbered lists, highlights, etc.).
- All data persists in Firestore, so cards stay in sync across browsers/devices.

## Getting Started

1. **Install dependencies**
   ```bash
   npm install
   ```
2. **Configure Firebase**
   - Create a Firestore project (or reuse an existing one).
   - Enable Firestore in _Native mode_.
   - Create a web app in the Firebase console and copy the config values.
   - Duplicate `.env.example` to `.env` and fill in the `VITE_FIREBASE_*` keys.
3. **Run the dev server**
   ```bash
   npm run dev
   ```
   _Or_ use the helper script (auto-installs deps first):
   ```bash
   python3 scripts/manage.py dev
   ```
   Visit the printed URL (usually `http://localhost:5173`).

## Firestore Shape

Cards live under `boards/{boardId}/cards` where `boardId` is either `lana` or `ugc`. Each card document stores:

```json5
{
  "board": "lana",           // or "ugc"
  "content": "<p>Rich text</p>",
  "order": 0,                  // used for drag-and-drop ordering
  "createdAt": Timestamp,
  "updatedAt": Timestamp
}
```

Drag-and-drop updates the `order` field for the affected board(s) so the UI renders in the saved order on every device.

## Available Scripts

| Script        | Description                                   |
|---------------|-----------------------------------------------|
| `npm run dev` / `python3 scripts/manage.py dev` | Start Vite in dev mode with hot reloading. |
| `npm run build` | Production build output to `dist/`.         |
| `npm run preview` / `python3 scripts/manage.py preview` | Serve the production build locally. |

## Next Ideas

- Add auth/roles if you need to separate internal notes from client deliverables.
- Drop in more board types (e.g., “Pitches”, “Products”) by extending `src/constants.js`.
- Sync additional metadata (due dates, rates) by expanding the card schema and UI controls.

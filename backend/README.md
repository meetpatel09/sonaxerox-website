# Backend — Google Apps Script

Free backend for the print page (`/print/`). It stores each order's PDF in Google Drive (folder **SonaXerox-Orders**) and
one row per order in a Google Sheet (**Sona Xerox Orders**), and gives the shop-PC listener a secured API.

| File | Purpose |
|---|---|
| `orders-backend.gs` | the web app: `doPost` (customer order) + `doGet` (listener API: `pending`, `file`, `done`, `error`) |
| `drive-cleanup.gs` | `cleanupOldDriveFiles()` — trashes a PDF 24 h after the order **only if** it is `PRINTED`/`ERROR` (a `NEW` order is never deleted) |

## Set up / update
1. <https://script.google.com> → project **Sona Xerox Print** → paste `orders-backend.gs`, then `drive-cleanup.gs` **below** it.
2. **Change `SECRET`** at the top of `orders-backend.gs` to your own long random text. Use the same value in the shop PC
   `listener.config.json`. *Do not commit the real value* — this repository is public.
3. **Deploy → Manage deployments → ✏️ → Version: New version → Deploy.** The `/exec` URL stays the same, so the website needs no change.
   (First time only: *Deploy → New deployment → Web app → Execute as: Me → Who has access: Anyone*.)
4. Triggers (⏰): `cleanupOldDriveFiles`, deployment **Head**, time-driven, every hour.

## Sheet columns
`Time · Token · Phone · Colour · Sides · Copies · Pages · File URL · File ID · Status`
Status: `NEW` → `PRINTED` | `ERROR` → (`… (file deleted)` after cleanup). Tokens are `S101`, `S102`, … (row number + 100).

## Limits (enforced here, not only in the page)
30 pages · 30 copies · phone must be 10 digits. The page also limits the PDF to 15 MB.

## Security notes
- `doPost` (customer orders) is open by design; `doGet` actions other than the health check need `SECRET`.
- Because anyone can send an order, consider a hold/approval or payment step before auto-printing (see `docs/BACKLOG.md`).
- If `SECRET` was ever the template value `CHANGE-ME-sona-valod-2026`, change it now — that text is public.

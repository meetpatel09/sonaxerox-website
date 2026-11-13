# Backlog

Ordered by how much it matters. Tick items off in the pull request that does them.

## Should do soon
- [ ] **Abuse protection for `/print/`** — anyone can POST an order and it prints automatically. Options: hold new orders until staff tap *Approve* on a staff page; rate-limit per phone number in the Apps Script; or require payment first (below).
- [ ] **Confirm the live Apps Script `SECRET` is not the template** `CHANGE-ME-sona-valod-2026` (it is public in this repository).
- [ ] **Re-submit `sitemap.xml`** in Google Search Console (the earlier submission pointed to a file that did not exist).
- [ ] **HEIC on `/print/`** — the scan page converts iPhone HEIC photos; the print page does not yet (it shows "can't open this photo").
- [ ] **Payment** — decision pending (see `docs/DECISIONS.md` D5). If Cashfree: do KYC before the 0%-fee offer ends on **31 Mar 2027**; needs Terms / Privacy / Refund / Contact pages and a small confirmation endpoint; unpaid orders must not print.

## Features asked for
- [ ] Staff "**Today's orders**" page with a *Ready* button (needs Google sign-in, not just a PIN).
- [ ] **Printer status** indicator (listener writes a heartbeat row; the staff page shows "online / last seen").
- [ ] **Installable app (PWA) with Share Target** so customers can share a PDF straight from WhatsApp to `/print/`.
- [ ] **Photo gallery** section on the main site (needs photos of the shop).
- [ ] More services on the main site: Template design, Online application, Social-media post.
- [ ] **Photo / signature resizer** for online forms; **passport-photo maker**.
- [ ] `/scan/`: a **Horizontal** tilt line (left/right squeeze) to go with Vertical.
- [ ] `/print/`: **crop and straighten** in the photo editor (reuse the scan page's corner engine).

## Housekeeping
- [ ] Main site SEO: `LocalBusiness` structured data (JSON-LD), Open Graph tags, canonical link.
- [ ] CI: add an HTML validator and a link checker; run the tests on a weekly schedule to catch CDN/library changes.
- [ ] The photo-cleaning engine exists in `/print/` and (partly) elsewhere; if it grows, extract a shared `assets/engine.js` and keep pages self-contained by inlining at build time.
- [ ] Listener: run as a Windows service and add a self-update check.
- [ ] Move the shop PC listener folder out of `C:` if it is still there (a Windows reset would delete it).

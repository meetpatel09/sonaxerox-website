# Changelog

Newest first. Dates come from git where the file is in the repository, otherwise from when the work was done.

## 2026-11-14 — `/print/` copies limit
* One order is now limited to **30 pages in total including copies** (pages × copies ≤ 30; double-sided counts 2 pages as 1). The "+" button stops at the allowed number, copies are lowered automatically if pages/sides change, and a hint shows the maximum. Enforced on the page only (not in the Apps Script).

## 2026-11-14 — Shop PC: listener auto-restart + no double printing
* **New:** `install-autostart.bat` (Windows checks every minute and starts the listener if it is not running), `run-listener-forever.bat`, `remove-autostart.bat`.
* **Fixed (found while using it):** one order could print again and again. The listener now allows **only one copy** on the PC (local port lock), and remembers printed orders in `listener.printed.txt`, so a failed "mark PRINTED" call can no longer cause a re-print. Tests reproduce both cases.

## 2026-11-14 — `/print/` redesign
* **New layout:** hero strip (prices, pay at pickup), 3-step progress (Upload → Choose → Send), two columns on computers (upload + preview left, price/Send + options right), sticky price/Send bar on phones.
* **New:** *Edit pages* for PDFs — rotate, remove and reorder pages in the browser; only the edited PDF is sent.
* **New:** drag & drop a file onto the upload box; the Send button says why it is disabled; token appears in the header only after ordering.
* **New:** order-received screen with "what to do next", shop address/hours, WhatsApp and call buttons.
* Colour and sides choices have icons; photo editor, preview/zoom, prices, limits and the order sent to the backend are unchanged.
* **Tests:** new `test_print_pageedit` suite (28+ checks); one header check in `test_print_pdf` updated for the new token behaviour.

## 2026-11-13 — Project setup
* Repository organised: `backend/`, `shop-pc/`, `tools/`, `tests/`, `docs/`, project skills, CI, pull-request template.
* **New:** `sitemap.xml` and `robots.txt` (were missing); `_config.yml` keeps developer folders off the public site.
* **Fixed:** `/scan/`, `/aadhaar-card/`, `/voter-card/` were not `noindex`; Aadhaar and voter pages had no favicon.
* **Tests:** 11 suites, ~250 checks in a real browser (print, scan, Aadhaar, listener, structure rules).
* **Shop PC:** the listener can now read `listener.config.json`, so replacing `listener.py` never wipes the URL / secret / printer names.

## 2026-10-19 → 11-08 — `/scan/`
* **Turn left / right** buttons and a **Straighten** line (±45°) on the corner screen; the dots travel with the photo and the scan follows what you see.
* **Vertical** slider (±30°, upright, beside the photo) for pages shot from above or below.
* **iPhone HEIC** photos are converted automatically; clear messages for unreadable files; works inside locked-down preview windows that block `blob:` images; big photos are scaled safely; transparent PNGs get a white background.
* The scan is now cut directly from the original photo (sharper after turning); window resize no longer drifts the dots.

## 2026-10-18 — `/print/`
* **Photos** (JPG/PNG/WebP) are accepted: *Make it print-friendly* editor (Clean document, B&W document, Auto photo, As is; brightness, contrast, sharpen, rotate, Fit/Fill; several photos; edit again) → A4 PDF; EXIF rotation respected; PDF auto-shrunk to stay under 15 MB.
* **Live price** box and the amount on the order-received screen.
* **Gujarati / English** toggle (Gujarati default, remembered in `sx_lang`).
* **Preview** with zoom (+ / − / Fit, pinch, drag, double-tap, Ctrl+wheel), page arrows, and ✓ marks for the pages that will print.
* **₹ glyph bundled** (older PCs showed an empty box).
* Fixed: the order-received screen could sit off-screen on long pages; the zoom bar could cover the Send button on small phones.

## 2026-10-11
* **`/pdf-tools/`** (merge, split, rotate, reorder, shrink; password-protected PDFs), **`/our-tools/`** private dashboard (Gujarati/English).
* **`/aadhaar-card/`**: *Scale text* (drag a corner, Shift for free stretch, Enter/Esc) and *Burn* (darken faded text/colour, white paper untouched), Ctrl+Z.

## 2026-09-01 → 10-10 — `/scan/`
First version of the scan tool: four draggable corners (perspective correction), Windows-Photos-style adjustment sliders (Light / Colour), multi-page, PDF/JPEG/ZIP export, ID-card sheet layout, zoomable preview, Safari-safe printing.

## 2026-08-17 — `/aadhaar-card/` and `/voter-card/`
Print-ready sheets from the official e-Aadhaar / voter-ID PDFs (password-protected PDFs supported).

## 2026-07-30
Favicon from the real shop banner; Google Search Console verification file.

## 2026-07-25 — online printing
`/print/` first version; Apps Script backend (v1, then v2 with listener endpoints); shop-PC listener (SumatraPDF, two printers, 24 h cleanup, hidden start, auto-start with Windows).

## 2026-07-14 / 15 — website and domain
Bilingual CMYK website with the animated photocopier; custom domain **sonaxerox.in** (CNAME, DNS, HTTPS); QR code.

## 2026-06-12
First website draft and the photocopier drawing (`assets-src/xerox-machine-design.html`).

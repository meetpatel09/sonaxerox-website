# Architecture

## 1. The website
Static files, served by GitHub Pages straight from the repository root. No bundler, no framework, no `package.json` at the root.
Each page is **one self-contained HTML file** (CSS + JS inside) so it can be edited, tested and rolled back on its own.
Pages that need a library load it from **cdnjs with an exact version** (pdf-lib 1.17.1, pdf.js 3.11.174, JSZip 3.10.1, heic2any 0.0.4);
the Aadhaar and voter-card pages ship their own copy of pdf.js next to the page.

Two visual styles exist on purpose:
| | main site, `/aadhaar-card/`, `/voter-card/`, `/our-tools/` | `/print/`, `/scan/`, `/pdf-tools/` |
|---|---|---|
| background / ink | cream `#FBFAF6` / `#161616` | white `#FFFFFF` / `#161513` |
| cyan · magenta · yellow | `#00A3C4` · `#E0218A` · `#FFC400` | `#00AEEF` · `#EC008C` · `#F5C400` |
| fonts | Bricolage Grotesque, Archivo, Hind Vadodara, IBM Plex Mono | Archivo Black, Work Sans, Hind Vadodara, IBM Plex Mono |
| mood | brand / marketing | tools — clean, mobile-first (the print page is a 420 px column) |

## 2. Online printing (`/print/` → Apps Script → shop PC)
1. **Page** (`print/index.html`): the customer picks a PDF *or photos*. Photos go through a client-side editor (see §4) and become an A4 PDF.
   The page checks ≤ 30 pages, ≤ 15 MB and pages × copies ≤ 30 in total (double-sided: 2 pages = 1; page only, not in the backend), lets the customer print only some pages (a new PDF containing just those pages is built in the browser),
   shows the price live (`RATE_BW = ₹2`, `RATE_COLOR = ₹10` per page × copies — double-sided costs the same per page) and `POST`s JSON to the Apps Script URL:
   `{fileName, fileData(base64), pages, color: bw|color, side: single|double, copies, phone}`.
2. **Backend** (`backend/orders-backend.gs`): validates (10-digit phone, ≤ 30 pages, ≤ 30 copies), stores the PDF in Drive folder *SonaXerox-Orders*,
   appends a row to the Sheet *Sona Xerox Orders* (`Time, Token, Phone, Colour, Sides, Copies, Pages, File URL, File ID, Status`) and answers `{ok:true, token:"S101"}`.
   Token = `S` + (100 + row number). The page shows the token with a rubber-stamp animation and the amount to pay.
3. **Listener** (`shop-pc/listener.py`): every 15 s `GET ?action=pending&key=SECRET` → for each `NEW` order `?action=file` (PDF as base64) →
   `SumatraPDF -print-to <printer> -print-settings "<simplex|duplexlong>,<color|monochrome>,<N>x,fit" -silent file.pdf` → `?action=done` (or `?action=error`).
   B&W and colour use different printers (`PRINTER_BW` / `PRINTER_COLOR`).
4. **Status**: `NEW → PRINTED | ERROR`; after 24 h the Drive PDF is trashed (`drive-cleanup.gs`, hourly trigger) and the status gets `(file deleted)`. A `NEW` order is **never** deleted.
   The PC also deletes its local copies after 24 h.
5. **Payment**: none online yet — the customer pays **at pickup** (cash/UPI at the counter). See `docs/DECISIONS.md` (D5) for the options that were studied.

**When prices change** edit `print/index.html` in three places: the constants `RATE_BW` / `RATE_COLOR`, the dictionary entries `per2`, `per10` and `priceIdle` (Gujarati **and** English), then run `tests/test_print_pdf.py` (it fails if any text still shows the old rate).

## 3. Scan tool (`/scan/`)
Upload → **corner screen** → **adjust screen** → pages → export. Key invariants (the tests protect them):
* The photo's original pixels are never altered; turning / straightening / vertical correction are views on top of them.
* The four dots are stored in **original-photo coordinates** (`corners0`), so *turning* and *straightening* carry them with the photo.
* The **Vertical** slider (perspective, ±30°) is different on purpose: an untouched starting frame **refits** inside the corrected photo, and a frame the user dragged **stays where it is on screen** while the photo is squeezed under it.
* The scan is cut straight from the **original** photo with a single homography (the 4 dots → a rectangle); quarter turns only change which dot is "first" so the page follows what you see.
* Photos open through three routes (normal image → `createImageBitmap` → data URL) so the page also works in sandboxed previews that block `blob:` images; iPhone **HEIC** is converted by heic2any (loaded on demand).

## 4. Photo clean-up (`/print/`)
Engine in the page (all client-side): **Clean document** = divide out the lighting estimate (per-channel, removes shadows and yellow cast; a dark block is never brightened more than ~1.8×), snap paper to white, darken ink;
**B&W document** = same, greyscale; **Auto photo** = tone stretch + brightness toward a pleasant average + a little colour; **As is**.
Style is picked automatically (`looksLikeDoc`). Output: A4 page (landscape for wide photos), Fit (10 mm border) or Fill, JPEG-embedded in the PDF at ≤ 300 dpi; if the PDF would exceed 15 MB it is rebuilt at lower quality / resolution (4 steps).

## 5. Security notes
* The repo and the website are public. The Apps Script URL is public by design; **only** the listener endpoints are protected by `SECRET`.
* `doPost` (placing an order) is open: anyone can submit an order, and orders print automatically. See `docs/BACKLOG.md` (abuse protection).
* Customers' phone numbers are stored in the Sheet; PDFs are deleted after 24 h. ID documents (Aadhaar/voter) are processed only in the browser.
* Third-party code loaded at run time: cdnjs libraries (pinned). `heic2any` is loaded only when an HEIC file is chosen.

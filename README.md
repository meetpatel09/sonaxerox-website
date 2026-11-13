# Sona Xerox — website & shop tools

Website and software tools for **Sona Xerox**, Valod, Gujarat (near S.G. Highschool) — live at **<https://sonaxerox.in>**.
Owners: Kamleshbhai Patel & Meet Patel · WhatsApp +91 77788 05780 · open every day 7:30 AM – 7:00 PM.

Everything on the website is **plain HTML + JavaScript — no build step, no framework, no server of our own.** GitHub Pages
hosts it for free; a Google Apps Script is the only "backend".

## What is live

| Address | What it is | Who uses it | Google |
|---|---|---|---|
| `/` | bilingual (Gujarati / English) shop website with an animated photocopier | everyone | indexed |
| `/print/` | **online print order**: upload a PDF *or photos* (cleaned for printing), page range, colour, sides, copies → live price → token | customers | indexed (in the sitemap) |
| `/scan/` | **photo → straight PDF**: turn, straighten, correct the angle, mark the 4 corners, adjust, export PDF/JPEG | shop | `noindex` |
| `/pdf-tools/` | merge / split / rotate / reorder / shrink PDFs | shop | `noindex` |
| `/aadhaar-card/` | e-Aadhaar PDF → print-ready card sheet (with *Scale text* and *Burn* tools) | shop | `noindex` |
| `/voter-card/` | voter-ID PDF → print-ready card | shop | `noindex` |
| `/our-tools/` | private dashboard with a button for every page (Gujarati / English) | shop | `noindex, nofollow`, not linked from anywhere |

All photo / PDF / ID processing happens **in the browser** — files are only sent to our server when a customer presses *Send to shop printer*.

## How printing works

```
customer's phone ──► /print/ ──► Google Apps Script ──► Google Drive (PDF) + Google Sheet (order row, status NEW)
                       (browser)        (backend/)                              ▲
                                                                                │ every 15 s: pending → file → done / error
shop PC (Windows) ◄───────────── listener.py (shop-pc/) ────────────────────────┘
   └─► SumatraPDF ─► black & white printer / colour printer          customer pays at pickup and shows the token (S101, S102…)
```

Details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Repository map

```
index.html  print/  scan/  pdf-tools/  aadhaar-card/  voter-card/  our-tools/     ← the website (served as-is)
favicon.png  CNAME  sitemap.xml  robots.txt  google96403b….html                  ← site files (never delete CNAME or the google file)
backend/        Google Apps Script source (copy-paste into script.google.com)       ┐
shop-pc/        listener + launchers for the Windows shop PC                        │ NOT published —
tools/          new_page.py (scaffold a page), verify_live.py (live vs repo)        │ _config.yml keeps these
tests/          browser + unit tests (Playwright)                                   │ off sonaxerox.in
docs/           architecture, deployment, testing, decisions, changelog, backlog    │
assets-src/     source artwork (QR code, photocopier drawing)                       ┘
.claude/skills/ project skills for Claude (conventions, testing, deploy, print pipeline, image tools)
CLAUDE.md       short guide for AI assistants working in this repo
```

## Working on the site

```bash
python3 -m http.server 8000                  # preview at http://localhost:8000  (the pages work from any static server)

# one-time test setup
pip install -r tests/requirements.txt && python3 -m playwright install chromium
(cd tests && npm install)

python3 tests/run_all.py                     # all suites (~4 min)      --fast = no browser (10 s)   --slow = + heavy photos
python3 tools/new_page.py my-tool "My tool" "મારું ટૂલ"          # new page: file + dashboard button + noindex, all automatic
```

**The rules** (each one is enforced by a test, so a pull request cannot forget them):
1. **Every page gets a button on `/our-tools/`** — `tools/new_page.py` does it for you.
2. Private tools are `noindex`; only pages listed in `sitemap.xml` may be indexed.
3. Every visible text exists in **Gujarati and English** (`sx_lang` remembers the choice).
4. Any page that shows **₹** must bundle the rupee glyph (`tools/templates/rupee-face.css`) — older Windows PCs draw an empty box otherwise.
5. **This repository is public: never commit a secret.** The Apps Script `SECRET` and the shop PC's `listener.config.json` stay out.
6. Load libraries from cdnjs with an **exact pinned version**; nothing from random hosts.
7. Change through a **pull request**, let the tests pass, merge, then run `python3 tools/verify_live.py`.

How to deploy, roll back and verify: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) · what the tests cover: [`docs/TESTING.md`](docs/TESTING.md) ·
why things are the way they are: [`docs/DECISIONS.md`](docs/DECISIONS.md) · what's next: [`docs/BACKLOG.md`](docs/BACKLOG.md).

## Hosting facts

GitHub Pages from branch `main`, folder `/` · custom domain **sonaxerox.in** (GoDaddy, 3 years) · DNS: four `A` records
`185.199.108.153 / .109.153 / .110.153 / .111.153` for `@`, `CNAME www → meetpatel09.github.io` · HTTPS enforced ·
Google Search Console verified by `google96403b7903aa5e97.html`.

© Sona Xerox. All rights reserved — the code is public to read, not licensed for reuse.

---
name: sonaxerox-site-conventions
description: House rules for building or changing ANY page of the Sona Xerox shop website (sonaxerox.in, GitHub repo meetpatel09/sonaxerox-website) — design tokens, Gujarati/English toggle, the mandatory /our-tools/ dashboard button, noindex for private tools, the ₹ glyph, pinned libraries, mobile-first layout. Use this whenever the user mentions Sona Xerox, sonaxerox.in, the shop site, a new tool/page for the shop, /print, /scan, /pdf-tools, /aadhaar-card, /voter-card, /our-tools, Gujarati text, CMYK styling, or asks to add or change anything in this repo — even if they never say "conventions".
---

# Sona Xerox site conventions

Sona Xerox is a printing/xerox shop in Valod, Gujarat (owners Kamleshbhai Patel and Meet Patel; WhatsApp +91 77788 05780; open daily 7:30 AM–7:00 PM). The website is plain HTML hosted free on GitHub Pages; each page is **one self-contained HTML file** (CSS + JS inside). No build step, no framework. The owner (Meet) is a data engineer, writes short informal messages, and wants **complete, working files**, not sketches.

## The rules (each is enforced by a test in the repo — breaking one fails CI)
1. **Every new page gets a button on the private dashboard `/our-tools/`.** In the repo run `python3 tools/new_page.py slug "English title" "ગુજરાતી શીર્ષક" [--public] [--paper] [--rupee]` — it creates the page, adds the button, and sets noindex. Doing it by hand: copy an existing `<li><a class="tool" href="/slug/">…</a></li>` block in `our-tools/index.html` (icon, `data-gu`/`data-en` name, `sonaxerox.in/slug/` path line).
2. **Private tools are `<meta name="robots" content="noindex">`**; only pages listed in `sitemap.xml` (home, `/print/`) may be indexed. Never list private paths in `robots.txt` (that advertises them). The dashboard is `noindex, nofollow` and is not linked from any public page.
3. **Every visible text exists in Gujarati and English**, default Gujarati on customer pages, choice remembered in `localStorage['sx_lang']`. See `references/bilingual.md`.
4. **₹ must render everywhere.** Older Windows PCs have fonts without ₹ and draw an empty box. Any page that shows ₹ embeds `tools/templates/rupee-face.css` (a ~1 KB Poppins subset) and puts `'SX Rupee'` first in the font stack (`'SX Rupee Bold'` for heavy display digits).
5. **The repository is public. Never commit a secret** (Apps Script `SECRET`, `listener.config.json`, tokens). Placeholders only.
6. **Libraries come from cdnjs at an exact pinned version** that is at least two weeks old (current: pdf-lib 1.17.1, pdf.js 3.11.174, JSZip 3.10.1, heic2any 0.0.4). No unpinned or unknown hosts. Aadhaar/voter pages ship their own pdf.js copy beside the page.
7. **Files stay on the user's device.** Aadhaar/voter IDs, photos and PDFs are processed in the browser; only the print page uploads, and only when the customer presses *Send*.
8. **Test before you hand over** (`sonaxerox-testing` skill) and say plainly what you could not test (real phones, Safari).

## Building a page — checklist
- Start from `tools/templates/page.html` (tokens, header, language toggle already there).
- Mobile first: `<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">`, touch targets ≥ 44 px, `env(safe-area-inset-*)` for fixed bars, no horizontal scroll at 360 px. A fixed footer needs a `z-index` above floating bars and the page needs bottom padding for it.
- Use `max-height: min(…vh, …)` not bare `100vh` for photo areas; leave room for controls.
- Colours/fonts: two palettes exist — see `references/design-tokens.md`. Don't invent a third.
- Gujarati typography: font **Hind Vadodara**, `letter-spacing:0`, no `text-transform:uppercase` on Gujarati, slightly larger size than Latin.
- Buttons whose text is uppercase via CSS show capitals in `innerText` — tests must use `textContent`.
- Add the page to `sitemap.xml` only if customers should find it on Google.
- Update `docs/CHANGELOG.md` (and `docs/BACKLOG.md` if you finish an item).

## Working with the owner
- Short, informal English with typos is normal — answer clearly, in plain words, skip jargon; Gujarati copy should be simple spoken Gujarati.
- Reference answers as concise bullets; end with what to upload/do next. One short question at most when something is truly ambiguous.
- Show a screenshot or measured result for visual work; keep messages for his father (the co-owner) in respectful Gujarati ("તમે").
- Prices today: B&W ₹2/page, colour ₹10/page; pay at pickup. Payment gateways were studied and deferred (`sonaxerox-print-pipeline`).

## Where to look
`references/design-tokens.md` · `references/bilingual.md` (pattern + Gujarati glossary) · `docs/DECISIONS.md` in the repo for why things are as they are.

---
name: sonaxerox-testing
description: How to test and debug Sona Xerox pages in a real headless browser (Playwright) with a faked network, synthetic photos and PDFs, old-PC fonts and locked-down-window simulation. Use whenever you build, change, verify or debug anything on sonaxerox.in (/print, /scan, /aadhaar-card, /pdf-tools, the shop-PC listener), whenever the user says "test it", shows an error message or screenshot, reports "it doesn't open / looks wrong on my PC / shows a box / not working", or before you hand over any HTML file — even if they don't mention testing.
---

# Testing Sona Xerox pages

The repo has a full suite (`tests/`, ~250 checks, `python3 tests/run_all.py`). It opens the **real page files** in Chromium from disk, answers CDN libraries from `tests/node_modules`, blocks Google Fonts, fakes the Apps Script backend, and generates photos/PDFs whose correct answer is known. Read `docs/TESTING.md` for the full table; this skill is the way of working.

## Workflow
1. **Reproduce before you fix.** A bug report is a hypothesis; build the smallest fixture that triggers it and watch it fail. The owner's reports so far, and what reproduced them: "Could not open that image" → a **HEIC** file, then a page under a **CSP that blocks `blob:` images** (a sandboxed preview); "₹ shows a box on the shop PC" → browser restricted to **Arial-like fonts**; "Send button not clickable" → fixed footer under a floating zoom bar on a 320×520 screen. See `references/harness-patterns.md` for each recipe.
2. **Fix, then add a test that fails without the fix** (so it can't come back). Put it in the suite for that page.
3. **Run the narrow suite while editing** (`--only scan_vertical`), the **full suite before handing over** (`python3 tests/run_all.py`), `--slow` when touching photo size handling.
4. **Look at it.** Take screenshots (desktop + 390 px phone) and view them; numbers pass while layouts can still be ugly.
5. **Report honestly**: what passed (counts), what changed, what you could *not* test (real iPhone/Android, Safari, the shop PC) and what to try on the real device.

## Principles
- **Measure, don't just look for elements.** Check pixels (canvas data), geometry (bounding boxes), file contents (the PDF that was *sent*), ratios (checker cell width top÷bottom → 1.00 means straight). Examples of good assertions: paper brightness ≥ 245 after "Clean document"; the uploaded PDF contains only pages 2–3; the dots are still on the red/green/blue/yellow markers after turning.
- **Test what the user does:** real mouse drags/wheel/keyboard; touch via CDP on a phone context; viewport resizes; the language toggle mid-error.
- **Fake the network, not the page.** Never mock the DOM — it would have hidden every bug above.
- **Fixtures are generated, deterministic, and never committed** (`tests/make_fixtures.py`). Design them so the right answer is exact (markers under the default dots, a checkerboard squeezed by a known angle).
- When a check fails, decide whether the **page** or the **test** is wrong; say which. (Several "failures" here were over-strict tests: thresholds, `inner_text` capitals, a measuring row on grey.)

## Commands
```bash
python3 tests/run_all.py [--fast | --slow | --only NAME]
python3 tests/test_print_pdf.py            # any suite on its own
python3 tests/make_fixtures.py [--slow]    # regenerate photos/PDFs
```
New suite → copy the skeleton in `docs/TESTING.md`, register it in `run_all.py`.

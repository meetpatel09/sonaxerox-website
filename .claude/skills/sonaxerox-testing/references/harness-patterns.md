# Harness patterns (Playwright, Python sync API)

```python
from common import *            # REPO, Report, FakeBackend, browser, new_context, open_page, fx, canvas_image, pdf_from_b64, page_pixels, luminance
with browser() as b:                          # one browser at a time — nested sync_playwright() raises an error
    be = FakeBackend()                        # be.sent = JSON bodies posted to the "Apps Script"; be.mode = "ok" | "badphone" | "offline"
    ctx = new_context(b, be)                  # kind="phone" → 390×844 touch; kind=(1366,768); heic="offline"|"ok"; heic_delay=0.8
    p = open_page(ctx, "print/index.html", errors)
    p.set_input_files("#fileInput", fx("p6.pdf"))
```

**Old Windows PC without ₹** — `with browser(old_pc_fonts=True) as ob:` (FONTCONFIG_FILE → Liberation fonts only). To prove a glyph is real, screenshot a span with `₹` and a span with an unassigned char (`\uE000`); identical bytes = empty box.

**Locked-down preview window** — copy the page, insert `<meta http-equiv="Content-Security-Policy" content="img-src data: https:">` after `<head>` (variants: `img-src https:`; a strict `default-src 'none'` policy) and open that copy.

**Touch** — `cdp = ctx.new_cdp_session(p); cdp.send("Input.dispatchTouchEvent", {"type":"touchStart","touchPoints":[{"x":x,"y":y,"id":0}]})`, then `touchMove`…, `touchEnd` with `[]`. Two ids = pinch. Scroll the element into view first.

**Canvas pixels** — `canvas_image(p, "#editorImg")` → PIL RGBA. Alpha < 200 = outside the photo. Classify marker colours by nearest of red/green/blue/yellow.

**Sliders** — set `value` and dispatch an `input` event in `evaluate`; for a rotated (upright) range use real mouse drags on its bounding box.

**Downloads** — `new_context(b, accept_downloads=True)`; `with p.expect_download() as dl: …click…`; check the first 4 bytes are `%PDF`.

**Exact text** — buttons are uppercase via CSS: use `p.text_content(sel)`, not `inner_text`.

**Listener** — `tests/test_listener.py` starts an HTTP server that behaves like the Apps Script and a shell script that behaves like SumatraPDF, runs `listener.py` as a subprocess for a few seconds, then inspects the calls.

**Geometry assertions** — straightness: cell width top÷bottom within 4% of 1.0; level paper: top-edge height difference at 25%/75% ≤ 3 px; upright frame: dot0.x≈dot3.x and dot0.y≈dot1.y within 1.5 px.

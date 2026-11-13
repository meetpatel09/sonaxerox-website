#!/usr/bin/env python3
"""/scan/ — opening photos: JPG/PNG/HEIC, broken files, huge and transparent images, and locked-down windows (previews) that block blob images.   (--slow adds a 54-megapixel photo)"""
import sys, tempfile, time
from common import *
from scan_helpers import *
import make_fixtures

SLOW = "--slow" in sys.argv
make_fixtures.ensure(slow=SLOW)
rep, errors = Report("Scan page — opening photos"), []
ALL4 = ["red", "green", "blue", "yellow"]
errtext = lambda p: p.locator("#errNote").inner_text().strip() if p.locator("#errNote").is_visible() else ""
SCAN = (REPO / "scan/index.html").read_text(encoding="utf-8")

CSPS = {   # what a sandboxed preview window might enforce
    "blob images blocked": "img-src data: https:",
    "blob + data images blocked": "img-src https:",
    "strict (default-src none)": "default-src 'none'; script-src 'unsafe-inline' https:; style-src 'unsafe-inline' https:; img-src data: https:; font-src https: data:; connect-src https:",
}
tmp = Path(tempfile.mkdtemp())
for i, (name, csp) in enumerate(CSPS.items()):
    (tmp / f"csp{i}.html").write_text(SCAN.replace("<head>", f'<head><meta http-equiv="Content-Security-Policy" content="{csp}">', 1), encoding="utf-8")


def open_file(ctx, fixture, url=None):
    p = ctx.new_page(); p.on("pageerror", lambda e: errors.append(str(e))); p.goto(url or page_url("scan/index.html"))
    p.set_input_files("#fileInput", fx(fixture)); return p


with browser() as b:
    # ---------- normal formats ----------
    ctx = new_context(b)
    for fixture, label_ in (("markers.jpg", "JPG"), ("logo.png", "PNG"), ("doc_photo.jpg", "JPG with a phone's EXIF rotation"), ("big.jpg", "6000×4500 JPG")):
        p = open_file(ctx, fixture); p.wait_for_timeout(2500)
        rep.check(f"{label_} opens on the corners screen", p.locator("#editorImg").count() > 0 and errtext(p) == "", errtext(p)); p.close()
    p = open_file(ctx, "logo.png"); p.wait_for_selector("#editorImg", timeout=20000)
    rep.check("a transparent PNG gets a white background (not black)", p.evaluate("Array.from(document.getElementById('editorImg').getContext('2d').getImageData(3,3,1,1).data)") == [255, 255, 255, 255])
    ctx.close()

    # ---------- HEIC (iPhone) ----------
    ctx = new_context(b, heic="ok", heic_delay=0.8); p = open_file(ctx, "markers.heic")
    seen = False
    try:
        p.wait_for_function("document.getElementById('overlay').classList.contains('show') && document.getElementById('overlayText').textContent.includes('Converting')", timeout=3000); seen = True
    except Exception:
        pass
    rep.check("HEIC: a 'Converting your iPhone photo…' message is shown while it works", seen)
    p.wait_for_selector("#editorImg", timeout=60000); p.wait_for_timeout(600)
    rep.check("HEIC opens on the corners screen, overlay gone, dots on the markers", errtext(p) == "" and cdim(p) == [1100, 825] and not p.is_visible("#overlay") and under(p) == ALL4)
    p.click("#rotR"); p.wait_for_timeout(300); p.click("#primaryBtn"); cls, _, _ = scan_corner_classes(p)
    rep.check("HEIC → turned → scanned page comes out right", cls == ["yellow", "red", "green", "blue"], cls)
    ctx.close()
    ctx = new_context(b, heic="offline"); p = open_file(ctx, "markers.heic"); p.wait_for_timeout(2500)
    rep.check("HEIC but the converter cannot load → message about HEIC + internet; page usable again", errtext(p) == "Could not convert this iPhone (HEIC) photo — check your internet connection, or choose a JPG instead" and not p.is_visible("#overlay"))
    p.set_input_files("#fileInput", fx("markers.jpg")); p.wait_for_selector("#editorImg", timeout=20000)
    rep.check("…and a normal JPG works right after", errtext(p) == "")
    ctx.close()

    # ---------- broken files ----------
    ctx = new_context(b); p = ctx.new_page(); p.goto(page_url("scan/index.html"))
    p.set_input_files("#fileInput", fx("garbage.jpg")); p.wait_for_timeout(1000)
    rep.check("a file that is not an image → 'try a JPG or PNG photo'", errtext(p) == "Could not open that image — try a JPG or PNG photo", errtext(p))
    p.set_input_files("#fileInput", fx("fake.heic")); p.wait_for_timeout(3000)
    rep.check("a broken .heic → 'could not read this HEIC photo' (not stuck on 'Converting')", errtext(p) == "Could not read this iPhone (HEIC) photo — please choose a JPG instead" and not p.is_visible("#overlay"))
    if SLOW:
        t0 = time.time(); p.set_input_files("#fileInput", fx("huge.jpg")); p.wait_for_selector("#editorImg", timeout=90000)
        rep.check(f"a 54-megapixel photo opens ({time.time() - t0:.1f}s)", cdim(p)[0] == 1100)
    ctx.close()

    # ---------- locked-down windows (e.g. a sandboxed preview that blocks blob: images) ----------
    for i, name in enumerate(CSPS):
        ctx = new_context(b)
        for fixture in ("markers.jpg", "logo.png"):
            p = open_file(ctx, fixture, url=(tmp / f"csp{i}.html").as_uri()); p.wait_for_timeout(2000)
            rep.check(f"locked-down window ({name}): {fixture} still opens", p.locator("#editorImg").count() > 0 and errtext(p) == "", errtext(p)); p.close()
        ctx.close()
    ctx = new_context(b, accept_downloads=True); p = open_file(ctx, "tilted_paper.jpg", url=(tmp / "csp0.html").as_uri()); p.wait_for_selector("#editorImg", timeout=20000)
    p.click("#primaryBtn"); p.wait_for_selector("#adjCanvas", timeout=30000); p.click("#primaryBtn"); p.wait_for_timeout(1500)
    with p.expect_download(timeout=20000) as dl:
        p.locator("footer button", has_text="Download").first.click()
    pdf_ok = open(dl.value.path(), "rb").read(4) == b"%PDF"
    rep.check("locked-down window: the whole flow works, down to the downloaded PDF", pdf_ok and p.evaluate("[...document.querySelectorAll('.page-thumb img')].every(i=>i.complete&&i.naturalWidth>0)"))
    ctx.close()

sys.exit(rep.finish(errors))

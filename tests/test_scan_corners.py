#!/usr/bin/env python3
"""/scan/ — the corner screen: turn buttons, Straighten line, dots that follow the photo, the scan following what you see, laptop + phone."""
import sys
from common import *
from scan_helpers import *
import make_fixtures

make_fixtures.ensure()
rep, errors = Report("Scan page — corners, turning, straightening"), []
ALL4 = ["red", "green", "blue", "yellow"]

with browser() as b:
    ctx = new_context(b); p = open_corners(ctx, errors, "markers.jpg")
    rep.check("turn-left, turn-right buttons and the Straighten line exist", all(p.locator(s).count() == 1 for s in ("#rotL", "#rotR", "#rotRange")))
    rep.check("starts at 0.0° and Reset is hidden", label(p) == "0.0°" and not p.is_visible("#rotReset"))
    start, c0 = dots(p)["pts"], cdim(p)
    rep.check("photo is shown on a canvas (1100 × 825) and each dot starts on its own marker", c0 == [1100, 825] and under(p) == ALL4, under(p))

    # ---- 90° buttons ----
    p.click("#rotR"); p.wait_for_timeout(300); d = dots(p)
    rep.check("turn right: portrait, and the dots TURNED WITH THE PHOTO (red dot is now top-right)", cdim(p) == [825, 1100] and under(p) == ALL4 and d["pts"][0][0] > d["vw"] * .5 and d["pts"][0][1] < d["vh"] * .5)
    rep.check("'Reset' appears once turned", p.is_visible("#rotReset"))
    p.click("#rotL"); p.click("#rotL"); p.wait_for_timeout(300); p.click("#rotR"); p.wait_for_timeout(300)
    rep.check("R,L,L,R brings everything back (same size, same dot positions ±1px)", cdim(p) == c0 and all(abs(a[0] - b2[0]) < 1.5 and abs(a[1] - b2[1]) < 1.5 for a, b2 in zip(start, dots(p)["pts"])))
    for _ in range(4): p.click("#rotR"); p.wait_for_timeout(100)
    rep.check("four turns right = full circle", cdim(p) == c0 and under(p) == ALL4)

    # ---- straighten line ----
    set_fine(p, 10)
    rep.check("line at 10: '+10.0°', canvas grows to hold the tilted photo, dots stay on their markers", label(p) == "+10.0°" and cdim(p)[1] > c0[1] and under(p) == ALL4)
    set_fine(p, -7.5); rep.check("negative tilt: '-7.5°'", label(p) == "-7.5°")
    p.dblclick("#rotRange"); p.wait_for_timeout(250)
    rep.check("double-click on the line resets it", label(p) == "0.0°" and cdim(p) == c0)
    bb = p.locator("#rotRange").bounding_box(); cy = bb["y"] + bb["height"] / 2
    p.mouse.move(bb["x"] + bb["width"] / 2, cy); p.mouse.down(); p.mouse.move(bb["x"] + bb["width"] * .75, cy, steps=8); p.mouse.up(); p.wait_for_timeout(300)
    v = float(label(p).replace("°", "").replace("+", ""))
    rep.check("dragging the line with the mouse turns the photo clockwise", 12 <= v <= 30, v)
    p.click("#rotReset"); p.wait_for_timeout(250)
    rep.check("'Reset' restores 0.0° and the original orientation", label(p) == "0.0°" and cdim(p) == c0 and not p.is_visible("#rotReset"))
    p.click("#rotR"); set_fine(p, 12.5); p.click("#resetCorners"); p.wait_for_timeout(300)
    rep.check("'Reset corners' puts the dots back on the turned photo's own starting box", under(p) == ALL4)
    p.click("#rotReset")

    # ---- the scan follows what you see ----
    p.click("#primaryBtn"); cls, w, h = scan_corner_classes(p)
    rep.check("no turn: scanned page has red TL, green TR, blue BR, yellow BL (landscape)", cls == ALL4 and w > h, (cls, w, h))
    p.click("#backCorners"); p.wait_for_selector("#editorImg"); p.wait_for_timeout(400); p.click("#rotR"); p.wait_for_timeout(300)
    p.click("#primaryBtn"); cls, w, h = scan_corner_classes(p)
    rep.check("turned right 90°: the scan is turned too (yellow, red, green, blue) and portrait", cls == ["yellow", "red", "green", "blue"] and h > w, (cls, w, h))
    p.click("#backCorners"); p.wait_for_selector("#editorImg"); p.wait_for_timeout(400)
    rep.check("'Redo corners' remembers the turn", cdim(p) == [825, 1100] and under(p) == ALL4)
    p.click("#rotL"); p.wait_for_timeout(200); p.click("#rotL"); p.wait_for_timeout(300); p.click("#primaryBtn")
    cls, _, _ = scan_corner_classes(p)
    rep.check("turned left 90°: opposite orientation (green, blue, yellow, red)", cls == ["green", "blue", "yellow", "red"], cls)
    ctx.close()

    # ---- a really crooked photo ----
    ctx = new_context(b); p = open_corners(ctx, errors, "tilted_paper.jpg")
    t0 = paper_tilt(editor_png(p)); set_fine(p, -12); good = paper_tilt(editor_png(p)); set_fine(p, 12); bad = paper_tilt(editor_png(p))
    rep.check("a paper tilted 12° looks level at -12° (and not at +12°)", t0 >= 30 and good <= 3 and good < bad, f"{t0:.0f}px off at 0°, {good:.0f}px at -12°, {bad:.0f}px at +12°")
    set_fine(p, -12); img = editor_png(p); arr = np.asarray(img).astype(int); box = p.locator("#editorImg").bounding_box(); sc = box["width"] / img.size[0]
    for i, k in enumerate(ALL4):
        r, g, b2 = COL[k]; m = (abs(arr[..., 0] - r) < 45) & (abs(arr[..., 1] - g) < 45) & (abs(arr[..., 2] - b2) < 45) & (arr[..., 3] > 200)
        ys, xs = np.where(m); dd = dots(p); pt = dd["pts"][i]
        sx, sy = box["x"] + pt[0] * box["width"] / dd["vw"], box["y"] + pt[1] * box["height"] / dd["vh"]
        p.mouse.move(sx, sy); p.mouse.down(); p.mouse.move(box["x"] + xs.mean() * sc, box["y"] + ys.mean() * sc, steps=6); p.mouse.up()
    p.wait_for_timeout(200); rep.check("dragged dots land on the marked paper corners", under(p) == ALL4)
    p.click("#primaryBtn"); cls, w, h = scan_corner_classes(p)
    rep.check("the straightened scan: paper fills the page, markers in the right corners, portrait", cls == ALL4 and h > w, (cls, w, h))
    ctx.close()

    # ---- laptop sizes: nothing hidden behind the pinned button ----
    for (vw, vh) in ((1280, 900), (1366, 768)):
        ctx = new_context(b, kind=(vw, vh)); p = open_corners(ctx, errors, "markers.jpg")
        hb, fb = p.locator(".rot-hint").bounding_box(), p.locator("footer").bounding_box()
        rep.check(f"laptop {vw}x{vh}: both lines and the hint are visible above the pinned button (no scrolling)", hb["y"] + hb["height"] <= fb["y"] + 1)
        ctx.close()
    ctx = new_context(b, kind=(1280, 680)); p = open_corners(ctx, errors, "markers.jpg"); p.evaluate("window.scrollTo(0,document.body.scrollHeight)"); p.wait_for_timeout(200)
    hb, fb = p.locator(".rot-hint").bounding_box(), p.locator("footer").bounding_box()
    rep.check("very small laptop 1280x680: after scrolling, the hint is visible above the pinned button", hb["y"] + hb["height"] <= fb["y"] + 1)
    p.click("#rotR"); set_fine(p, 8); p.set_viewport_size({"width": 900, "height": 700}); p.wait_for_timeout(500)
    rep.check("window resized: dots stay on their markers", under(p) == ALL4)
    p.click("#cancelUpload"); p.set_input_files("#fileInput", fx("tilted_paper.jpg")); p.wait_for_selector("#editorImg"); p.wait_for_timeout(400)
    rep.check("choosing a different photo starts fresh (0.0°, not turned)", label(p) == "0.0°" and not p.is_visible("#rotReset"))
    ctx.close()

    # ---- phone ----
    ctx = new_context(b, kind="phone"); p = open_corners(ctx, errors, "markers.jpg")
    rep.check("phone: no sideways scroll; the Straighten bar fits the screen", not p.evaluate("document.documentElement.scrollWidth>window.innerWidth") and p.locator("#rotBar").bounding_box()["x"] + p.locator("#rotBar").bounding_box()["width"] <= 390.5)
    p.tap("#rotR"); p.wait_for_timeout(300)
    rep.check("phone: tapping a turn button works and the dots follow", cdim(p)[1] > cdim(p)[0] and under(p) == ALL4)
    cdp = ctx.new_cdp_session(p); bb = p.locator("#rotRange").bounding_box(); y = bb["y"] + bb["height"] / 2
    tch = lambda kind, x, yy: cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [] if kind == "touchEnd" else [{"x": x, "y": yy, "id": 0}]})
    tch("touchStart", bb["x"] + bb["width"] / 2, y)
    for i in range(1, 11): tch("touchMove", bb["x"] + bb["width"] / 2 + i * bb["width"] * .03, y)
    tch("touchEnd", 0, 0); p.wait_for_timeout(300)
    rep.check("phone: dragging the line with a finger works; dots stay on their markers", float(label(p).replace("°", "").replace("+", "")) > 5 and under(p) == ALL4)
    ctx.close()

sys.exit(rep.finish(errors))

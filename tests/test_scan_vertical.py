#!/usr/bin/env python3
"""/scan/ — the upright 'Vertical' slider beside the photo (fixes pages shot from above/below) and the scan it produces."""
import sys
from common import *
from scan_helpers import *
import make_fixtures

make_fixtures.ensure()
rep, errors = Report("Scan page — Vertical slider"), []
ALL4 = ["red", "green", "blue", "yellow"]
tnum = lambda p: float(tval(p).replace("°", "").replace("+", ""))


def valid_width(img, fy):
    a = np.asarray(img); xs = np.where(a[int(fy * a.shape[0]), :, 3] > 200)[0]
    return int(xs.max() - xs.min()) if len(xs) else 0


def frame_upright(d, tol=1.5):
    return abs(d[0][0] - d[3][0]) < tol and abs(d[1][0] - d[2][0]) < tol and abs(d[0][1] - d[1][1]) < tol and abs(d[3][1] - d[2][1]) < tol


with browser() as b:
    ctx = new_context(b); p = open_corners(ctx, errors, "keystone.jpg")
    rep.check("a 'Vertical' line exists and the Straighten line is still under the photo", p.locator("#tiltRange").count() == 1 and "Vertical" in p.inner_text("#tiltBar") and "Straighten" in p.inner_text("#rotBar"))
    tr, cv = p.locator("#tiltRange").bounding_box(), p.locator("#editorImg").bounding_box()
    rep.check("the Vertical line is UPRIGHT and stands on the RIGHT side of the photo, alongside it", tr["height"] > tr["width"] * 3 and tr["x"] >= cv["x"] + cv["width"] - 2 and tr["y"] >= cv["y"] - 5 and tr["y"] + tr["height"] <= cv["y"] + max(cv["height"], 250) + 5, (round(tr["width"]), round(tr["height"])))
    cx, cy = tr["x"] + tr["width"] / 2, tr["y"] + tr["height"] / 2
    p.mouse.move(cx, cy); p.mouse.down(); p.mouse.move(cx, cy - tr["height"] * .25, steps=8); p.mouse.up(); p.wait_for_timeout(300); up = tnum(p)
    p.mouse.move(cx, cy - tr["height"] * .25); p.mouse.down(); p.mouse.move(cx, cy + tr["height"] * .25, steps=10); p.mouse.up(); p.wait_for_timeout(300); down = tnum(p)
    rep.check("real mouse: dragging the knob UP gives a positive value, DOWN a negative one", up > 6 and down < -6, f"up {up:+.1f}°, then down {down:+.1f}°")
    p.dblclick("#tiltRange"); p.wait_for_timeout(300)
    rep.check("starts at 0.0° with its own Reset hidden", tval(p) == "0.0°" and not p.is_visible("#tiltReset"))
    r0 = checker_ratio(editor_png(p)); rep.check("the photo really is squeezed (cells narrower at the top)", r0 < 0.88, f"top/bottom cell width {r0:.2f}")
    set_tilt(p, 24); r24 = checker_ratio(editor_png(p))
    rep.check("Vertical +24° makes the page straight (within 4%)", abs(r24 - 1) < 0.04, f"{r0:.2f} → {r24:.2f}")
    set_tilt(p, -24); rn = checker_ratio(editor_png(p)); set_tilt(p, 12); r12 = checker_ratio(editor_png(p))
    rep.check("works in both directions and smoothly (more up = top wider)", rn < r0 < r12 < r24, f"-24:{rn:.2f} 0:{r0:.2f} +12:{r12:.2f} +24:{r24:.2f}")
    rep.check("label shows '+12.0°' and Reset appears", tval(p) == "+12.0°" and p.is_visible("#tiltReset"))
    p.click("#tiltReset"); p.wait_for_timeout(300)
    rep.check("'Reset' (Vertical) restores the photo", tval(p) == "0.0°" and abs(checker_ratio(editor_png(p)) - r0) < 0.02)

    # ---- the frame ----
    p.click("#resetCorners"); p.wait_for_timeout(200)
    rep.check("the starting frame is an upright rectangle", frame_upright(dots(p)["pts"]))
    set_tilt(p, 24)
    rep.check("after Vertical +24° it is STILL an upright rectangle (it stays, the photo moves under it)", frame_upright(dots(p)["pts"]))
    p.click("#resetCorners"); p.wait_for_timeout(200); a = np.asarray(editor_png(p))
    bx = p.evaluate("(()=>{const s=document.querySelector('#editorWrap svg'),vb=s.viewBox.baseVal,c=document.getElementById('editorImg');return {sx:c.width/vb.width,sy:c.height/vb.height,pts:[...s.querySelectorAll('.corner-handle')].map(h=>[+h.getAttribute('cx'),+h.getAttribute('cy')])}})()")
    inside = [a[min(a.shape[0] - 1, int(y * bx["sy"])), min(a.shape[1] - 1, int(x * bx["sx"])), 3] > 200 for x, y in bx["pts"]]
    rep.check("while squeezed, the starting frame stays fully inside the photo (all 4 dots on the photo)", all(inside), inside)
    # a frame you placed yourself is not refitted
    p.click("#resetCorners"); p.wait_for_timeout(200); set_tilt(p, 0)
    bb2 = p.locator("#editorImg").bounding_box(); dd = dots(p); sx, sy = bb2["width"] / dd["vw"], bb2["height"] / dd["vh"]
    for i in (0, 3):
        px, py = dd["pts"][i]; p.mouse.move(bb2["x"] + px * sx, bb2["y"] + py * sy); p.mouse.down(); p.mouse.move(bb2["x"] + (px + 40) * sx, bb2["y"] + py * sy, steps=5); p.mouse.up()
    p.wait_for_timeout(150); w_before = dots(p)["pts"][1][0] - dots(p)["pts"][0][0]; set_tilt(p, 24); m1 = dots(p)["pts"]
    rep.check("a frame you dragged yourself stays an upright rectangle and is not reset by the line", frame_upright(m1) and abs((m1[1][0] - m1[0][0]) - w_before) > 8)

    # ---- the scan gets the correction ----
    p.click("#resetCorners"); p.wait_for_timeout(200); p.click("#primaryBtn"); p.wait_for_selector("#adjCanvas", timeout=30000); p.wait_for_timeout(1000)
    sr = checker_ratio(canvas_image(p, "#adjCanvas"))
    p.click("#backCorners"); p.wait_for_selector("#editorImg"); p.wait_for_timeout(500)
    rep.check("'Redo corners' remembers the vertical setting", tval(p) == "+24.0°")
    p.click("#tiltReset"); p.wait_for_timeout(300); p.click("#resetCorners"); p.wait_for_timeout(300)
    p.click("#primaryBtn"); p.wait_for_selector("#adjCanvas", timeout=30000); p.wait_for_timeout(1000); sr0 = checker_ratio(canvas_image(p, "#adjCanvas"))
    rep.check("THE SCAN: without the line the squeeze stays in the scan; with it the scanned page is straight", sr0 < 0.92 and abs(sr - 1) < 0.05, f"scanned cell width top/bottom: {sr0:.2f} without, {sr:.2f} with Vertical +24")
    ctx.close()

    # ---- other direction / turning / speed ----
    ctx = new_context(b); p = open_corners(ctx, errors, "keystone_neg.jpg")
    n0 = checker_ratio(editor_png(p)); set_tilt(p, -24); n1 = checker_ratio(editor_png(p))
    rep.check("the other way round (bottom narrower): Vertical -24° straightens it", n0 > 1.12 and abs(n1 - 1) < 0.04, f"{n0:.2f} → {n1:.2f}")
    ctx.close()
    ctx = new_context(b); p = open_corners(ctx, errors, "keystone.jpg"); set_tilt(p, 10)
    img = editor_png(p)
    rep.check("Vertical +10 widens the TOP of the photo", valid_width(img, .05) > valid_width(img, .95) * 1.05)
    p.click("#rotR"); p.wait_for_timeout(500); img2 = editor_png(p)
    rep.check("after turning 90° the squeeze still acts top/bottom of what you SEE", valid_width(img2, .05) > valid_width(img2, .95) * 1.05)
    p.click("#rotReset"); p.wait_for_timeout(300)
    ms = p.evaluate("""async()=>{const r=document.getElementById('tiltRange');const t0=performance.now();for(let i=0;i<12;i++){r.value=(i%2?9:12);r.dispatchEvent(new Event('input',{bubbles:true}));await new Promise(f=>requestAnimationFrame(()=>requestAnimationFrame(f)));}return (performance.now()-t0)/12;}""")
    rep.check(f"dragging the line stays smooth ({ms:.0f} ms per update)", ms < 250)
    ctx.close()
    ctx = new_context(b); p = open_corners(ctx, errors, "markers.jpg"); set_tilt(p, 8); before = under(p); p.click("#rotR"); p.wait_for_timeout(400)
    rep.check("turning with a squeeze set: dots stay on the same spots of the photo", before == under(p))
    ctx.close()

    # ---- phone ----
    ctx = new_context(b, kind="phone"); p = open_corners(ctx, errors, "keystone.jpg")
    tb = p.locator("#tiltBar").bounding_box()
    rep.check("phone: the Vertical column fits the screen, no sideways scroll", tb["x"] + tb["width"] <= 390.5 and not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    cdp = ctx.new_cdp_session(p); bb = p.locator("#tiltRange").bounding_box(); cvb = p.locator("#editorImg").bounding_box()
    tch = lambda kind, x, yy: cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [] if kind == "touchEnd" else [{"x": x, "y": yy, "id": 0}]})
    xm, ym = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
    rep.check("phone: the line is upright beside the photo", bb["height"] > bb["width"] * 3 and xm > cvb["x"] + cvb["width"] - 4)
    tch("touchStart", xm, ym)
    for i in range(1, 9): tch("touchMove", xm, ym - i * bb["height"] * .04)
    tch("touchEnd", 0, 0); p.wait_for_timeout(400)
    rep.check("phone: sliding it UP with a finger gives a positive value", tnum(p) > 4, tval(p))
    p.evaluate("window.scrollTo(0,document.body.scrollHeight)"); p.wait_for_timeout(200)
    rep.check("phone: after scrolling down, the hint is clear of the pinned button", p.locator(".rot-hint").bounding_box()["y"] + p.locator(".rot-hint").bounding_box()["height"] <= p.locator("footer").bounding_box()["y"] + 2)
    ctx.close()

sys.exit(rep.finish(errors))

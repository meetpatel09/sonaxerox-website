#!/usr/bin/env python3
"""/print/ — layout bugs we have already fixed once: the order-received screen on small phones, the footer covering Send, the ₹ sign on old PCs."""
import hashlib, sys
from common import *
import make_fixtures

make_fixtures.ensure()
rep, errors, be = Report("Print page — layout & ₹ glyph"), [], FakeBackend()


def tofu_check(p, selector):
    """Is '₹' drawn as a real glyph (not the same empty box as an unassigned character) in the font this element uses?"""
    p.evaluate("""(sel)=>{ const el=document.querySelector(sel), cs=getComputedStyle(el);
        for(const [id,ch] of [['t_rs','\\u20B9'],['t_box','\\uE000']]){ const s=document.createElement('span'); s.id=id; s.textContent=ch;
          s.style.cssText=`position:fixed;left:10px;top:${id=='t_rs'?10:90}px;font-family:${cs.fontFamily};font-size:${cs.fontSize};font-weight:${cs.fontWeight};color:#000;background:#fff;padding:4px;z-index:99999`;
          document.body.appendChild(s); } }""", selector)
    p.wait_for_timeout(300)
    a, b_ = p.locator("#t_rs").screenshot(), p.locator("#t_box").screenshot()
    p.evaluate("document.getElementById('t_rs').remove(); document.getElementById('t_box').remove()")
    return hashlib.md5(a).hexdigest() != hashlib.md5(b_).hexdigest()


def upload(p, name="p6.pdf"):
    p.set_input_files("#fileInput", fx(name)); p.wait_for_selector("#preview.show", timeout=30000); p.wait_for_timeout(600); p.fill("#phoneInput", "9876543210")


with browser() as b:
    # ---------- order-received screen always reachable ----------
    for (w, h, name) in ((390, 844, "normal phone"), (360, 640, "small phone"), (320, 520, "very small phone")):
        for scroll in ("top", "bottom"):
            ctx = new_context(b, be, (w, h)); p = open_page(ctx, "print/index.html", errors); upload(p)
            p.evaluate("window.scrollTo(0, %s)" % ("0" if scroll == "top" else "document.body.scrollHeight")); p.wait_for_timeout(150)
            p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000); p.wait_for_timeout(900)
            inview = lambda s: (lambda bb: bb["y"] >= -1 and bb["y"] + bb["height"] <= h + 1 and bb["x"] >= -1 and bb["x"] + bb["width"] <= w + 1)(p.locator(s).bounding_box())
            ok = all(inview(s) for s in (".stamp-wrap", "#overlayAmt", "#overlayBreak", "#closeOverlay"))
            if not ok:
                p.evaluate("document.getElementById('overlay').scrollTo(0, 9999)"); p.wait_for_timeout(100); ok = inview("#closeOverlay")
            rep.check(f"{name} {w}x{h}, page scrolled to {scroll}: stamp, amount and 'New order' reachable (clicking Send also proves the zoom bar does not cover it)", ok)
            ctx.close()

# ---------- ₹ on a PC whose fonts have no ₹ (separate browser, started after the first one closed) ----------
if liberation_dir():
    with browser(old_pc_fonts=True) as ob:
        ctx = new_context(ob, be, (430, 900)); p = open_page(ctx, "print/index.html", errors); upload(p)
        for label_, sel in (("big price", ".price-amt"), ("price breakdown", ".price-break"), ("rates on the buttons", ".choice .sub")):
            rep.check(f"old-PC fonts: ₹ shows as a real glyph — {label_}", tofu_check(p, sel))
        p.click("#sendBtn"); p.wait_for_selector("#overlay.show"); p.wait_for_timeout(900)
        for label_, sel in (("amount on the success screen", ".overlay-price b"), ("success breakdown", ".overlay-price small")):
            rep.check(f"old-PC fonts: ₹ shows as a real glyph — {label_}", tofu_check(p, sel))
        ctx.close()
else:
    rep.check("(skipped: Liberation fonts not installed — install fonts-liberation to run the ₹ test)", True)

sys.exit(rep.finish(errors))

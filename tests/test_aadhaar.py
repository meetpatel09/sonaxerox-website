#!/usr/bin/env python3
"""/aadhaar-card/ — open an e-Aadhaar PDF (also password-protected), crop the two cards, and the Scale-text and Burn tools."""
import sys
from common import *
import make_fixtures

make_fixtures.ensure()
rep, errors = Report("Aadhaar card tool"), []
PASSWORD = "TESTPASS1"                                    # the password of tests/.fixtures/card_locked.pdf


def open_card(ctx, pdf="card.pdf"):
    p = open_page(ctx, "aadhaar-card/index.html", errors)
    p.set_input_files("#file", fx(pdf))
    if pdf == "card_locked.pdf":
        p.wait_for_selector("#pwdPrompt.show", timeout=30000)
        return p
    p.wait_for_selector("#editor", state="visible", timeout=60000); p.wait_for_timeout(400)
    return p


def P(p, x, y):
    b = p.locator("#canvas").bounding_box(); w, h = p.evaluate("[canvas.width,canvas.height]")
    return b["x"] + x * b["width"] / w, b["y"] + y * b["height"] / h


def drag(p, x0, y0, x1, y1, steps=8):
    p.mouse.move(*P(p, x0, y0)); p.mouse.down(); p.mouse.move(*P(p, x1, y1), steps=steps); p.mouse.up()


snap = lambda p: p.evaluate("window.__s=wctx().getImageData(0,0,work().width,work().height).data.slice()")
changed = lambda p: p.evaluate("(()=>{const d=wctx().getImageData(0,0,work().width,work().height).data,s=window.__s;let n=0;for(let i=0;i<d.length;i+=4){if(d[i]!==s[i]||d[i+1]!==s[i+1]||d[i+2]!==s[i+2])n++;}return n;})()")


def ink_bbox(p, x0, y0, x1, y1, thr=190):
    return p.evaluate("""([x0,y0,x1,y1,thr])=>{const d=wctx().getImageData(x0,y0,x1-x0,y1-y0);let a=1e9,b=1e9,c=-1,e=-1;
      for(let y=0;y<d.height;y++)for(let x=0;x<d.width;x++){const i=(y*d.width+x)*4,l=.299*d.data[i]+.587*d.data[i+1]+.114*d.data[i+2];if(l<thr){if(x<a)a=x;if(y<b)b=y;if(x>c)c=x;if(y>e)e=y;}}
      return c<0?null:{x:x0+a,y:y0+b,w:c-a+1,h:e-b+1};}""", [x0, y0, x1, y1, thr])


def mean_ink(p, x0, y0, x1, y1, thr=200):
    return p.evaluate("""([x0,y0,x1,y1,thr])=>{const d=wctx().getImageData(x0,y0,x1-x0,y1-y0);let s=0,n=0;for(let i=0;i<d.data.length;i+=4){const l=.299*d.data[i]+.587*d.data[i+1]+.114*d.data[i+2];if(l<thr){s+=l;n++;}}return n?s/n:255;}""", [x0, y0, x1, y1, thr])


with browser() as b:
    ctx = new_context(b); p = open_card(ctx)
    rep.check("the PDF opens and the front card is cropped to card size (1011 × 638)", p.evaluate("[canvas.width,canvas.height]") == [1011, 638])
    rep.check("six tools: Sharpen, Bright/Contrast, Saturation, Photo Enhance, Scale text, Burn", p.locator(".tool").count() == 6)
    rep.check("both sides are available (Front / Back)", p.locator(".tab[data-side=back]").count() == 1)
    NB = ink_bbox(p, 290, 170, 700, 255); snap(p)

    # ---------- Scale text ----------
    p.click(".tool[data-tool=scale]")
    drag(p, NB["x"] - 12, NB["y"] - 12, NB["x"] + NB["w"] + 12, NB["y"] + NB["h"] + 12)
    X = p.evaluate("xf?{r:xf.rect,w0:xf.w0,h0:xf.h0}:null")
    rep.check("selecting a box around the name lifts it for scaling (handles appear)", X is not None and not p.is_disabled("#applyBtn"))
    r = X["r"]; drag(p, r["x"] + r["w"], r["y"] + r["h"], r["x"] + r["w"] + .4 * r["w"], r["y"] + r["h"] + .1 * r["h"])
    R = p.evaluate("xf.rect"); k = R["w"] / X["w0"]
    rep.check("dragging the bottom-right corner scales ~140%, proportionally, from the opposite corner", abs(k - 1.4) < .03 and abs(R["h"] / X["h0"] - k) < .01 and abs(R["x"] - r["x"]) <= 1 and p.inner_text("#xfScale") == "140%")
    p.click("#applyBtn"); NB2 = ink_bbox(p, int(R["x"]), int(R["y"]), int(R["x"] + R["w"]) + 1, int(R["y"] + R["h"]) + 1)
    rep.check("Apply commits it: the name is now ~1.4× wider and taller", p.evaluate("xf") is None and NB2 and abs(NB2["w"] / NB["w"] - 1.4) < .05 and abs(NB2["h"] / NB["h"] - 1.4) < .06)
    p.click("#undoBtn"); rep.check("Undo restores the card exactly", changed(p) == 0)
    p.click(".tool[data-tool=sharpen]"); p.click(".tool[data-tool=scale]"); drag(p, NB["x"] - 12, NB["y"] - 12, NB["x"] + NB["w"] + 12, NB["y"] + NB["h"] + 12)
    p.keyboard.down("Shift"); r0 = p.evaluate("xf.rect"); drag(p, r0["x"] + r0["w"], r0["y"] + r0["h"], r0["x"] + r0["w"] + 60, r0["y"] + r0["h"] + 5); p.keyboard.up("Shift")
    R = p.evaluate("xf.rect"); rep.check("holding Shift stretches freely", abs(R["w"] / X["w0"] - R["h"] / X["h0"]) > .08)
    p.keyboard.press("Escape"); rep.check("Esc cancels: card untouched", p.evaluate("xf") is None and changed(p) == 0)
    p.click(".tool[data-tool=scale]"); r0 = p.evaluate("xf.rect"); cx, cy = r0["x"] + r0["w"] / 2, r0["y"] + r0["h"] / 2
    drag(p, cx, cy, cx + 40, cy + 25); R = p.evaluate("xf.rect")
    rep.check("dragging inside the box moves it; Enter applies", abs(R["x"] - r0["x"] - 40) <= 2 and (p.keyboard.press("Enter") or True) and p.evaluate("xf") is None and changed(p) > 0)
    p.click("#undoBtn")

    # ---------- Burn ----------
    p.click(".tool[data-tool=burn]")
    rep.check("Burn shows its own controls, hides the system cursor (brush circle instead)", p.is_visible("[data-for=burn]") and p.evaluate("canvas.style.cursor") == "none")
    p.fill("#brushSize", "36"); p.dispatch_event("#brushSize", "input"); p.fill("#burnStr", "50"); p.dispatch_event("#burnStr", "input")
    before = mean_ink(p, 290, 170, 700, 255)
    white0 = p.evaluate("(()=>{const d=wctx().getImageData(560,150,300,60).data;let s=0,n=0;for(let i=0;i<d.length;i+=4){if(d[i]>=252&&d[i+1]>=250&&d[i+2]>=244){s+=d[i]+d[i+1]+d[i+2];n++;}}return [n,s];})()")
    drag(p, NB["x"] - 10, NB["y"] + NB["h"] / 2, NB["x"] + NB["w"] + 10, NB["y"] + NB["h"] / 2, steps=25)
    rep.check("burning darkens the faded name", mean_ink(p, 290, 170, 700, 255) < before - 12, f"{before:.0f} → {mean_ink(p, 290, 170, 700, 255):.0f}")
    white1 = p.evaluate("(()=>{const d=wctx().getImageData(560,150,300,60).data;let s=0,n=0;for(let i=0;i<d.length;i+=4){if(d[i]>=252&&d[i+1]>=250&&d[i+2]>=244){s+=d[i]+d[i+1]+d[i+2];n++;}}return [n,s];})()")
    rep.check("white paper stays white", white0 == white1)
    p.click("#undoBtn"); rep.check("Undo removes the whole stroke exactly", changed(p) == 0)
    p.click(".tool[data-tool=sharpen]"); drag(p, 300, 170, 560, 260); S = p.evaluate("sel"); p.click(".tool[data-tool=burn]")
    drag(p, 200, 215, 800, 215, steps=40)
    ch = p.evaluate("""(S)=>{const d=wctx().getImageData(0,0,work().width,work().height).data,s=window.__s,W=work().width;let x0=1e9,x1=-1,y0=1e9,y1=-1;
      for(let i=0;i<d.length;i+=4){if(d[i]!==s[i]||d[i+1]!==s[i+1]||d[i+2]!==s[i+2]){const p=i/4,x=p%W,y=(p/W)|0;if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;}}return [x0,y0,x1,y1];}""", S)
    rep.check("with a selection, burn only changes pixels inside it", ch[0] >= S["x"] and ch[2] <= S["x"] + S["w"] and ch[1] >= S["y"] and ch[3] <= S["y"] + S["h"], (ch, S))
    p.keyboard.press("Control+z"); rep.check("Ctrl+Z undoes the stroke", changed(p) == 0)
    ctx.close()

    # ---------- password-protected e-Aadhaar ----------
    ctx = new_context(b); p = open_card(ctx, "card_locked.pdf")
    rep.check("a password-protected e-Aadhaar asks for the password", p.is_visible("#pwdPrompt"))
    p.fill("#pwd", PASSWORD); p.click("#unlockBtn"); p.wait_for_selector("#editor", state="visible", timeout=30000)
    rep.check("…and opens after the right password", p.evaluate("[canvas.width,canvas.height]") == [1011, 638])
    ctx.close()

    # ---------- phone ----------
    ctx = new_context(b, kind="phone"); p = open_card(ctx)
    rep.check("phone: no sideways scroll with the editor open", not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    ctx.close()

sys.exit(rep.finish(errors))

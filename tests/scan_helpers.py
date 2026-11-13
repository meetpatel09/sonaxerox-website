"""Helpers shared by the /scan/ test suites."""
import math
import numpy as np
from common import *

COL = {"red": (230, 20, 30), "green": (20, 200, 40), "blue": (20, 40, 230), "yellow": (250, 220, 0)}


def classify(rgb):
    best = min(COL.items(), key=lambda kv: sum((a - b) ** 2 for a, b in zip(rgb, kv[1])))
    return best[0] if sum((a - b) ** 2 for a, b in zip(rgb, best[1])) < 110 ** 2 * 3 else "other"


def open_corners(ctx, errors, fixture, **kw):
    p = open_page(ctx, "scan/index.html", errors)
    p.set_input_files("#fileInput", fx(fixture))
    p.wait_for_selector("#editorImg", timeout=30000); p.wait_for_timeout(500)
    return p


def dots(p):
    return p.evaluate("""(()=>{const s=document.querySelector('#editorWrap svg'),vb=s.viewBox.baseVal;return {vw:vb.width,vh:vb.height,
      pts:[...s.querySelectorAll('.corner-handle')].map(c=>[+c.getAttribute('cx'),+c.getAttribute('cy')])};})()""")


def colour_under_dots(p):
    return p.evaluate("""(()=>{const cv=document.getElementById('editorImg'),g=cv.getContext('2d'),s=document.querySelector('#editorWrap svg'),vb=s.viewBox.baseVal;
      return [...s.querySelectorAll('.corner-handle')].map(c=>{const x=Math.round(+c.getAttribute('cx')*cv.width/vb.width),y=Math.round(+c.getAttribute('cy')*cv.height/vb.height);
        const d=g.getImageData(Math.max(0,x-4),Math.max(0,y-4),9,9).data;let r=0,gg=0,b=0,n=0;for(let i=0;i<d.length;i+=4){if(d[i+3]>200){r+=d[i];gg+=d[i+1];b+=d[i+2];n++;}}return n?[r/n,gg/n,b/n]:[0,0,0];});})()""")


under = lambda p: [classify(c) for c in colour_under_dots(p)]
cdim = lambda p: p.evaluate("[document.getElementById('editorImg').width,document.getElementById('editorImg').height]")
label = lambda p: p.inner_text("#rotVal").strip()
tval = lambda p: p.inner_text("#tiltVal").strip()


def set_range(p, rid, v):
    p.evaluate("([id,v])=>{const r=document.getElementById(id);r.value=v;r.dispatchEvent(new Event('input',{bubbles:true}));}", [rid, v]); p.wait_for_timeout(300)


set_fine = lambda p, v: set_range(p, "rotRange", v)
set_tilt = lambda p, v: set_range(p, "tiltRange", v)
editor_png = lambda p: canvas_image(p, "#editorImg")


def scan_corner_classes(p):
    """After 'Confirm corners': wait for the adjust screen and classify the colour in each corner of the scanned page."""
    p.wait_for_selector("#adjCanvas", timeout=30000); p.wait_for_timeout(900)
    a = p.evaluate("""(()=>{const c=document.getElementById('adjCanvas'),g=c.getContext('2d'),W=c.width,H=c.height;
      const at=(fx,fy)=>{const x=Math.round(fx*(W-1)),y=Math.round(fy*(H-1)),d=g.getImageData(Math.max(0,x-3),Math.max(0,y-3),7,7).data;let r=0,gg=0,b=0,n=0;for(let i=0;i<d.length;i+=4){r+=d[i];gg+=d[i+1];b+=d[i+2];n++;}return [r/n,gg/n,b/n];};
      return {w:W,h:H,tl:at(.02,.02),tr:at(.98,.02),br:at(.98,.98),bl:at(.02,.98)};})()""")
    return [classify(a[k]) for k in ("tl", "tr", "br", "bl")], a["w"], a["h"]


def checker_spacing(img, fy):
    """Median spacing (px) between black/white checker edges along a row at height fraction fy."""
    a = np.asarray(img).astype(int); H, W = a.shape[:2]; row = a[int(fy * H)]
    lum = row[:, 0] * .299 + row[:, 1] * .587 + row[:, 2] * .114; alive = row[:, 3] > 200
    cls = np.zeros(W, int); cls[(lum < 70) & alive] = -1; cls[(lum > 200) & alive] = 1
    pts, last = [], 0
    for x in range(W):
        if cls[x] != 0:
            if last != 0 and cls[x] != last: pts.append(x)
            last = cls[x]
    d = np.diff(pts); d = d[d > 6]
    return float(np.median(d)) if len(d) >= 3 else float("nan")


def checker_ratio(img):
    """Cell width at the top-most rows that show the pattern ÷ at the bottom-most ones (1.0 = a perfectly straight page)."""
    vals = [(fy, checker_spacing(img, fy)) for fy in np.linspace(0.05, 0.95, 37)]
    vals = [(fy, s) for fy, s in vals if not math.isnan(s)]
    if len(vals) < 8: return float("nan")
    return float(np.mean([s for _, s in vals[:4]]) / np.mean([s for _, s in vals[-4:]]))


def paper_tilt(img):
    """|height difference| of the paper's top edge at 25% and 75% of its width (0 = perfectly level)."""
    a = np.asarray(img).astype(int); lum = a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114
    m = (a[..., 3] > 200) & (lum > 215) & (a[..., 0] > 215) & (a[..., 2] > 200)
    ys, xs = np.where(m); x0, x1 = xs.min(), xs.max(); w = x1 - x0
    top = lambda x: (lambda idx: idx.min() if len(idx) else np.nan)(np.where(m[:, x])[0])
    return abs(top(int(x0 + .25 * w)) - top(int(x0 + .75 * w)))

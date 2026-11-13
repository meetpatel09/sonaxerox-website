#!/usr/bin/env python3
"""/print/ — photos: the 'make it print-friendly' editor, A4 PDF building, multi-photo, edit-again, errors, phone.   (--slow adds the heavy photos)"""
import sys, time
import numpy as np
from common import *
import make_fixtures

SLOW = "--slow" in sys.argv
make_fixtures.ensure(slow=SLOW)
rep, errors, be = Report("Print page — photo editor"), [], FakeBackend()
txt = lambda p, s: p.inner_text(s).strip()
raw = lambda p, s: (p.text_content(s) or "").strip()
ed_open = lambda p: p.evaluate("document.getElementById('edRoot').classList.contains('show')")
GONE = "!document.getElementById('edRoot').classList.contains('show')"


def stats(p):
    return p.evaluate("""(()=>{const c=document.getElementById('edCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
      let w=0,k=0,s=0,n=c.width*c.height,md=0;for(let i=0;i<d.length;i+=4){const l=.299*d[i]+.587*d[i+1]+.114*d[i+2];s+=l;if(l>=245)w++;if(l<100)k++;
        const a=Math.abs(d[i]-d[i+1]),b=Math.abs(d[i+1]-d[i+2]);if(a>md)md=a;if(b>md)md=b;}
      const px=(x,y)=>{const i=(y*c.width+x)*4;return [d[i],d[i+1],d[i+2]]};
      return {white:w/n,dark:k/n,mean:s/n,orient:c.getAttribute('data-orient'),w:c.width,h:c.height,tl:px(2,2),colourDiff:md}})()""")


def pick(p, *names): p.set_input_files("#fileInput", [fx(n) for n in names])
def wait_ed(p, t=60000): p.wait_for_function("document.getElementById('edRoot').classList.contains('show')", timeout=t); p.wait_for_timeout(500)
def style(p, m): p.click(f"[data-mode={m}]"); p.wait_for_timeout(700)
def done(p, t=120000): p.click("#edDone"); p.wait_for_function(GONE, timeout=t); p.wait_for_selector("#preview.show", timeout=30000); p.wait_for_timeout(500)
def send(p):
    p.fill("#phoneInput", "9876543210"); p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=20000)
    return pdf_from_b64(be.sent[-1]["fileData"])


with browser() as b:
    ctx = new_context(b, be)
    p = open_page(ctx, "print/index.html", errors)

    # ---------- one document photo ----------
    pick(p, "doc_photo.jpg"); wait_ed(p)
    st = stats(p)
    rep.check("choosing a photo opens the editor (Gujarati title)", ed_open(p) and txt(p, "#edTitle") == "પ્રિન્ટ માટે તૈયાર કરો")
    rep.check("the phone's EXIF rotation is respected: upright portrait A4", st["orient"] == "portrait" and st["h"] > st["w"])
    rep.check("a document photo is detected → 'Clean document' pre-selected", "active" in p.get_attribute("[data-mode=doc]", "class") and "આપોઆપ પસંદ કર્યું" in txt(p, "#edModeHint"))
    rep.check("clean result: mostly white paper + real dark text", st["white"] > 0.75 and st["dark"] > 0.02, f"white {st['white']:.2f} dark {st['dark']:.3f}")
    style(p, "asis"); rep.check("'As is' keeps the dim yellow photo", stats(p)["white"] < 0.30)
    style(p, "bw"); s2 = stats(p)
    rep.check("'B&W document': white paper, black text, truly greyscale", s2["white"] > 0.75 and s2["dark"] > 0.02 and s2["colourDiff"] <= 2)
    style(p, "doc")
    bx = p.locator("#edCompare").bounding_box(); p.mouse.move(bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2); p.mouse.down(); p.wait_for_timeout(400)
    held = stats(p)["white"]; p.mouse.up(); p.wait_for_timeout(400)
    rep.check("holding 'see original' shows the untouched photo; releasing restores", held < 0.30 and stats(p)["white"] > 0.75)
    p.click("#edRotR"); p.wait_for_timeout(600); land = stats(p)["orient"]; p.click("#edRotL"); p.wait_for_timeout(600)
    rep.check("rotate right → landscape, rotate left → portrait again", land == "landscape" and stats(p)["orient"] == "portrait")
    style(p, "asis"); m0 = stats(p)["mean"]; p.fill("#edBri", "40"); p.dispatch_event("#edBri", "input"); p.wait_for_timeout(700)
    rep.check("Brightness slider brightens", stats(p)["mean"] > m0 + 8 and txt(p, "#edBriV") == "40")
    p.fill("#edBri", "0"); p.dispatch_event("#edBri", "input"); style(p, "doc")
    t0 = time.time(); done(p)
    rep.check(f"Done builds the PDF ({time.time() - t0:.1f}s): file line, preview, price, Edit button",
              txt(p, "#dropText") == "doc_photo.pdf" and txt(p, "#dropSub").startswith("1 ફોટો → 1 પેજ ·") and txt(p, "#pvLabel") == "પેજ 1 / 1" and txt(p, "#priceAmt") == "₹2" and p.is_visible("#editPhotosBtn"))
    pdf = send(p); pg = pdf[0]; L = luminance(page_pixels(pg))
    rep.check("order sent: 1 page, A4 portrait", be.sent[-1]["pages"] == 1 and len(pdf) == 1 and abs(pg.rect.width - 595.28) < 1 and abs(pg.rect.height - 841.89) < 1)
    rep.check("the printed page is white with real black text (not a muddy beige photo)", (L >= 245).mean() > 0.78 and (L < 100).mean() > 0.02, f"white {(L >= 245).mean():.2f}")
    rep.check("PDF is a sensible size (< 15 MB)", len(base64.b64decode(be.sent[-1]["fileData"])) < 15 * 1024 * 1024)
    p.click("#closeOverlay"); rep.check("'New order' forgets the photos", not p.is_visible("#editPhotosBtn"))

    # ---------- colourful dark photo ----------
    pick(p, "photo_dark.jpg"); wait_ed(p)
    rep.check("a normal photo is NOT treated as a document → 'Auto photo'; wide photo → landscape", "active" in p.get_attribute("[data-mode=photo]", "class") and stats(p)["orient"] == "landscape")
    style(p, "asis"); dark = stats(p)["mean"]; style(p, "photo"); rep.check("Auto photo lifts an under-exposed photo", stats(p)["mean"] > dark + 25, f"{dark:.0f} → {stats(p)['mean']:.0f}")
    p.click("[data-fit=fill]"); p.wait_for_timeout(600); sf = stats(p); p.click("[data-fit=fit]"); p.wait_for_timeout(600)
    rep.check("'Fill page' covers the page; 'Fit page' keeps a white border", sf["tl"] != [255, 255, 255] and stats(p)["tl"] == [255, 255, 255])
    p.click("#edClose"); p.wait_for_timeout(300)
    rep.check("closing (✕) cancels and returns to idle", not ed_open(p) and txt(p, "#dropText") == "PDF અથવા ફોટો પસંદ કરવા દબાવો")

    # ---------- several photos ----------
    pick(p, "doc_photo.jpg", "photo_dark.jpg", "logo.png"); wait_ed(p)
    rep.check("3 photos: thumbnails + 'ફોટો 1 / 3'; the document photo gets 'Clean document'", p.locator(".th").count() == 3 and txt(p, "#edCount") == "ફોટો 1 / 3" and "active" in p.get_attribute("[data-mode=doc]", "class"))
    p.locator(".th").nth(1).click(); p.wait_for_timeout(500)
    rep.check("tapping a thumbnail switches photo (its own style)", txt(p, "#edCount") == "ફોટો 2 / 3" and "active" in p.get_attribute("[data-mode=photo]", "class"))
    p.locator(".th").nth(2).locator(".thx").click(); p.wait_for_timeout(400)
    rep.check("✕ on a thumbnail removes that photo", p.locator(".th").count() == 2)
    p.set_input_files("#edAddInput", [fx("logo.png")]); p.wait_for_timeout(1200)
    rep.check("'+ Add photo' adds one", p.locator(".th").count() == 3 and txt(p, "#edCount") == "ફોટો 3 / 3")
    p.locator(".th").nth(0).click(); style(p, "bw"); p.click("#edAll"); p.wait_for_timeout(300); p.locator(".th").nth(1).click(); p.wait_for_timeout(500)
    rep.check("'Apply to all' copies the style to every photo", "active" in p.get_attribute("[data-mode=bw]", "class"))
    style(p, "photo"); done(p)
    rep.check("3 photos → 'photos.pdf', 3 pages, ₹6", txt(p, "#dropText") == "photos.pdf" and txt(p, "#dropSub").startswith("3 ફોટા → 3 પેજ") and txt(p, "#priceAmt") == "₹6")
    pdf = send(p); sizes = [(round(q.rect.width), round(q.rect.height)) for q in pdf]
    rep.check("PDF pages: document portrait, wide photo landscape, square logo portrait", sizes == [(595, 842), (842, 595), (595, 842)], sizes)
    p.click("#closeOverlay")

    # ---------- edit again / cancel ----------
    pick(p, "doc_photo.jpg"); wait_ed(p); done(p)
    p.click("#editPhotosBtn"); wait_ed(p)
    rep.check("'Edit photos' reopens with the same settings", "active" in p.get_attribute("[data-mode=doc]", "class"))
    style(p, "bw"); p.click("#edClose"); p.wait_for_timeout(300)
    rep.check("cancelling a re-edit keeps the earlier PDF", txt(p, "#dropText") == "doc_photo.pdf")
    p.click("#editPhotosBtn"); wait_ed(p); style(p, "bw"); done(p, 60000); p.wait_for_timeout(500)
    pdf = send(p); a = page_pixels(pdf[0], 40)
    rep.check("re-edit to B&W regenerates the PDF (greyscale page)", np.abs(a[..., 0] - a[..., 1]).max() <= 3 and np.abs(a[..., 1] - a[..., 2]).max() <= 3)
    p.click("#closeOverlay")
    p.set_input_files("#fileInput", fx("p6.pdf")); p.wait_for_selector("#preview.show"); p.wait_for_timeout(500)
    pick(p, "photo_dark.jpg"); wait_ed(p); p.click("#edClose"); p.wait_for_timeout(300)
    rep.check("choosing a photo then cancelling keeps the PDF that was already chosen", txt(p, "#dropText") == "p6.pdf" and txt(p, "#priceAmt") == "₹12")

    # ---------- errors ----------
    pick(p, "garbage.jpg"); p.wait_for_timeout(800)
    rep.check("a broken 'photo' → Gujarati error", txt(p, "#dropText") == "આ ફોટો ખૂલતો નથી (JPG અથવા PNG વાપરો)")
    p.set_input_files("#fileInput", [fx("p6.pdf"), fx("logo.png")]); p.wait_for_timeout(300)
    rep.check("PDF + photo together → error", txt(p, "#dropText") == "એક PDF અથવા ફોટા પસંદ કરો — બંને નહીં")
    p.set_input_files("#fileInput", [fx("p6.pdf"), fx("p35.pdf")]); p.wait_for_timeout(300)
    rep.check("two PDFs → error", txt(p, "#dropText") == "કૃપા કરીને ફક્ત એક જ PDF પસંદ કરો")
    p.set_input_files("#fileInput", [fx(f"tiny_{i:02d}.jpg") for i in range(31)]); p.wait_for_timeout(500)
    rep.check("31 photos → 'max 30', editor not opened (and English after the toggle)", txt(p, "#dropText") == "એક ઓર્ડરમાં વધુમાં વધુ 30 ફોટા" and not ed_open(p) and (p.click("#langBtn") or True) and txt(p, "#dropText") == "Max 30 photos per order")
    pick(p, "doc_photo.jpg"); wait_ed(p)
    rep.check("English editor: title, style names, 'Done · 1 page'", txt(p, "#edTitle") == "Make it print-friendly" and raw(p, "[data-mode=doc]") == "Clean document" and raw(p, "#edDone") == "Done · 1 page")
    p.click("#edClose"); p.click("#langBtn")

    # ---------- big photo (+ heavy ones with --slow) ----------
    pick(p, "big.jpg"); wait_ed(p)
    done(p); rep.check("a 6000×4500 photo converts", txt(p, "#dropText") == "big.pdf")
    if SLOW:
        t0 = time.time(); pick(p, *[f"noise_{i}.jpg" for i in range(6)]); wait_ed(p, 120000)
        p.click("#edDone"); p.wait_for_function(f"{GONE} || document.getElementById('edErr').textContent.length>0", timeout=290000); p.wait_for_timeout(500)
        if ed_open(p): rep.check("heavy noisy photos: a clear error instead of hanging", txt(p, "#edErr") != "")
        else:
            mb = float(txt(p, "#dropSub").split("·")[-1].replace("MB", "").strip())
            rep.check(f"6 huge noisy photos are squeezed under 15 MB automatically ({time.time() - t0:.0f}s)", mb <= 15, f"{mb} MB")
    ctx.close()

    # ---------- phone ----------
    ctx = new_context(b, be, "phone"); p = open_page(ctx, "print/index.html", errors)
    pick(p, "doc_photo.jpg", "photo_dark.jpg"); wait_ed(p)
    cb = p.locator(".ed-card").bounding_box()
    rep.check("phone: editor fits the screen, no sideways scroll", cb["x"] >= 0 and cb["x"] + cb["width"] <= 390.5 and not p.evaluate("(()=>{const r=document.getElementById('edRoot');return r.scrollWidth>r.clientWidth})()"))
    p.tap("[data-mode=bw]"); p.wait_for_timeout(700)
    db = p.locator("#edDone").bounding_box()
    rep.check("phone: tapping a style works and the Done button is always visible", "active" in p.get_attribute("[data-mode=bw]", "class") and db["y"] + db["height"] <= 845)
    p.tap("#edDone"); p.wait_for_function(GONE, timeout=90000); p.wait_for_timeout(600)
    rep.check("phone: Done works; no sideways scroll on the page", txt(p, "#dropSub").startswith("2 ફોટા → 2 પેજ") and not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    ctx.close()

sys.exit(rep.finish(errors))

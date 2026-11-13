#!/usr/bin/env python3
"""/print/ — ordering a PDF: Gujarati/English, preview + zoom, page selection, live price, the order that is sent, errors, phone."""
import sys
import numpy as np
from common import *
import make_fixtures

make_fixtures.ensure()
rep, errors, be = Report("Print page — PDF ordering"), [], FakeBackend()
txt = lambda p, s: p.inner_text(s).strip()
raw = lambda p, s: (p.text_content(s) or "").strip()          # ignores CSS text-transform (buttons are shown in capitals)
label = lambda p: txt(p, "#pvLabel")
zoom = lambda p: txt(p, "#pvZoomLabel")


def upload(p, name, wait=True):
    p.set_input_files("#fileInput", fx(name))
    if wait:
        p.wait_for_selector("#preview.show", timeout=30000)
        p.wait_for_function("document.getElementById('pvCanvas').width>10", timeout=30000)
        p.wait_for_timeout(300)


def canvas_ink(p):
    return p.evaluate("(()=>{const c=document.getElementById('pvCanvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=16){if(d[i]<200)n++;}return {w:c.width,ink:n}})()")


with browser() as b:
    ctx = new_context(b, be)
    p = open_page(ctx, "print/index.html", errors)

    # ---------- language ----------
    rep.check("opens in Gujarati by default", p.get_attribute("body", "data-lang") == "gu" and p.get_attribute("html", "lang") == "gu")
    rep.check("Gujarati labels, rates and placeholders",
              "PDF અપલોડ કરો" in txt(p, ".step:nth-of-type(1) .step-label") and raw(p, "#sendBtn") == "દુકાનના પ્રિન્ટર પર મોકલો"
              and txt(p, "#priceBreak") == "બ્લેક & વ્હાઇટ ₹2/પેજ · કલર ₹10/પેજ · લેતી વખતે ચૂકવો" and txt(p, "#priceAmt") == "₹—"
              and p.get_attribute("#phoneInput", "placeholder") == "10 અંકનો મોબાઇલ નંબર")
    p.click("#langBtn")
    rep.check("English: all the main texts", raw(p, "#sendBtn") == "Send to shop printer" and txt(p, "#dropText") == "Tap to choose a PDF or photo"
              and txt(p, "#dropSub") == "PDF, JPG or PNG — photos get a print clean-up" and txt(p, "#priceBreak") == "B&W ₹2/page · Colour ₹10/page · pay at pickup"
              and txt(p, "#rangeHint") == "Upload a PDF first" and p.get_attribute("html", "lang") == "en")
    p.reload()
    rep.check("the language choice is remembered after a reload", raw(p, "#sendBtn") == "Send to shop printer")
    p.click("#langBtn"); p.reload()

    # ---------- preview ----------
    upload(p, "p6.pdf")
    rep.check("file line, hint and price appear as soon as a PDF is chosen",
              txt(p, "#dropText") == "p6.pdf" and txt(p, "#dropSub").startswith("6 પેજ ·") and txt(p, "#rangeHint") == "બધા 6 પેજ પ્રિન્ટ થશે"
              and txt(p, "#priceAmt") == "₹12" and txt(p, "#priceBreak") == "6 પેજ × ₹2 · લેતી વખતે ચૂકવો")
    rep.check("preview shows page 1 / 6 at 100% and the page is really drawn", label(p) == "પેજ 1 / 6" and zoom(p) == "100%" and canvas_ink(p)["ink"] > 20)
    rep.check("‹ is disabled on the first page", p.is_disabled("#pvPrev") and not p.is_disabled("#pvNext"))
    p.click("#pvNext"); p.wait_for_timeout(200)
    rep.check("› goes to page 2", label(p) == "પેજ 2 / 6")
    p.focus("#pvVp"); p.keyboard.press("ArrowRight"); p.wait_for_timeout(150)
    rep.check("keyboard → goes to page 3", label(p) == "પેજ 3 / 6")
    p.keyboard.press("ArrowLeft"); p.wait_for_timeout(150)
    for _ in range(4): p.click("#pvNext"); p.wait_for_timeout(100)
    rep.check("› is disabled on the last page", label(p) == "પેજ 6 / 6" and p.is_disabled("#pvNext"))
    for _ in range(5): p.click("#pvPrev"); p.wait_for_timeout(80)
    w0 = canvas_ink(p)["w"]
    for _ in range(3): p.click("#pvZoomIn")
    z = int(zoom(p).rstrip("%")); p.wait_for_timeout(700)
    rep.check("+ zooms in and the page is redrawn sharper", z >= 270 and canvas_ink(p)["w"] > w0 * 1.5, f"{zoom(p)}, canvas {w0}px -> {canvas_ink(p)['w']}px")
    p.click("#pvZoomOut"); rep.check("− zooms out", int(zoom(p).rstrip("%")) < z)
    p.click("#pvFit"); rep.check("Fit returns to 100%", zoom(p) == "100%")
    box = p.locator("#pvVp").bounding_box(); cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    plain = p.evaluate("(()=>{const e=new WheelEvent('wheel',{deltaY:100,cancelable:true,bubbles:true});document.getElementById('pvVp').dispatchEvent(e);return e.defaultPrevented})()")
    ctrl = p.evaluate("(()=>{const e=new WheelEvent('wheel',{deltaY:-100,ctrlKey:true,cancelable:true,bubbles:true});document.getElementById('pvVp').dispatchEvent(e);return e.defaultPrevented})()")
    rep.check("a plain mouse wheel still scrolls the page; Ctrl+wheel / pinch zooms the preview", plain is False and ctrl is True and int(zoom(p).rstrip("%")) > 100)
    p.click("#pvFit")
    for _ in range(3): p.click("#pvZoomIn")
    tf = lambda: p.evaluate("(()=>{const m=new DOMMatrix(getComputedStyle(document.getElementById('pvStage')).transform);return [m.e,m.f]})()")
    t0 = tf(); p.mouse.move(cx, cy); p.mouse.down(); p.mouse.move(cx - 60, cy - 40, steps=6); p.mouse.up()
    rep.check("dragging moves the zoomed page", tf() != t0)
    zb = zoom(p); p.click("#pvNext"); p.wait_for_timeout(300)
    rep.check("zoom is kept when you flip to the next page", zoom(p) == zb and label(p) == "પેજ 2 / 6")
    p.click("#pvFit"); p.click("#pvPrev"); p.wait_for_timeout(200)
    p.mouse.dblclick(cx, cy); p.wait_for_timeout(100); z1 = zoom(p); p.mouse.dblclick(cx, cy); p.wait_for_timeout(100)
    rep.check("double-click zooms in, again returns to Fit", int(z1.rstrip("%")) >= 240 and zoom(p) == "100%")

    # ---------- page selection + price ----------
    p.click("[data-val=select]"); p.fill("#rangeInput", "2-3")
    rep.check("selection hint (Gujarati)", txt(p, "#rangeHint") == "6 માંથી 2 પેજ પ્રિન્ટ થશે")
    rep.check("preview marks page 1 as not printing", "પ્રિન્ટ નહીં થાય" in label(p))
    p.click("#pvNext"); p.wait_for_timeout(200)
    rep.check("…and page 2 as ✓ will print", "✓" in label(p) and "પ્રિન્ટ થશે" in label(p))
    p.click("#plus"); p.click("#plus")
    rep.check("price: 2 pages x ₹2 x 3 copies = ₹12", txt(p, "#priceAmt") == "₹12" and txt(p, "#priceBreak") == "2 પેજ × ₹2 × 3 કોપી · લેતી વખતે ચૂકવો")
    p.click("#langBtn")
    rep.check("English: hint, price and preview label switch live",
              txt(p, "#rangeHint") == "Printing 2 of 6 pages" and txt(p, "#priceBreak") == "2 pages × ₹2 × 3 copies · pay at pickup" and label(p) == "Page 2 / 6 ✓ will print")
    p.fill("#phoneInput", "9876543210"); p.click("[data-val=color]")
    rep.check("colour recalculates: 2 x ₹10 x 3 = ₹60", txt(p, "#priceAmt") == "₹60")
    p.click("[data-val=bw]"); p.click("#langBtn")

    # ---------- the order ----------
    p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000)
    o = be.sent[-1]; doc = pdf_from_b64(o["fileData"])
    rep.check("payload: 2 pages, 3 copies, B&W, single, phone, file name", o["pages"] == 2 and o["copies"] == 3 and o["color"] == "bw" and o["side"] == "single" and o["phone"] == "9876543210" and o["fileName"] == "p6.pdf")
    rep.check("the uploaded PDF contains ONLY the chosen pages (PAGE-2, PAGE-3)", [pg.get_text().strip().split("\n")[0] for pg in doc] == ["PAGE-2", "PAGE-3"])
    rep.check("success screen: token, amount and how it was worked out", txt(p, "#overlayToken") == "ટોકન #S105" and txt(p, "#overlayAmt") == "₹12" and txt(p, "#overlayBreak") == "2 પેજ × ₹2 × 3 કોપી" and txt(p, "#tokenNo") == "#S105")
    p.click("#closeOverlay")
    rep.check("'નવો ઓર્ડર' resets the page completely", not p.is_visible("#preview") and txt(p, "#priceAmt") == "₹—" and txt(p, "#dropText") == "PDF અથવા ફોટો પસંદ કરવા દબાવો" and txt(p, "#tokenNo") == "#—")

    # ---------- price accuracy ----------
    upload(p, "p6.pdf"); bad = []
    for col, rate in (("bw", 2), ("color", 10)):
        p.click(f"[data-val={col}]")
        while int(txt(p, "#copyCount")) > 1: p.click("#minus")
        for copies in (1, 2, 5, 12):
            while int(txt(p, "#copyCount")) < copies: p.click("#plus")
            if txt(p, "#priceAmt") != f"₹{6 * rate * copies}": bad.append((col, copies, txt(p, "#priceAmt")))
    rep.check("price is right for B&W/colour x 1, 2, 5, 12 copies", not bad, bad or "8 combinations")
    p.click("[data-val=bw]")
    while int(txt(p, "#copyCount")) > 1: p.click("#minus")
    p.click("[data-val=select]"); p.fill("#rangeInput", "3")
    rep.check("single page: '1 પેજ × ₹2' = ₹2", txt(p, "#priceAmt") == "₹2" and txt(p, "#priceBreak") == "1 પેજ × ₹2 · લેતી વખતે ચૂકવો")
    p.fill("#rangeInput", "9"); rep.check("invalid page numbers: no price (₹—)", txt(p, "#priceAmt") == "₹—")

    # ---------- errors ----------
    p.click("[data-val=all]"); upload(p, "p35.pdf")
    rep.check("35 pages in 'all' mode: error, no price, Send disabled", txt(p, "#rangeHint").startswith("PDF માં 35 પેજ છે") and txt(p, "#priceAmt") == "₹—" and p.is_disabled("#sendBtn"))
    p.click("[data-val=select]")
    for val, want in (("1-31", "31 પેજ પસંદ કર્યા — વધુમાં વધુ 30"), ("40", "પેજ નંબર 1 થી 35 વચ્ચે હોવો જોઈએ"), ("abc", "આવા નંબર વાપરો: 1-5, 8")):
        p.fill("#rangeInput", val); rep.check(f"page range '{val}' → Gujarati error", txt(p, "#rangeHint") == want, txt(p, "#rangeHint"))
    p.fill("#rangeInput", "1-3"); p.fill("#phoneInput", "9876543210")
    be.mode = "badphone"; p.click("#sendBtn"); p.wait_for_function("document.getElementById('errNote').classList.contains('show')")
    rep.check("server error 'Invalid phone number' → Gujarati, and English after the toggle", txt(p, "#errNote") == "ફોન નંબર ખોટો છે" and (p.click("#langBtn") or True) and txt(p, "#errNote") == "Invalid phone number")
    p.click("#langBtn")
    be.mode = "offline"; p.click("#sendBtn"); p.wait_for_timeout(600)
    rep.check("no internet → clear message; Send usable again", txt(p, "#errNote") == "ઇન્ટરનેટ નથી — તપાસીને ફરી પ્રયત્ન કરો" and not p.is_disabled("#sendBtn"))
    ctx.close()

    # ---------- phone ----------
    ctx = new_context(b, be, "phone"); be.mode = "ok"
    p = open_page(ctx, "print/index.html", errors)
    lb, tk = p.locator("#langBtn").bounding_box(), p.locator(".ticket-no").bounding_box()
    rep.check("phone: header fits (language button + token inside the screen)", lb["x"] >= 0 and tk["x"] + tk["width"] <= 390)
    upload(p, "p6.pdf")
    rep.check("phone: no sideways scroll", not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    p.evaluate("window.scrollTo(0, document.body.scrollHeight)"); p.wait_for_timeout(200)
    pb, fb = p.locator("#phoneInput").bounding_box(), p.locator("footer").bounding_box()
    rep.check("phone: the price box + Send button never cover the phone-number field", pb["y"] + pb["height"] <= fb["y"] + 1)
    p.evaluate("window.scrollTo(0,0)"); p.locator("#pvVp").scroll_into_view_if_needed(); p.wait_for_timeout(200)
    cdp = ctx.new_cdp_session(p); touch = lambda kind, pts: cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": x, "y": y, "id": i} for i, (x, y) in enumerate(pts)]})
    bx = p.locator("#pvVp").bounding_box(); mx, my = bx["x"] + bx["width"] / 2, bx["y"] + bx["height"] / 2
    rep.check("phone: at Fit a finger still scrolls the page", p.evaluate("document.getElementById('pvVp').style.touchAction") == "pan-y")
    touch("touchStart", [(mx - 25, my), (mx + 25, my)])
    for i in range(1, 11): d = 25 + i * 9; touch("touchMove", [(mx - d, my), (mx + d, my)])
    touch("touchEnd", []); p.wait_for_timeout(250)
    rep.check("phone: two-finger pinch zooms the preview", int(zoom(p).rstrip("%")) >= 200, zoom(p))
    p.tap("#pvFit"); p.wait_for_timeout(100)
    touch("touchStart", [(mx + 80, my)])
    for i in range(1, 9): touch("touchMove", [(mx + 80 - i * 20, my + 2)])
    touch("touchEnd", []); p.wait_for_timeout(300)
    rep.check("phone: swiping left at Fit flips to the next page", label(p) == "પેજ 2 / 6", label(p))
    ctx.close()

sys.exit(rep.finish(errors))

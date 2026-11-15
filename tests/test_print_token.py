#!/usr/bin/env python3
"""/print/ — after ordering: Gujarati WhatsApp message with the token, token picture, recent-orders list on this phone."""
import json, sys, time
from urllib.parse import urlparse, parse_qs
from PIL import Image
from common import *
import make_fixtures

make_fixtures.ensure()
rep, errors, be = Report("Print page — token keepsake (WhatsApp, picture, recent orders)"), [], FakeBackend()
txt = lambda p, s: p.inner_text(s).strip()


def order(p, token="S105", colour=False, double=False, copies=1):
    be.token = token
    p.set_input_files("#fileInput", fx("p6.pdf")); p.wait_for_selector("#preview.show", timeout=30000); p.wait_for_timeout(300)
    if colour: p.click("[data-val=color]")
    if double: p.click("[data-val=double]")
    for _ in range(copies - 1): p.click("#plus")
    p.fill("#phoneInput", "9876543210"); p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000); p.wait_for_timeout(400)


with browser() as b:
    ctx = new_context(b, be, (1280, 900), accept_downloads=True); p = open_page(ctx, "print/index.html", errors)
    rep.check("no 'recent orders' card on a fresh phone", not p.is_visible("#recentCard"))
    order(p, "S105", colour=True, double=True, copies=2)

    # ---------- WhatsApp ----------
    href = p.get_attribute("#waToken", "href"); u = urlparse(href); msg = parse_qs(u.query)["text"][0]
    rep.check("WhatsApp button opens a chat with the shop number (77788 05780)", u.netloc == "wa.me" and u.path == "/917778805780", href[:60])
    rep.check("the message is in Gujarati and has token, pages, colour, sides, copies, amount and the customer's number",
              all(x in msg for x in ("નમસ્તે Sona Xerox", "ટોકન: S105", "6 પેજ · કલર · બંને બાજુ · 2 કોપી", "રકમ: ₹120", "મોબાઇલ: 9876543210")), msg)
    rep.check("the link opens in a new tab (the token screen stays open)", p.get_attribute("#waToken", "target") == "_blank" and "noopener" in p.get_attribute("#waToken", "rel"))
    tog = lambda: p.evaluate("document.getElementById('langBtn').click()")   # the success screen covers the button
    tog()
    rep.check("English page: buttons switch language, but the message to the shop stays Gujarati",
              "WhatsApp" in txt(p, "#waToken") and txt(p, "#saveToken").startswith("⬇ Save token") and "ટોકન: S105" in parse_qs(urlparse(p.get_attribute("#waToken", "href")).query)["text"][0]); tog()

    # ---------- token picture ----------
    p.evaluate("navigator.canShare = undefined")                         # force the plain download path (desktop)
    with p.expect_download(timeout=20000) as dl:
        p.click("#saveToken")
    d = dl.value; path = ART / "token_S105.png"; ART.mkdir(exist_ok=True); d.save_as(str(path))
    im = Image.open(path).convert("RGB")
    ink = sum(1 for px in im.resize((108, 135)).getdata() if sum(px) < 600) / (108 * 135)
    rep.check("'Save token' downloads sonaxerox-token-S105.png", d.suggested_filename == "sonaxerox-token-S105.png")
    rep.check("the picture is a 1080×1350 image with real content (not blank)", im.size == (1080, 1350) and ink > 0.05, (im.size, round(ink, 3)))
    rep.check("the 'Save token' button is usable again afterwards", not p.is_disabled("#saveToken"))
    shared = p.evaluate("""async()=>{ let got=null; navigator.canShare=()=>true; navigator.share=async d=>{got=d.files&&d.files[0]&&d.files[0].name};
        document.getElementById('saveToken').click(); await new Promise(r=>setTimeout(r,1500)); return got }""")
    rep.check("where the phone supports it, 'Save token' opens the share sheet with the picture file", shared == "sonaxerox-token-S105.png", shared)

    # ---------- recent orders ----------
    p.click("#closeOverlay")
    rep.check("after 'New order' the recent-orders card lists the token", p.is_visible("#recentCard") and "S105" in txt(p, "#recentList") and "₹120" in txt(p, "#recentList"))
    pos = (p.locator("#recentCard").bounding_box(), p.locator("#dropZone").bounding_box())
    rep.check("the list is shown above the upload box", pos[0]["y"] < pos[1]["y"])
    p.reload(); p.wait_for_timeout(300)
    rep.check("the list is still there after reloading the page (saved on this phone)", p.is_visible("#recentCard") and "S105" in txt(p, "#recentList"))
    order(p, "S106"); p.click("#closeOverlay")
    rep.check("a new order goes to the top of the list", txt(p, "#recentList").split("\n")[0].strip() == "S106" and p.locator("#recentList li").count() == 2)
    now = int(time.time() * 1000)
    seed = [{"token": "S9%02d" % i, "ts": now - i * 1000, "pages": 6, "copies": 1, "total": 12, "color": "bw", "side": "single", "phone": "9876543210"} for i in range(7)]
    seed.append({"token": "OLD1", "ts": now - 9 * 86400000, "pages": 1, "copies": 1, "total": 2, "color": "bw", "side": "single", "phone": "9876543210"})
    p.evaluate("(s)=>localStorage.setItem('sx_orders', JSON.stringify(s))", seed); p.reload(); p.wait_for_timeout(300)
    shown = p.locator("#recentList .tk").all_inner_texts()
    rep.check("only the last 5 orders are listed, and anything older than 7 days is dropped", shown == ["S900", "S901", "S902", "S903", "S904"], shown)
    p.click("#langBtn")
    rep.check("English: titles switch", txt(p, "#recentCard .card-title") == "Your recent orders" and txt(p, "#recentClear") == "Clear list"); p.click("#langBtn")
    p.click("#recentClear")
    rep.check("'Clear list' empties it and hides the card", not p.is_visible("#recentCard") and p.evaluate("JSON.parse(localStorage.getItem('sx_orders')||'[]').length") == 0)
    p.evaluate("localStorage.setItem('sx_orders', '{not json')"); p.reload(); p.wait_for_timeout(300)
    rep.check("a damaged saved list is ignored (page still works)", not p.is_visible("#recentCard") and p.is_visible("#dropZone"))
    ctx.close()

    # ---------- phone ----------
    ctx = new_context(b, be, "phone"); p = open_page(ctx, "print/index.html", errors); order(p, "S107")
    boxes = [p.locator(s).bounding_box() for s in ("#waToken", "#saveToken")]
    rep.check("phone: both buttons fit the screen width and there is no sideways scroll",
              all(bx["x"] >= 0 and bx["x"] + bx["width"] <= 390 for bx in boxes) and not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    p.evaluate("document.getElementById('overlay').scrollTo(0, 9999)"); p.wait_for_timeout(150)
    cb = p.locator("#closeOverlay").bounding_box()
    rep.check("phone: 'New order' is still reachable after scrolling the success screen", cb["y"] + cb["height"] <= 844 + 1)
    ctx.close()

sys.exit(rep.finish(errors))

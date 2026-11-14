#!/usr/bin/env python3
"""/print/ — redesign features: PDF page editor (rotate, remove, reorder), drag & drop, progress steps, two-column layout on wide screens."""
import sys
from common import *
import make_fixtures

make_fixtures.ensure()
rep, errors, be = Report("Print page — page editor, drag & drop, layout"), [], FakeBackend()
txt = lambda p, s: p.inner_text(s).strip()
raw = lambda p, s: (p.text_content(s) or "").strip()          # ignores CSS text-transform (buttons are shown in capitals)


def upload(p, name="p6.pdf"):
    p.set_input_files("#fileInput", fx(name))
    p.wait_for_selector("#preview.show", timeout=30000)
    p.wait_for_function("document.getElementById('pvCanvas').width>10", timeout=30000)
    p.wait_for_timeout(300)


def first_lines(b64):
    return [pg.get_text().strip().split("\n")[0] for pg in pdf_from_b64(b64)]


with browser() as b:
    # ---------- wide screen: two columns, summary beside the form ----------
    ctx = new_context(b, be, (1280, 900)); p = open_page(ctx, "print/index.html", errors)
    drop, opts, summ = p.locator("#dropZone").bounding_box(), p.locator("#rangeHint").bounding_box(), p.locator("footer.summary").bounding_box()
    rep.check("desktop: upload on the left, options + price/Send on the right", drop["x"] + drop["width"] < opts["x"] and summ["x"] > drop["x"] + drop["width"] and opts["x"] > drop["x"] + drop["width"] and summ["x"] + summ["width"] <= 1280)
    sb = p.locator("footer.summary").bounding_box()
    rep.check("desktop: price + Send are visible on first screen without scrolling", sb["y"] + sb["height"] <= 900)
    rep.check("Send is disabled and says why (file first)", p.is_disabled("#sendBtn") and txt(p, "#sendHint") == "પહેલા પ્રિન્ટ માટે ફાઇલ પસંદ કરો")
    rep.check("desktop: no sideways scroll", not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    rep.check("progress starts at step 1 (upload)", p.evaluate("[...document.querySelectorAll('#progress li')].map(l=>l.className).join(',')") == "current,,")
    rep.check("'Edit pages' button is hidden before a file is chosen", not p.is_visible("#editPagesBtn"))

    upload(p)
    rep.check("progress moves to step 2 once a file is chosen", p.evaluate("[...document.querySelectorAll('#progress li')].map(l=>l.className).join(',')") == "done,current,")
    rep.check("'Edit pages' button appears for a PDF", p.is_visible("#editPagesBtn") and not p.is_visible("#editPhotosBtn"))
    rep.check("…then asks for the phone number", txt(p, "#sendHint") == "મોકલવા માટે તમારો 10 અંકનો ફોન નંબર લખો")
    p.fill("#phoneInput", "9876543210")
    rep.check("hint disappears when ready", txt(p, "#sendHint") == "")
    rep.check("progress moves to step 3 when the order is ready", p.evaluate("[...document.querySelectorAll('#progress li')].map(l=>l.className).join(',')") == "done,done,current")

    # ---------- page editor ----------
    p.click("#editPagesBtn"); p.wait_for_selector("#peRoot.show"); p.wait_for_function("document.querySelectorAll('#peGrid .pe-item').length==6")
    p.wait_for_timeout(1200)
    rep.check("editor shows 6 thumbnails and the page count", txt(p, "#peCount") == "6 પેજ" and raw(p, "#peDone") == "થઈ ગયું · 6 પેજ")
    ink = p.evaluate("(()=>{const c=document.querySelector('#peGrid canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=16){if(d[i]<200)n++;}return n})()")
    rep.check("thumbnails are really drawn", ink > 5, ink)
    rep.check("first page can't move earlier, last can't move later", p.is_disabled("#peGrid .pe-item:first-child .mu") and p.is_disabled("#peGrid .pe-item:last-child .md"))
    p.click("#peGrid .pe-item:nth-child(1) .md")                       # PAGE-1 moves after PAGE-2
    p.click("#peGrid .pe-item:nth-child(3) .rm")                       # remove PAGE-3
    p.click("#peGrid .pe-item:nth-child(1) .rr")                       # rotate (now) first page right
    rep.check("count shows 6 → 5 after removing a page", txt(p, "#peCount") == "6 → 5 પેજ")
    tog = lambda: p.evaluate("document.getElementById('langBtn').click()")   # the editor covers the button, so click it from code
    tog(); rep.check("English: editor texts switch live", txt(p, "#peTitle") == "Edit pages" and raw(p, "#peDone") == "Done · 5 pages"); tog()
    p.click("#peReset")
    rep.check("Reset brings back all 6 pages in order", p.locator("#peGrid .pe-item").count() == 6 and txt(p, "#peCount") == "6 પેજ")
    p.click("#peGrid .pe-item:nth-child(1) .md"); p.click("#peGrid .pe-item:nth-child(3) .rm"); p.click("#peGrid .pe-item:nth-child(1) .rr")
    p.click("#peDone"); p.wait_for_function("!document.getElementById('peRoot').classList.contains('show')", timeout=15000)
    p.wait_for_timeout(400)
    rep.check("after Done the order has 5 pages and the price follows (5 × ₹2 = ₹10)", txt(p, "#rangeHint") == "બધા 5 પેજ પ્રિન્ટ થશે" and txt(p, "#priceAmt") == "₹10" and txt(p, "#dropSub").startswith("5 પેજ"))
    rep.check("the file keeps its name and 'Edit pages' stays available", txt(p, "#dropText") == "p6.pdf" and p.is_visible("#editPagesBtn"))
    p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000)
    o = be.sent[-1]; doc = pdf_from_b64(o["fileData"]); lines = first_lines(o["fileData"])
    rep.check("sent PDF = pages in the new order without the removed one", lines == ["PAGE-2", "PAGE-1", "PAGE-4", "PAGE-5", "PAGE-6"] and o["pages"] == 5, lines)
    rep.check("the rotated page is turned 90°, the others are not", [pg.rotation for pg in doc] == [90, 0, 0, 0, 0], [pg.rotation for pg in doc])
    rep.check("success screen has the shop details and WhatsApp/call buttons", p.is_visible("#overlay .shop-info") and "wa.me/917778805780" in (p.get_attribute("#overlay .btn-ghost.wa", "href") or "") and (p.get_attribute("#overlay a[href^=tel]", "href") or "").endswith("7778805780"))
    p.click("#closeOverlay")
    rep.check("'New order' hides the editor button and resets progress", not p.is_visible("#editPagesBtn") and p.evaluate("[...document.querySelectorAll('#progress li')].map(l=>l.className).join(',')") == "current,,")

    # ---------- editor: can't remove everything; closing cancels ----------
    upload(p)
    p.click("#editPagesBtn"); p.wait_for_function("document.querySelectorAll('#peGrid .pe-item').length==6")
    for _ in range(6): p.click("#peGrid .pe-item:nth-child(1) .rm")
    p.click("#peDone")
    rep.check("removing every page → 'keep at least one page'", txt(p, "#peErr") == "ઓછામાં ઓછું એક પેજ રાખો" and p.is_visible("#peRoot"))
    p.keyboard.press("Escape"); p.wait_for_timeout(200)
    rep.check("Escape closes the editor without changing the file", not p.is_visible("#peRoot") and txt(p, "#rangeHint") == "બધા 6 પેજ પ્રિન્ટ થશે")
    p.click("#editPagesBtn"); p.wait_for_function("document.querySelectorAll('#peGrid .pe-item').length==6")
    p.click("#peDone"); p.wait_for_timeout(300)
    rep.check("Done without changes just closes (file untouched)", not p.is_visible("#peRoot") and txt(p, "#rangeHint") == "બધા 6 પેજ પ્રિન્ટ થશે")

    # ---------- drag & drop ----------
    p.click("#editPagesBtn"); p.keyboard.press("Escape")
    p.evaluate("""async (b64)=>{ const bin=atob(b64), u=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
        const dt=new DataTransfer(); dt.items.add(new File([u],'dropped.pdf',{type:'application/pdf'}));
        const z=document.getElementById('dropZone'); z.dispatchEvent(new DragEvent('dragover',{dataTransfer:dt,bubbles:true,cancelable:true}));
        z.dispatchEvent(new DragEvent('drop',{dataTransfer:dt,bubbles:true,cancelable:true})); }""",
               __import__("base64").b64encode(open(fx("p6.pdf"), "rb").read()).decode())
    p.wait_for_function("document.getElementById('dropText').textContent.trim()==='dropped.pdf'", timeout=15000)
    rep.check("dropping a PDF on the upload box loads it", txt(p, "#dropText") == "dropped.pdf" and txt(p, "#dropSub").startswith("6 પેજ"))
    ctx.close()

    # ---------- copies limit: pages x copies <= 30 (double-sided: 2 pages = 1) ----------
    ctx = new_context(b, be, (1280, 900)); be.mode = "ok"; p = open_page(ctx, "print/index.html", errors)
    upload(p, "p6.pdf")
    def copies_up(n=60):
        for _ in range(n):
            if p.is_disabled("#plus"): break
            p.click("#plus")
        return int(p.input_value("#copyCount"))
    rep.check("6 pages, single-sided: copies stop at 5 (6 x 5 = 30), '+' is disabled", copies_up() == 5 and p.is_disabled("#plus") and txt(p, "#priceAmt") == "₹60")
    rep.check("the hint says how many copies are allowed (Gujarati)", "વધુમાં વધુ 5 કોપી" in txt(p, "#copyHint") and "કુલ 30 પેજ" in txt(p, "#copyHint"))
    p.click("[data-val=double]")
    rep.check("switching to double-sided: 6 pages = 3 sheets → allowed copies rise to 10, '+' works again", not p.is_disabled("#plus") and "વધુમાં વધુ 10 કોપી" in txt(p, "#copyHint"))
    rep.check("…and 10 copies double-sided is accepted (3 x 10 = 30)", copies_up() == 10 and p.is_disabled("#plus"))
    p.click("[data-val=single]")
    rep.check("back to single-sided: copies are pulled down to 5 automatically (never more than the limit)", p.input_value("#copyCount") == "5" and p.is_disabled("#plus"))
    p.click("[data-val=select]"); p.fill("#rangeInput", "1")
    rep.check("choosing just 1 page: up to 30 copies", "વધુમાં વધુ 30 કોપી" in txt(p, "#copyHint") and not p.is_disabled("#plus"))
    rep.check("1 page x 30 copies is allowed, and '+' stops there", copies_up() == 30 and p.is_disabled("#plus"))
    p.fill("#rangeInput", "1-5")
    rep.check("then choosing 5 pages: copies drop to 6 (5 x 6 = 30)", p.input_value("#copyCount") == "6" and p.is_disabled("#plus"))
    p.fill("#rangeInput", "1-3")
    rep.check("odd pages double-sided round up: 3 pages = 2 sheets → max 15 copies", (p.click("[data-val=double]") or True) and "વધુમાં વધુ 15 કોપી" in txt(p, "#copyHint"))
    p.click("#langBtn")
    rep.check("English hint", txt(p, "#copyHint").startswith("Up to 15 copies for this file") and "30 pages in total" in txt(p, "#copyHint")); p.click("#langBtn")
    p.click("[data-val=all]"); p.click("[data-val=single]"); upload(p, "p35.pdf")
    p.click("[data-val=select]"); p.fill("#rangeInput", "1-30")
    rep.check("a 30-page file single-sided: only 1 copy; double-sided (15 sheets): 2 copies", p.is_disabled("#plus") and p.input_value("#copyCount") == "1" and (p.click("[data-val=double]") or True) and copies_up() == 2)
    p.click("[data-val=single]")
    p.fill("#phoneInput", "9876543210"); p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000)
    o = be.sent[-1]
    rep.check("the order sent never exceeds the limit (pages x copies <= 30)", o["pages"] * o["copies"] <= 30, (o["pages"], o["copies"]))
    p.click("#closeOverlay")
    rep.check("'New order' resets copies to 1", p.input_value("#copyCount") == "1" and txt(p, "#copyHint") == "")
    ctx.close()

    # ---------- typing the number of copies ----------
    ctx = new_context(b, be, (1280, 900)); be.mode = "ok"; p = open_page(ctx, "print/index.html", errors)
    import base64 as _b64
    two = REPO / "tests/.fixtures/p2.pdf"
    if not two.exists():                                           # fixtures made before p2.pdf was added
        import pymupdf
        d = pymupdf.open()
        for i in (1, 2): d.new_page().insert_text((72, 120), "PAGE-%d" % i, fontsize=24)
        d.save(str(two))
    p.set_input_files("#fileInput", str(two)); p.wait_for_selector("#preview.show", timeout=30000); p.wait_for_timeout(400)
    cc = lambda: p.input_value("#copyCount")
    def typ(v):                                                   # like a customer: clear the box, then press the keys one by one
        p.fill("#copyCount", ""); p.locator("#copyCount").press_sequentially(v)
    rep.check("copies is a box you can type in (starts at 1)", p.evaluate("document.getElementById('copyCount').tagName") == "INPUT" and cc() == "1")
    typ("7")
    rep.check("typing 7 → 7 copies; price follows (2 pages × ₹2 × 7 = ₹28)", cc() == "7" and txt(p, "#priceAmt") == "₹28")
    typ("50")
    rep.check("typing 50 for a 2-page file (single-sided) is cut to the limit, 15, with a red message", cc() == "15" and "વધુમાં વધુ 15 કોપી જ થઈ શકે" in txt(p, "#copyHint") and p.evaluate("document.getElementById('copyHint').classList.contains('warn')") and p.is_disabled("#plus"))
    p.wait_for_timeout(2800)
    rep.check("…and the normal hint comes back after a moment", "કુલ 30 પેજ" in txt(p, "#copyHint") and not p.evaluate("document.getElementById('copyHint').classList.contains('warn')"))
    p.click("[data-val=double]"); typ("30")
    rep.check("double-sided: typing 30 is accepted (2 pages = 1 sheet)", cc() == "30" and txt(p, "#priceAmt") == "₹120")
    typ("9x4")
    rep.check("letters are ignored — only digits stay (9x4 → 94 → cut to 30)", cc() == "30")
    p.fill("#copyCount", ""); p.click("#phoneInput")
    rep.check("leaving the box empty puts the last number back (never 0 or blank)", cc() == "30" and txt(p, "#priceAmt") == "₹120")
    p.fill("#copyCount", "0"); p.click("#phoneInput")
    rep.check("typing 0 is not accepted — last number stays", cc() == "30")
    p.click("[data-val=single]")
    rep.check("back to single-sided: typed 30 is pulled down to 15", cc() == "15")
    typ("4"); p.click("#plus"); p.click("#plus"); p.click("#minus")
    rep.check("+ and − still work from a typed number (4 → 5)", cc() == "5")
    p.fill("#phoneInput", "9876543210"); typ("12"); p.click("#sendBtn"); p.wait_for_selector("#overlay.show", timeout=15000)
    rep.check("the order sent has the typed copies (12) and stays within the limit", be.sent[-1]["copies"] == 12 and be.sent[-1]["pages"] * be.sent[-1]["copies"] <= 30)
    p.click("#closeOverlay")
    rep.check("'New order' puts the box back to 1", cc() == "1")
    ctx.close()

    # ---------- phone: page editor fits the screen ----------
    ctx = new_context(b, be, "phone"); p = open_page(ctx, "print/index.html", errors); upload(p)
    p.click("#editPagesBtn"); p.wait_for_function("document.querySelectorAll('#peGrid .pe-item').length==6"); p.wait_for_timeout(600)
    rep.check("phone: editor has no sideways scroll", not p.evaluate("(()=>{const r=document.getElementById('peRoot');return r.scrollWidth>r.clientWidth})()"))
    db = p.locator("#peDone").bounding_box()
    rep.check("phone: the Done button is always visible", db["y"] + db["height"] <= 844 + 1 and db["x"] >= 0)
    p.click("#peGrid .pe-item:nth-child(2) .rm"); p.click("#peDone"); p.wait_for_timeout(800)
    rep.check("phone: Done works", txt(p, "#rangeHint") == "બધા 5 પેજ પ્રિન્ટ થશે")
    rep.check("phone: no sideways scroll on the page", not p.evaluate("document.documentElement.scrollWidth>window.innerWidth"))
    ctx.close()

sys.exit(rep.finish(errors))

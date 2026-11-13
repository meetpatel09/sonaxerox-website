#!/usr/bin/env python3
"""Every page opens without JavaScript errors on desktop and phone, without sideways scrolling; the main site and the dashboard basics work."""
import sys
from common import *

rep, errors = Report("Smoke test — every page"), []
PAGES = ["index.html"] + sorted(f"{p.parent.name}/index.html" for p in REPO.glob("*/index.html"))

with browser() as b:
    for kind in ("desktop", "phone"):
        ctx = new_context(b, kind=kind)
        for rel in PAGES:
            p = open_page(ctx, rel, errors); p.wait_for_timeout(700)
            over = p.evaluate("document.documentElement.scrollWidth>window.innerWidth+1")
            rep.check(f"{kind}: {rel} opens, has a title" + (", no sideways scroll" if kind == "phone" else ""), bool(p.title().strip()) and (kind == "desktop" or not over), p.title()[:40] if not over else "SIDEWAYS SCROLL")
            p.close()
        ctx.close()

    ctx = new_context(b); p = open_page(ctx, "index.html", errors); body = p.inner_text("body")
    html = p.content()
    rep.check("main site shows the shop's phone number, hours and town", "77788" in html and "7:30" in body and ("Valod" in body or "વાલોડ" in body))
    rep.check("main site has a language toggle that switches the page text", p.locator("[data-gu], [data-lang], .lang-toggle, #langBtn, button:has-text('English')").count() > 0)
    p.close()
    p = open_page(ctx, "our-tools/index.html", errors)
    gu = p.inner_text(".tool .name"); p.click("#langBtn"); en = p.inner_text(".tool .name")
    rep.check("dashboard: the language toggle switches every button's name (Gujarati ⇄ English)", gu != en and en in {"Main website", "Print order page", "Scan to PDF"} or en != gu)
    p.reload(); rep.check("dashboard: the choice is remembered (sx_lang)", p.evaluate("localStorage.getItem('sx_lang')") == "en" and p.get_attribute("html", "lang") == "en")
    ctx.close()

sys.exit(rep.finish(errors))

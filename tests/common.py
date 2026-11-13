"""Shared helpers for the browser tests.

The pages load pdf-lib / pdf.js / JSZip / heic2any from CDNs. Tests must not depend on the internet, so those
requests are answered from tests/node_modules (same versions). Google Fonts are blocked so results do not depend
on them either. The Apps Script backend is replaced by a fake that records what the page sends.
"""
import base64, io, json, math, os, shutil, subprocess, sys, tempfile, time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
NM = TESTS / "node_modules"
FIX = TESTS / ".fixtures"
ART = TESTS / ".artifacts"          # screenshots from failing / visual checks end up here (git-ignored)


def page_url(rel):
    return (REPO / rel).as_uri()


class Report:
    """Collects PASS/FAIL lines; finish() prints the summary and returns the process exit code."""
    def __init__(self, name):
        self.name, self.results, self.t0 = name, [], time.time()
        print(f"\n=== {name} ===")

    def check(self, label, cond, detail=""):
        ok = bool(cond)
        self.results.append((label, ok))
        print(("  PASS " if ok else "  FAIL ") + label + (f"   -> {detail}" if detail != "" else ""), flush=True)
        return ok

    def finish(self, js_errors=None):
        if js_errors is not None:
            self.check("no JavaScript errors on any page", not js_errors, js_errors[:3] if js_errors else "")
        passed = sum(1 for _, ok in self.results if ok)
        print(f"--- {self.name}: {passed}/{len(self.results)} checks passed ({time.time() - self.t0:.0f}s)")
        return 0 if passed == len(self.results) else 1


# ---------------------------------------------------------------- browser + network faking
class FakeBackend:
    """Stands in for the Google Apps Script web app."""
    def __init__(self):
        self.sent, self.mode, self.token = [], "ok", "S105"

    def handle(self, route):
        if self.mode == "offline":
            return route.abort()
        try:
            self.sent.append(json.loads(route.request.post_data or "{}"))
        except Exception:
            self.sent.append({})
        body = {"ok": True, "token": self.token} if self.mode == "ok" else {"ok": False, "error": "Invalid phone number"}
        route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"}, body=json.dumps(body))


def install_routes(ctx, backend=None, heic="ok", heic_delay=0.0):
    """heic: 'ok' | 'offline' (converter cannot load)."""
    js = "application/javascript"
    ctx.route("https://cdnjs.cloudflare.com/ajax/libs/pdf-lib/**", lambda r: r.fulfill(path=str(NM / "pdf-lib/dist/pdf-lib.min.js"), content_type=js))
    ctx.route("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/**/pdf.min.js", lambda r: r.fulfill(path=str(NM / "pdfjs-dist/build/pdf.min.js"), content_type=js))
    ctx.route("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/**/pdf.worker.min.js", lambda r: r.fulfill(path=str(NM / "pdfjs-dist/build/pdf.worker.min.js"), content_type=js))
    ctx.route("https://cdnjs.cloudflare.com/ajax/libs/jszip/**", lambda r: r.fulfill(path=str(NM / "jszip/dist/jszip.min.js"), content_type=js))

    def heic_handler(route):
        if heic == "offline":
            return route.abort()
        if heic_delay:
            time.sleep(heic_delay)
        route.fulfill(path=str(NM / "heic2any/dist/heic2any.min.js"), content_type=js)
    ctx.route("https://cdnjs.cloudflare.com/ajax/libs/heic2any/**", heic_handler)
    ctx.route("https://fonts.googleapis.com/**", lambda r: r.abort())
    ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
    if backend is not None:
        ctx.route("https://script.google.com/**", backend.handle)


def liberation_dir():
    """Folder with Liberation fonts (they have no ₹ glyph — like an old Windows PC). None if not installed."""
    for base in ("/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype/liberation2", "/usr/share/fonts/liberation"):
        if (Path(base) / "LiberationSans-Regular.ttf").exists():
            return base
    return None


@contextmanager
def browser(old_pc_fonts=False):
    """Headless Chromium. old_pc_fonts=True restricts system fonts to Arial-like ones that lack the ₹ sign."""
    from playwright.sync_api import sync_playwright
    env, tmp = dict(os.environ), None
    if old_pc_fonts:
        d = liberation_dir()
        if not d:
            raise RuntimeError("Liberation fonts not installed")
        tmp = tempfile.mkdtemp()
        Path(tmp, "fonts.conf").write_text(
            f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>{d}</dir><cachedir>{tmp}/cache</cachedir>'
            '<alias binding="same"><family>sans-serif</family><prefer><family>Liberation Sans</family></prefer></alias>'
            '<alias binding="same"><family>monospace</family><prefer><family>Liberation Mono</family></prefer></alias></fontconfig>')
        env["FONTCONFIG_FILE"] = str(Path(tmp, "fonts.conf"))
    with sync_playwright() as p:
        b = p.chromium.launch(env=env)
        try:
            yield b
        finally:
            b.close()
            if tmp:
                shutil.rmtree(tmp, ignore_errors=True)


def new_context(b, backend=None, kind="desktop", heic="ok", heic_delay=0.0, accept_downloads=False):
    kw = {"accept_downloads": accept_downloads}
    if kind == "desktop":
        kw["viewport"] = {"width": 1280, "height": 900}
    elif kind == "laptop":
        kw["viewport"] = {"width": 1366, "height": 768}
    elif kind == "phone":
        kw.update(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
    elif isinstance(kind, tuple):
        kw["viewport"] = {"width": kind[0], "height": kind[1]}
    ctx = b.new_context(**kw)
    install_routes(ctx, backend, heic, heic_delay)
    return ctx


def open_page(ctx, rel, errors):
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"{rel}: {e}"))
    pg.goto(page_url(rel))
    return pg


def fx(name):
    p = FIX / name
    if not p.exists():
        raise FileNotFoundError(f"fixture {name} missing — run tests/make_fixtures.py")
    return str(p)


# ---------------------------------------------------------------- small image / pdf helpers
def png_to_image(data_url):
    return Image.open(io.BytesIO(base64.b64decode(data_url.split(",")[1]))).convert("RGBA")


def canvas_image(page, selector):
    return png_to_image(page.evaluate(f"document.querySelector('{selector}').toDataURL('image/png')"))


def pdf_from_b64(b64):
    import pymupdf
    return pymupdf.open(stream=base64.b64decode(b64), filetype="pdf")


def page_pixels(pdf_page, dpi=50):
    pm = pdf_page.get_pixmap(dpi=dpi)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)[..., :3].astype(int)


def luminance(a):
    return a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114

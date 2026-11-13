#!/usr/bin/env python3
"""tools/new_page.py and tools/verify_live.py."""
import http.server, re, shutil, subprocess, sys, tempfile, threading
from functools import partial
from html.parser import HTMLParser
from pathlib import Path
from common import REPO, Report

rep = Report("Developer tools")


def scratch():
    d = Path(tempfile.mkdtemp()); shutil.copytree(REPO, d / "r", ignore=shutil.ignore_patterns(".git", "node_modules", ".fixtures", "__pycache__")); return d / "r"


def run(cwd, *args):
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True, timeout=60)


r = scratch()
a = run(r, "tools/new_page.py", "photo-resizer", "Photo resizer", "ફોટો રિસાઇઝર", "--rupee")
rep.check("new_page (private): creates the page, adds the dashboard button, adds noindex, bundles the ₹ glyph, stays out of the sitemap",
          a.returncode == 0 and (r / "photo-resizer/index.html").exists() and 'href="/photo-resizer/"' in (r / "our-tools/index.html").read_text(encoding="utf-8")
          and 'content="noindex"' in (r / "photo-resizer/index.html").read_text(encoding="utf-8") and "SX Rupee" in (r / "photo-resizer/index.html").read_text(encoding="utf-8")
          and "photo-resizer" not in (r / "sitemap.xml").read_text(), a.stderr)
b = run(r, "tools/new_page.py", "gallery", "Gallery", "ગેલેરી", "--public", "--paper")
rep.check("new_page (--public --paper): in the sitemap, NOT noindex, cream palette", b.returncode == 0 and "https://sonaxerox.in/gallery/" in (r / "sitemap.xml").read_text() and "noindex" not in (r / "gallery/index.html").read_text(encoding="utf-8") and "#FBFAF6" in (r / "gallery/index.html").read_text(encoding="utf-8"))
rep.check("new_page refuses an existing page and a bad name, changing nothing", run(r, "tools/new_page.py", "gallery", "x", "y").returncode != 0 and run(r, "tools/new_page.py", "Bad Slug", "x", "y").returncode != 0)
for f in ("our-tools/index.html", "photo-resizer/index.html", "gallery/index.html"):
    HTMLParser().feed((r / f).read_text(encoding="utf-8"))
rep.check("the new dashboard buttons have Gujarati and English names", 'data-gu="ફોટો રિસાઇઝર" data-en="Photo resizer"' in (r / "our-tools/index.html").read_text(encoding="utf-8"))
t = run(r, "tests/test_site_structure.py")
rep.check("the project's own structure rules still pass after adding two pages with the scaffold", t.returncode == 0, t.stdout[-300:] if t.returncode else "")

# ---- verify_live ----
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a, **k): pass


site = scratch(); handler = partial(Quiet, directory=str(site))
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler); threading.Thread(target=srv.serve_forever, daemon=True).start(); base = f"http://127.0.0.1:{srv.server_address[1]}"
ok = run(REPO, "tools/verify_live.py", "--base", base)
rep.check("verify_live: a site identical to the repo reports 'All files match' (exit 0)", ok.returncode == 0 and "All files match" in ok.stdout, ok.stdout[-200:])
(site / "print/index.html").write_text("changed"); shutil.rmtree(site / "scan")
bad = run(REPO, "tools/verify_live.py", "--base", base)
rep.check("verify_live: a changed file is DIFFERENT, a missing one MISSING, exit code 1", bad.returncode == 1 and re.search(r"DIFFERENT .*/print/", bad.stdout) and re.search(r"MISSING .*/scan/", bad.stdout))
rep.check("verify_live only checks real site files (not docs / tests / backend)", "/docs/" not in ok.stdout and "/tests/" not in ok.stdout and "/backend/" not in ok.stdout and "listener" not in ok.stdout)
srv.shutdown()
sys.exit(rep.finish())

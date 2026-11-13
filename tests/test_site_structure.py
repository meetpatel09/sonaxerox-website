#!/usr/bin/env python3
"""Static rules for the repository (no browser): the project's standing rules, as tests."""
import re, subprocess, sys
import xml.dom.minidom as minidom
from pathlib import Path
import yaml
from common import REPO, Report

r = Report("Site structure & project rules")
SITE_DIRS = sorted(p.parent.name for p in REPO.glob("*/index.html"))          # folders that are web pages
text = lambda rel: (REPO / rel).read_text(encoding="utf-8")
sm = minidom.parseString(text("sitemap.xml").encode())
locs = [n.firstChild.nodeValue for n in sm.getElementsByTagName("loc")]
PUBLIC = {l.replace("https://sonaxerox.in/", "").strip("/") for l in locs} - {""}        # public pages = the ones listed in sitemap.xml (home page is always public)

# ---- the standing rule: every page has a button on the private dashboard ----
dash = text("our-tools/index.html")
tools_linked = set(re.findall(r'class="tool" href="/([a-z0-9-]+)/"', dash))
missing = [d for d in SITE_DIRS if d != "our-tools" and d not in tools_linked]
r.check("every page has a button on /our-tools/ (standing rule)", not missing, f"missing: {missing}" if missing else f"{len(tools_linked)} buttons for {len(SITE_DIRS) - 1} pages")
broken = [t for t in tools_linked if t not in SITE_DIRS]
r.check("…and every dashboard button points to a page that exists", not broken, broken)
n_buttons = len(re.findall(r'<a class="tool"', dash))
r.check("each dashboard button has Gujarati AND English names", n_buttons == len(re.findall(r'class="name" data-gu="[^"]+" data-en="[^"]+"', dash)), f"{n_buttons} buttons")

# ---- private tools must stay out of Google; public pages (the ones in the sitemap) must not be hidden ----
def robots(rel):
    m = re.search(r'<meta\s+name="robots"\s+content="([^"]*)"', text(rel)); return m.group(1).lower() if m else ""
private_pages = [d for d in SITE_DIRS if d not in PUBLIC]
leaky = [d for d in private_pages if "noindex" not in robots(f"{d}/index.html")]
r.check("every page that is NOT in the sitemap (a private tool) has <meta robots noindex>", not leaky, f"missing on: {leaky}" if leaky else private_pages)
r.check("the dashboard also says nofollow", "nofollow" in robots("our-tools/index.html"))
hidden = [p for p in ["index.html"] + [f"{d}/index.html" for d in PUBLIC] if "noindex" in robots(p)]
r.check("pages listed in the sitemap are NOT noindex (it would contradict the sitemap)", not hidden, hidden)

# ---- sitemap / robots / verification / domain ----
r.check("sitemap.xml is valid XML, lists the home page, and never lists the dashboard or a private tool", "https://sonaxerox.in/" in locs and not any("our-tools" in l for l in locs), locs)
r.check("every sitemap address is a real page", all((REPO / (l.replace("https://sonaxerox.in/", "") + "index.html")).exists() for l in locs))
r.check("robots.txt points to the sitemap and does not hide the private paths (it would advertise them)", "Sitemap: https://sonaxerox.in/sitemap.xml" in text("robots.txt") and not re.search(r"Disallow:\s*/(our-tools|scan|aadhaar|voter|pdf)", text("robots.txt")))
r.check("CNAME is sonaxerox.in", text("CNAME").strip() == "sonaxerox.in")
r.check("Google Search Console verification file is present and correct (never delete it)", text("google96403b7903aa5e97.html").strip() == "google-site-verification: google96403b7903aa5e97.html")
r.check("favicon.png is a real PNG", (REPO / "favicon.png").read_bytes()[:8] == b"\x89PNG\r\n\x1a\n")

# ---- publishing rules: developer folders must not become part of the website ----
cfg = yaml.safe_load(text("_config.yml")) or {}
excluded = set(cfg.get("exclude", []))
dev = {"backend", "shop-pc", "tools", "tests", "docs", "assets-src"}
r.check("_config.yml keeps developer folders off the public website", dev <= excluded, sorted(dev - excluded))
top_dirs = {p.name for p in REPO.iterdir() if p.is_dir() and not p.name.startswith(".") and p.name != "node_modules"}
unknown = top_dirs - set(SITE_DIRS) - dev
r.check("no unexpected top-level folder would be published by accident", not unknown, sorted(unknown))

# ---- every page basics ----
for rel in ["index.html"] + [f"{d}/index.html" for d in SITE_DIRS]:
    s = text(rel)
    ok = bool(re.search(r'<meta\s+charset="utf-8"', s, re.I)) and all(x in s for x in ('name="viewport"', "<title>", 'rel="icon"'))
    r.check(f"{rel}: charset, viewport, title and favicon present", ok)
priced = [rel for rel in ["index.html"] + [f"{d}/index.html" for d in SITE_DIRS] if "₹" in text(rel)]
r.check("any page that shows ₹ bundles the rupee glyph (old PCs draw an empty box otherwise)", all("SX Rupee" in text(p) for p in priced), priced)

# ---- Claude Code project commands (/setup-project, /ship, ...) must have a description ----
cmds = sorted((REPO / ".claude/commands").glob("*.md"))
r.check("every Claude Code slash command has a description and the core four exist",
        {"setup-project", "ship", "verify-live", "new-page"} <= {c.stem for c in cmds} and all(re.search(r"^description: .+", c.read_text(encoding="utf-8"), re.M) for c in cmds), [c.stem for c in cmds])

# ---- a public repository: no secrets ----
files = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True).stdout.split()
if not files:                                                                    # not a git checkout (e.g. a zip): scan the folder instead
    files = [str(p.relative_to(REPO)) for p in REPO.rglob("*") if p.is_file() and ".git" not in p.parts and ".venv" not in p.parts and "node_modules" not in p.parts and ".fixtures" not in p.parts]
bad = []
pat = re.compile(r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|sk-[A-Za-z0-9]{30,})")
for f in files:
    p = REPO / f
    if p.suffix in {".png", ".jpg", ".pdf", ".js", ".heic"} or not p.is_file():
        continue
    if pat.search(p.read_text(encoding="utf-8", errors="ignore")):
        bad.append(f)
r.check("no access tokens / API keys / private keys in the repository", not bad, bad)
secret = re.search(r"var SECRET = '([^']*)'", text("backend/orders-backend.gs"))
r.check("backend/orders-backend.gs only contains the TEMPLATE secret (real one lives only in Apps Script)", secret and secret.group(1) == "CHANGE-ME-sona-valod-2026", secret.group(1) if secret else None)
r.check("the shop PC's real settings file is not tracked", not any(f.endswith("listener.config.json") for f in files))
sys.exit(r.finish())

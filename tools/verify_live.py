#!/usr/bin/env python3
"""Check that the LIVE website serves exactly what is in this repository.

    python3 tools/verify_live.py                      # checks https://sonaxerox.in
    python3 tools/verify_live.py --base http://localhost:8000

Run it ~1-2 minutes after a deploy (GitHub Pages needs a moment). Prints OK / DIFFERENT / MISSING per file; exit code 1 if
anything is not OK. DIFFERENT right after a deploy usually means Pages is still building — wait and run again.
"""
import argparse, hashlib, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"backend", "shop-pc", "tools", "tests", "docs", "assets-src", "node_modules"}
SKIP_FILES = {"CNAME", "_config.yml", "README.md", "CLAUDE.md", "package.json", "package-lock.json", "requirements.txt"}


def site_files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if not p.is_file() or any(part.startswith(".") for part in rel.parts) or rel.parts[0] in SKIP_DIRS or rel.name in SKIP_FILES:
            continue
        yield rel


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--base", default="https://sonaxerox.in"); a = ap.parse_args()
    base = a.base.rstrip("/"); bad = 0
    for rel in site_files():
        url = f"{base}/{rel.as_posix()}"
        if rel.name == "index.html":                      # pages are served from the folder address
            url = f"{base}/{rel.parent.as_posix()}/" if rel.parent.as_posix() != "." else f"{base}/"
        try:
            req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "sx-verify"})
            body = urllib.request.urlopen(req, timeout=30).read()
            ok = hashlib.sha256(body).digest() == hashlib.sha256((ROOT / rel).read_bytes()).digest()
            print(("OK        " if ok else "DIFFERENT ") + url)
            bad += (not ok)
        except urllib.error.HTTPError as e:
            print(f"MISSING   {url}  (HTTP {e.code})"); bad += 1
        except Exception as e:
            print(f"ERROR     {url}  ({e})"); bad += 1
    print("\nAll files match." if not bad else f"\n{bad} problem(s).")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

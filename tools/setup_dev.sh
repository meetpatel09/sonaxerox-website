#!/usr/bin/env bash
# One-time setup of the development tools (Mac or Linux). Safe to run again.
#   bash tools/setup_dev.sh            # full setup, then a quick check
#   bash tools/setup_dev.sh --no-browser   # skip the Chromium download (static checks only)
set -euo pipefail
cd "$(dirname "$0")/.."

say()  { printf '\n\033[1m%s\033[0m\n' "$*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1' — $2"; exit 1; }; }

need git     "install the Xcode command line tools:  xcode-select --install"
need python3 "install Python 3 from python.org (or: brew install python)"
need node    "install Node.js (LTS) from nodejs.org (or: brew install node)"

say "1/5  Python environment (.venv — private to this folder)"
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --quiet --upgrade pip
pip install --quiet -r tests/requirements.txt

if [ "${1:-}" != "--no-browser" ]; then
  say "2/5  Test browser (Chromium, ~150 MB, downloaded once)"
  python -m playwright install chromium
else
  say "2/5  Test browser skipped (--no-browser)"
fi

say "3/5  Test libraries (the same versions the pages load from the CDNs)"
(cd tests && npm ci --no-audit --no-fund)

say "4/5  Test photos and PDFs (generated, never committed)"
python tests/make_fixtures.py

say "5/5  Quick check (no browser needed)"
python tests/run_all.py --fast

cat <<'DONE'

Setup finished.
  Run everything :  .venv/bin/python tests/run_all.py          (about 4 minutes)
  Preview a page :  python3 -m http.server 8000   → http://localhost:8000
  New page       :  .venv/bin/python tools/new_page.py slug "Title" "ગુજરાતી"
Tip: tests were written on Linux; on a Mac a few pixel/font checks may need a small tweak — send the output if one fails.
DONE

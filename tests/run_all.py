#!/usr/bin/env python3
"""Run every test suite and print one summary.

    python3 tests/run_all.py                 # everything except the slow photo tests (~4 min)
    python3 tests/run_all.py --slow          # + 54-megapixel and 6 huge noisy photos (~6 min)
    python3 tests/run_all.py --only scan     # only suites whose name contains "scan"
    python3 tests/run_all.py --fast          # just the quick static + tool checks (~10 s, no browser)

First time on a new computer:  pip install -r tests/requirements.txt && python3 -m playwright install chromium
                               (cd tests && npm install) && python3 tests/make_fixtures.py
"""
import subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITES = [  # (file, needs a browser)
    ("test_site_structure.py", False), ("test_tools.py", False), ("test_listener.py", False),
    ("test_smoke_pages.py", True), ("test_print_pdf.py", True), ("test_print_photos.py", True), ("test_print_layout.py", True), ("test_print_pageedit.py", True),
    ("test_scan_corners.py", True), ("test_scan_vertical.py", True), ("test_scan_open.py", True), ("test_aadhaar.py", True),
]


def main():
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    suites = [(f, br) for f, br in SUITES if (not only or only in f) and (not ("--fast" in args) or not br)]
    if not suites:
        sys.exit("no suite matches")
    subprocess.run([sys.executable, str(HERE / "make_fixtures.py")] + (["--slow"] if "--slow" in args else []), check=True, stdout=subprocess.DEVNULL)
    rows, t0 = [], time.time()
    for f, _ in suites:
        t = time.time()
        proc = subprocess.run([sys.executable, str(HERE / f)] + (["--slow"] if "--slow" in args else []), text=True, capture_output=True, cwd=HERE)
        tail = [l for l in proc.stdout.splitlines() if "checks passed" in l]
        fails = [l.strip() for l in proc.stdout.splitlines() if l.strip().startswith("FAIL")]
        rows.append((f, proc.returncode == 0, tail[-1].split(": ", 1)[-1] if tail else (proc.stderr.strip().splitlines() or ["crashed"])[-1][:90], time.time() - t, fails))
        print(("PASS  " if proc.returncode == 0 else "FAIL  ") + f"{f:28s} {rows[-1][2]}", flush=True)
        for l in fails: print("        " + l[:200])
    ok = all(r[1] for r in rows)
    print(f"\n{'ALL SUITES PASSED' if ok else 'SOME SUITES FAILED'}  ({sum(r[1] for r in rows)}/{len(rows)} suites, {time.time() - t0:.0f}s)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

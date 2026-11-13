#!/usr/bin/env python3
"""shop-pc/listener.py end to end — with a fake Apps Script server and a fake 'SumatraPDF' (nothing is really printed)."""
import base64, http.server, json, os, shutil, stat, subprocess, sys, tempfile, threading, time, urllib.parse
from pathlib import Path
from common import REPO, Report
import make_fixtures

make_fixtures.ensure()
rep = Report("Shop PC listener")
KEY = "test-secret-123"
PDF = (REPO / "tests/.fixtures/p6.pdf").read_bytes()


class State:
    orders = []; calls = []; done = []; errors = []


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        q = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}
        State.calls.append(q.get("action"))
        def out(obj): b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b)
        if q.get("key") != KEY: return out({"ok": False, "error": "Unauthorized"})
        a = q.get("action")
        if a == "pending": return out({"ok": True, "orders": [o for o in State.orders if o["token"] not in State.done and o["token"] not in State.errors]})
        if a == "file": return out({"ok": True, "name": "x.pdf", "data": base64.b64encode(PDF).decode()})
        if a == "done": State.done.append(q["token"]); return out({"ok": True})
        if a == "error": State.errors.append(q["token"]); return out({"ok": True})
        out({"ok": False, "error": "Unknown action"})


def start_server():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler); threading.Thread(target=srv.serve_forever, daemon=True).start(); return srv


def fake_sumatra(folder, exit_code=0):
    p = Path(folder) / "fake_sumatra.sh"
    p.write_text(f'#!/bin/sh\necho "$@" >> "{folder}/printed.log"\nexit {exit_code}\n'); p.chmod(p.stat().st_mode | stat.S_IEXEC); return p


def setup_folder(srv, exit_code=0, key=KEY, poll=1, bom=False):
    d = Path(tempfile.mkdtemp()); shutil.copy(REPO / "shop-pc/listener.py", d / "listener.py")
    cfg = {"BACKEND_URL": f"http://127.0.0.1:{srv.server_address[1]}/script.google.com/exec", "SECRET": key, "PRINTER_BW": "BW Xerox", "PRINTER_COLOR": "Colour Xerox",
           "SUMATRA_PATH": str(fake_sumatra(d, exit_code)), "POLL_SECONDS": poll}
    (d / "listener.config.json").write_bytes((b"\xef\xbb\xbf" if bom else b"") + json.dumps(cfg).encode()); return d


def run_listener(folder, seconds):
    proc = subprocess.Popen([sys.executable, "listener.py"], cwd=folder, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(seconds); proc.terminate()
    try: out, _ = proc.communicate(timeout=10)
    except Exception: proc.kill(); out, _ = proc.communicate()
    return out


srv = start_server()
order = lambda tok, color="B&W", side="Single", copies=1: {"row": 2, "token": tok, "phone": "9876543210", "color": color, "side": side, "copies": copies, "pages": 6, "fileId": "abc"}

# ---- two orders: B&W single, and colour double with 3 copies ----
State.orders = [order("S101"), order("S102", "Colour", "Double", 3)]; State.calls.clear(); State.done.clear(); State.errors.clear()
d = setup_folder(srv, bom=True); out = run_listener(d, 4)
printed = (d / "printed.log").read_text().splitlines() if (d / "printed.log").exists() else []
rep.check("settings are read from listener.config.json (even a Windows-Notepad file with a BOM)", "Sona Xerox listener started" in out and "CONFIG PROBLEMS" not in out)
rep.check("both orders were downloaded, printed and marked PRINTED on the backend", State.done == ["S101", "S102"] and (d / "orders/S101.pdf").exists() and (d / "orders/S102.pdf").exists(), State.done)
rep.check("the downloaded file is the real PDF", (d / "orders/S101.pdf").read_bytes() == PDF)
rep.check("B&W single-sided → black & white printer, 'simplex,monochrome,fit'", len(printed) == 2 and "-print-to BW Xerox" in printed[0] and "-print-settings simplex,monochrome,fit" in printed[0] and "-silent" in printed[0], printed[:1])
rep.check("colour double-sided ×3 → colour printer, 'duplexlong,color,3x,fit'", "-print-to Colour Xerox" in printed[1] and "duplexlong,color,3x,fit" in printed[1], printed[1:])
rep.check("an order is only printed once (not again on the next check)", len(printed) == 2 and State.calls.count("done") == 2)
rep.check("everything is written to listener.log", (d / "listener.log").exists() and "S102 -> PRINTED" in (d / "listener.log").read_text())

# ---- printer fails → ERROR ----
State.orders = [order("S201")]; State.done.clear(); State.errors.clear()
d = setup_folder(srv, exit_code=1); out = run_listener(d, 3)
rep.check("if SumatraPDF fails the order is marked ERROR (and not PRINTED)", State.errors == ["S201"] and State.done == [], (State.errors, State.done))

# ---- wrong secret ----
State.orders = [order("S301")]; State.done.clear(); State.errors.clear()
d = setup_folder(srv, key="wrong"); out = run_listener(d, 3)
rep.check("a wrong SECRET prints nothing and logs 'Unauthorized'", "Unauthorized" in out and not (d / "printed.log").exists() and not State.done)

# ---- the template defaults are refused ----
d = Path(tempfile.mkdtemp()); shutil.copy(REPO / "shop-pc/listener.py", d / "listener.py")
proc = subprocess.run([sys.executable, "listener.py"], cwd=d, capture_output=True, text=True, timeout=30)
rep.check("with the template defaults it refuses to start and says what to fix", proc.returncode == 1 and "BACKEND_URL is not set" in proc.stdout and "SECRET still has the default value" in proc.stdout)
d = Path(tempfile.mkdtemp()); shutil.copy(REPO / "shop-pc/listener.py", d / "listener.py"); (d / "listener.config.json").write_text("{ not json")
proc = subprocess.run([sys.executable, "listener.py"], cwd=d, capture_output=True, text=True, timeout=30)
rep.check("a broken listener.config.json gives a clear message (not a crash trace)", proc.returncode == 1 and "could not be read" in proc.stdout and "Traceback" not in proc.stderr)
rep.check("the example config is valid JSON with every key the listener understands", set(json.loads((REPO / "shop-pc/listener.config.example.json").read_text())) <= {"BACKEND_URL", "SECRET", "PRINTER_BW", "PRINTER_COLOR", "SUMATRA_PATH", "POLL_SECONDS", "CLEANUP_HOURS", "ORDERS_DIR"})
srv.shutdown()
sys.exit(rep.finish())

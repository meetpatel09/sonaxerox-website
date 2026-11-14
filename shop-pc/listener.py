"""
SONA XEROX — SHOP PRINT LISTENER
---------------------------------
Runs on the shop PC. Every few seconds it asks the backend
"any new orders?" — downloads the PDF, sends it to the Xerox
machine with the right settings, and marks the order PRINTED.

SETUP (one time):
  1. Install Python from python.org  (tick "Add Python to PATH")
  2. Install SumatraPDF from sumatrapdfreader.org (free)
  3. Fill in the CONFIG section below
  4. Double-click run-listener.bat to start

No extra Python packages needed — uses only built-in modules.
"""

import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request

# ============================================================
# CONFIG — fill these in
# ============================================================

# Your Apps Script web app URL (same one as in the order page)
BACKEND_URL = "PASTE_YOUR_APPS_SCRIPT_URL_HERE"

# Must EXACTLY match the SECRET in the Apps Script code
SECRET = "CHANGE-ME-sona-valod-2026"

# Exact printer names as shown in Windows > Settings > Printers
# (copy carefully — spelling and spaces must match)
PRINTER_BW = "PASTE_YOUR_BW_XEROX_NAME_HERE"       # black & white orders go here
PRINTER_COLOR = "PASTE_YOUR_COLOR_PRINTER_NAME_HERE"  # colour orders go here
# (If one machine does both, just put the same name in both lines)

# Where SumatraPDF.exe is installed. Common locations:
#   C:\Program Files\SumatraPDF\SumatraPDF.exe
#   C:\Users\YOURNAME\AppData\Local\SumatraPDF\SumatraPDF.exe
SUMATRA_PATH = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"

# How often to check for new orders (seconds)
POLL_SECONDS = 15

# Delete downloaded PDFs from this PC after this many hours
CLEANUP_HOURS = 24

# Only ONE listener may run on this PC (a second copy would print every order twice).
# It holds this local port while it runs; a second copy finds the port taken and exits quietly.
LOCK_PORT = 47651

# Folder where downloaded PDFs are kept (created automatically)
ORDERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders")

# ------------------------------------------------------------
# OPTIONAL: keep your real settings in listener.config.json (same folder as this file).
# Any key in that file replaces the value above, so you can swap in a newer listener.py
# later WITHOUT losing your URL, secret and printer names. See listener.config.example.json.
# ------------------------------------------------------------
def _load_local_config():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listener.config.json")
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8-sig") as fh:      # utf-8-sig: Windows Notepad adds an invisible BOM
            data = json.load(fh)
    except Exception as ex:
        print("listener.config.json could not be read: %s" % ex, flush=True)
        sys.exit(1)
    g = globals()
    for key in ("BACKEND_URL", "SECRET", "PRINTER_BW", "PRINTER_COLOR", "SUMATRA_PATH",
                "POLL_SECONDS", "CLEANUP_HOURS", "ORDERS_DIR", "LOCK_PORT"):
        if key in data:
            g[key] = data[key]


_load_local_config()

# ============================================================


# ------------------------------------------------------------
# Safety 1: never run twice.  Safety 2: never print the same order twice.
# ------------------------------------------------------------
_lock_socket = None
PRINTED_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listener.printed.txt")
PRINTED = set()


def acquire_single_instance_lock():
    """True if this is the only listener on the PC. Works for normal and 'Run as administrator' copies alike."""
    global _lock_socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if os.name == "nt":
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        s.bind(("127.0.0.1", int(LOCK_PORT)))
        s.listen(1)
    except OSError:
        s.close()
        return False
    _lock_socket = s            # keep it open for as long as the program runs
    return True


def printed_key(order):
    return "%s:%s" % (order["token"], order.get("fileId", ""))


def load_printed():
    """Orders already printed on this PC (survives a restart), so a failed 'done' call can never cause a re-print."""
    try:
        with open(PRINTED_FILE, encoding="utf-8") as fh:
            keys = fh.read().split()
    except OSError:
        return set()
    keys = keys[-500:]
    try:
        with open(PRINTED_FILE, "w", encoding="utf-8") as fh:
            fh.write("\n".join(keys) + ("\n" if keys else ""))
    except OSError:
        pass
    return set(keys)


def remember_printed(key):
    PRINTED.add(key)
    try:
        with open(PRINTED_FILE, "a", encoding="utf-8") as fh:
            fh.write(key + "\n")
    except OSError:
        pass


def api(params):
    """Call the backend with query parameters, return parsed JSON."""
    url = BACKEND_URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def log(msg):
    line = time.strftime("[%d-%b %H:%M:%S] ") + msg
    print(line, flush=True)
    # also write to listener.log next to this script (so you can check
    # what happened even when running invisibly in the background)
    try:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "listener.log")
        # simple rotation: if the log grows past 5 MB, archive it
        if os.path.exists(log_path) and os.path.getsize(log_path) > 5 * 1024 * 1024:
            old = log_path + ".old"
            if os.path.exists(old):
                os.remove(old)
            os.replace(log_path, old)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def check_config():
    problems = []
    if "script.google.com" not in BACKEND_URL:
        problems.append("BACKEND_URL is not set")
    if "CHANGE-ME" in SECRET:
        problems.append("SECRET still has the default value — set your own (same in Apps Script)")
    if "PASTE_YOUR" in PRINTER_BW:
        problems.append("PRINTER_BW is not set")
    if "PASTE_YOUR" in PRINTER_COLOR:
        problems.append("PRINTER_COLOR is not set")
    if not os.path.exists(SUMATRA_PATH):
        problems.append("SumatraPDF not found at: " + SUMATRA_PATH)
    if problems:
        log("CONFIG PROBLEMS — fix these at the top of listener.py:")
        for p in problems:
            log("  - " + p)
        sys.exit(1)


def print_settings(order):
    """Build the SumatraPDF -print-settings string from the order."""
    parts = []
    parts.append("duplexlong" if order["side"] == "Double" else "simplex")
    parts.append("color" if order["color"] == "Colour" else "monochrome")
    copies = int(order.get("copies") or 1)
    if copies > 1:
        parts.append(str(copies) + "x")
    parts.append("fit")
    return ",".join(parts)


def handle_order(order):
    token = order["token"]
    if printed_key(order) in PRINTED:
        log("Order %s was already printed on this PC - only telling the backend again (no second print)." % token)
        mark_done(token)
        return
    log("New order %s: %s pages, %s, %s, %s cop%s (phone %s)" % (
        token, order["pages"], order["color"], order["side"],
        order["copies"], "y" if str(order["copies"]) == "1" else "ies",
        order["phone"]))

    # 1) download the PDF
    log("  downloading PDF...")
    f = api({"action": "file", "id": order["fileId"], "key": SECRET})
    if not f.get("ok"):
        raise RuntimeError("file download failed: " + str(f.get("error")))
    pdf_path = os.path.join(ORDERS_DIR, token + ".pdf")
    with open(pdf_path, "wb") as fh:
        fh.write(base64.b64decode(f["data"]))
    log("  saved " + pdf_path)

    # 2) send to the right printer
    printer = PRINTER_COLOR if order["color"] == "Colour" else PRINTER_BW
    settings = print_settings(order)
    log("  printing on '%s' with settings: %s" % (printer, settings))
    cmd = [SUMATRA_PATH, "-print-to", printer,
           "-print-settings", settings, "-silent", pdf_path]
    result = subprocess.run(cmd, capture_output=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError("SumatraPDF exited with code %d" % result.returncode)

    # 3) remember it here FIRST, then tell the backend (so a failed call can never cause a second print)
    remember_printed(printed_key(order))
    mark_done(token)


def mark_done(token):
    for attempt in range(3):
        try:
            r = api({"action": "done", "token": token, "key": SECRET})
            if r.get("ok") is not False:
                log("  order %s -> PRINTED" % token)
                return True
            log("  backend refused 'done' for %s: %s" % (token, r.get("error")))
        except Exception as ex:
            log("  could not mark %s as PRINTED (try %d of 3): %s" % (token, attempt + 1, ex))
        time.sleep(2)
    log("  order %s IS printed, but the backend was not told. It will NOT be printed again; will retry telling it." % token)
    return False


def cleanup_old_files():
    """Delete PDFs in the orders folder older than CLEANUP_HOURS."""
    cutoff = time.time() - CLEANUP_HOURS * 3600
    removed = 0
    try:
        for name in os.listdir(ORDERS_DIR):
            path = os.path.join(ORDERS_DIR, name)
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                try:
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass  # file may be open in the print spooler; try next hour
        if removed:
            log("Cleanup: deleted %d old PDF(s) from this PC" % removed)
    except OSError:
        pass


def main():
    if not acquire_single_instance_lock():
        # silent in the log on purpose: the auto-start check runs every minute
        print("Another Sona Xerox listener is already running on this PC - this copy is not needed and will close.", flush=True)
        sys.exit(3)
    check_config()
    PRINTED.update(load_printed())
    os.makedirs(ORDERS_DIR, exist_ok=True)
    log("Sona Xerox listener started. Checking every %ds. Press Ctrl+C to stop." % POLL_SECONDS)

    last_cleanup = 0.0

    while True:
        # run local cleanup once per hour
        if time.time() - last_cleanup > 3600:
            cleanup_old_files()
            last_cleanup = time.time()

        try:
            resp = api({"action": "pending", "key": SECRET})
            if not resp.get("ok"):
                log("Backend error: " + str(resp.get("error")))
            else:
                orders = resp.get("orders", [])
                for order in orders:
                    try:
                        handle_order(order)
                    except Exception as ex:
                        log("  ERROR on order %s: %s" % (order.get("token"), ex))
                        try:
                            api({"action": "error", "token": order["token"], "key": SECRET})
                        except Exception:
                            pass
        except KeyboardInterrupt:
            log("Stopped by user.")
            return
        except Exception as ex:
            log("Network/other error (will retry): %s" % ex)

        try:
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            log("Stopped by user.")
            return


if __name__ == "__main__":
    main()

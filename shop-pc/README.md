# Shop PC — print listener

Runs on the Windows PC at the shop. Every 15 seconds it asks the backend "any new orders?", downloads the PDF,
sends it to the right printer with the right settings (colour/B&W, single/double side, copies) and marks the order
`PRINTED`. No Python packages needed — only built-in modules.

| File | What it does |
|---|---|
| `listener.py` | the listener itself |
| `listener.config.json` | **your** settings (URL, secret, printer names). Create it from `listener.config.example.json`. **Never commit it** (it is git-ignored). |
| `run-listener.bat` | start with a visible window (use this to debug) |
| `start-listener-hidden.vbs` | start invisibly (`pythonw`); a shortcut to this file in `shell:startup` makes it start with Windows |
| `stop-listener.bat` | stop the hidden listener |
| `run-listener-forever.bat` | visible window that **restarts the listener if it stops** (close the window to stop) |
| `install-autostart.bat` | **recommended:** Windows checks every minute and starts the listener if it is not running (after restart, crash or accidental close) |
| `keep-listener-running.vbs` | the check used by the task above (starts the listener invisibly only if it is not running) |
| `remove-autostart.bat` | switches the auto-start off and stops the listener |
| `listener.log` | what happened (rotates at 5 MB) |
| `orders/` | downloaded PDFs, deleted automatically after 24 hours |

## One-time setup
1. Install **Python** (python.org, tick *Add Python to PATH*) and **SumatraPDF** (free).
2. Copy this folder to a drive that is **not** `C:` (so a Windows reset cannot wipe it).
3. Copy `listener.config.example.json` to `listener.config.json` and fill it in:
   - `BACKEND_URL` — the Apps Script *web app* URL (ends with `/exec`)
   - `SECRET` — must be **exactly** the `SECRET` in the Apps Script (and **not** the default `CHANGE-ME…`)
   - `PRINTER_BW` / `PRINTER_COLOR` — exact names from *Windows → Settings → Printers* (same name in both if one machine does both)
4. Double-click `run-listener.bat`. You should see `Sona Xerox listener started`.
5. When it works: double-click `install-autostart.bat` once. From then on the listener starts with Windows and comes back by itself within a minute if it is closed or crashes.
   (Old way: a shortcut to `start-listener-hidden.vbs` in `shell:startup` — it starts the listener at login but does not bring it back.)
6. The listener now **allows only ONE copy on the PC**: a second copy (auto-start + an open window, or a copy started with "Run as administrator") closes by itself, so an order can never print twice because of that.
   To stop it for real, run `remove-autostart.bat` first (otherwise it restarts within a minute).

## Updating the listener
Stop every running listener first (`remove-autostart.bat`, or end all `python.exe` / `pythonw.exe` in Task Manager), then replace `listener.py` with the new version from GitHub. Your `listener.config.json` is untouched, so nothing to re-enter. Start again with `install-autostart.bat`.

`listener.printed.txt` (next to `listener.py`) remembers which orders were already printed on this PC — it is what stops a re-print if the backend could not be told. Do not delete it while orders are waiting.

## Troubleshooting
| Symptom | Check |
|---|---|
| `CONFIG PROBLEMS` in the log | the message says which setting is wrong |
| `Unauthorized` | `SECRET` differs between the Apps Script and `listener.config.json` |
| the same PDF prints again and again | more than one old listener running (end all `python.exe`/`pythonw.exe`), or an old `listener.py` without the one-copy lock — update it as described above. Then cancel the printer queue and set that order to `PRINTED` in the Sheet |
| order stays `NEW` | listener not running (Task Manager → `pythonw.exe`), or the PC was off — it will catch up on start |
| order becomes `ERROR` | open `listener.log`; usually a wrong printer name or SumatraPDF path |
| nothing prints, no error | printer offline / paused queue in Windows |

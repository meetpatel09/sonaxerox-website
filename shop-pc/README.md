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
5. When it works: make a shortcut to `start-listener-hidden.vbs`, press `Win+R`, type `shell:startup`, drop the shortcut there.

## Updating the listener
Replace `listener.py` with the new version from GitHub. Your `listener.config.json` is untouched, so nothing to re-enter.

## Troubleshooting
| Symptom | Check |
|---|---|
| `CONFIG PROBLEMS` in the log | the message says which setting is wrong |
| `Unauthorized` | `SECRET` differs between the Apps Script and `listener.config.json` |
| order stays `NEW` | listener not running (Task Manager → `pythonw.exe`), or the PC was off — it will catch up on start |
| order becomes `ERROR` | open `listener.log`; usually a wrong printer name or SumatraPDF path |
| nothing prints, no error | printer offline / paused queue in Windows |

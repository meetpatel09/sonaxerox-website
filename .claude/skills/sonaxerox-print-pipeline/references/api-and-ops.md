# Backend API and operations

Base URL: the Apps Script web app `/exec` (stored in `print/index.html` as `BACKEND_URL`; public by design).

| Call | Auth | Result |
|---|---|---|
| `POST` body = order JSON | none (open) | `{ok:true, token}` / `{ok:false, error}` |
| `GET` (no action) | none | `{ok:true, service:'Sona Xerox print backend is running'}` — health check |
| `GET ?action=pending&key=SECRET` | key | `{ok:true, orders:[{row, token, phone, color:'B&W'|'Colour', side:'Single'|'Double', copies, pages, fileId}]}` (status NEW only) |
| `GET ?action=file&id=FILE_ID&key=SECRET` | key | `{ok:true, name, data: base64}` |
| `GET ?action=done&token=S123&key=SECRET` | key | sets `PRINTED` |
| `GET ?action=error&token=S123&key=SECRET` | key | sets `ERROR` |

Script properties used: `FOLDER_ID`, `SHEET_ID` (created automatically on first order). Triggers: `cleanupOldDriveFiles` hourly on Head.

## Shop PC
Folder on a non-C: drive: `listener.py`, `listener.config.json`, `run-listener.bat` (visible, for debugging), `start-listener-hidden.vbs` (invisible; shortcut in `shell:startup`), `stop-listener.bat`, `listener.log` (rotates at 5 MB), `orders/` (PDFs deleted after 24 h). Needs Python 3 and SumatraPDF. No pip packages.

## Testing it without a printer
`tests/test_listener.py` runs the real listener against a fake backend and a fake `SumatraPDF` shell script and checks the printed arguments, status calls, wrong-secret and failure paths.

/**
 * SONA XEROX — PRINT ORDER BACKEND  (v2 — with listener support)
 * ---------------------------------------------------------------
 * REPLACES the previous version. After pasting:
 *   Deploy -> Manage deployments -> (pencil icon) -> Version: New version -> Deploy
 * The URL stays the same.
 *
 * v2 adds secure endpoints for the shop PC "listener":
 *   GET ?action=pending&key=SECRET          -> list of NEW orders
 *   GET ?action=file&id=FILE_ID&key=SECRET  -> the PDF as base64
 *   GET ?action=done&token=S123&key=SECRET  -> mark order PRINTED
 *   GET ?action=error&token=S123&key=SECRET -> mark order ERROR
 *
 * !! CHANGE THE SECRET BELOW — and use the SAME value in listener.py !!
 */

var SECRET = 'CHANGE-ME-sona-valod-2026';   // <<< change this to your own password-like text

var FOLDER_NAME = 'SonaXerox-Orders';
var SPREADSHEET_NAME = 'Sona Xerox Orders';
var SHEET_NAME = 'Orders';
var MAX_PAGES = 30;
var MAX_COPIES = 30;

/* ---------- Customer orders (unchanged) ---------- */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);

    if (!data.fileData) return jsonOut({ ok: false, error: 'No file received' });
    if (!/^[0-9]{10}$/.test(String(data.phone || ''))) {
      return jsonOut({ ok: false, error: 'Invalid phone number' });
    }
    var pages = Number(data.pages) || 0;
    if (pages < 1 || pages > MAX_PAGES) {
      return jsonOut({ ok: false, error: 'Max ' + MAX_PAGES + ' pages per order' });
    }
    var copies = Math.min(Math.max(Number(data.copies) || 1, 1), MAX_COPIES);
    var color = data.color === 'color' ? 'Colour' : 'B&W';
    var side = data.side === 'double' ? 'Double' : 'Single';

    var sheet = getOrdersSheet_();
    var token = 'S' + (100 + sheet.getLastRow());

    var bytes = Utilities.base64Decode(data.fileData);
    var safeName = String(data.fileName || 'order.pdf').replace(/[^\w.\- ]/g, '_');
    var blob = Utilities.newBlob(bytes, 'application/pdf', token + '_' + safeName);
    var file = getOrdersFolder_().createFile(blob);

    sheet.appendRow([
      new Date(), token, "'" + data.phone, color, side,
      copies, pages, file.getUrl(), file.getId(), 'NEW'
    ]);

    return jsonOut({ ok: true, token: token });

  } catch (err) {
    return jsonOut({ ok: false, error: 'Server error: ' + String(err) });
  }
}

/* ---------- Listener endpoints (new in v2) ---------- */

function doGet(e) {
  var p = (e && e.parameter) || {};

  // no action -> simple health check
  if (!p.action) return jsonOut({ ok: true, service: 'Sona Xerox print backend is running' });

  // everything else needs the secret key
  if (p.key !== SECRET) return jsonOut({ ok: false, error: 'Unauthorized' });

  try {
    if (p.action === 'pending') {
      var sheet = getOrdersSheet_();
      var last = sheet.getLastRow();
      var orders = [];
      if (last > 1) {
        var rows = sheet.getRange(2, 1, last - 1, 10).getValues();
        for (var i = 0; i < rows.length; i++) {
          if (rows[i][9] === 'NEW') {
            orders.push({
              row: i + 2,
              token: rows[i][1],
              phone: String(rows[i][2]),
              color: rows[i][3],   // 'B&W' or 'Colour'
              side: rows[i][4],    // 'Single' or 'Double'
              copies: rows[i][5],
              pages: rows[i][6],
              fileId: rows[i][8]
            });
          }
        }
      }
      return jsonOut({ ok: true, orders: orders });
    }

    if (p.action === 'file') {
      var f = DriveApp.getFileById(p.id);
      return jsonOut({
        ok: true,
        name: f.getName(),
        data: Utilities.base64Encode(f.getBlob().getBytes())
      });
    }

    if (p.action === 'done' || p.action === 'error') {
      var status = p.action === 'done' ? 'PRINTED' : 'ERROR';
      var sheet2 = getOrdersSheet_();
      var last2 = sheet2.getLastRow();
      if (last2 > 1) {
        var tokens = sheet2.getRange(2, 2, last2 - 1, 1).getValues();
        for (var j = 0; j < tokens.length; j++) {
          if (tokens[j][0] === p.token) {
            sheet2.getRange(j + 2, 10).setValue(status);
            return jsonOut({ ok: true, token: p.token, status: status });
          }
        }
      }
      return jsonOut({ ok: false, error: 'Token not found' });
    }

    return jsonOut({ ok: false, error: 'Unknown action' });

  } catch (err) {
    return jsonOut({ ok: false, error: 'Server error: ' + String(err) });
  }
}

/* ---------- Helpers ---------- */

function jsonOut(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function getOrdersFolder_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('FOLDER_ID');
  if (id) {
    try { return DriveApp.getFolderById(id); } catch (e) {}
  }
  var it = DriveApp.getFoldersByName(FOLDER_NAME);
  var folder = it.hasNext() ? it.next() : DriveApp.createFolder(FOLDER_NAME);
  props.setProperty('FOLDER_ID', folder.getId());
  return folder;
}

function getOrdersSheet_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('SHEET_ID');
  var ss = null;
  if (id) {
    try { ss = SpreadsheetApp.openById(id); } catch (e) { ss = null; }
  }
  if (!ss) {
    ss = SpreadsheetApp.create(SPREADSHEET_NAME);
    props.setProperty('SHEET_ID', ss.getId());
  }
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.getSheets()[0];
    sheet.setName(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Time', 'Token', 'Phone', 'Colour', 'Sides', 'Copies', 'Pages', 'File URL', 'File ID', 'Status']);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

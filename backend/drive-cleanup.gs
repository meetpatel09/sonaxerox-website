/**
 * SONA XEROX — DRIVE AUTO-CLEANUP (add-on to your existing script)
 * -----------------------------------------------------------------
 * Deletes order PDFs from Google Drive 24 hours after the order,
 * once they are PRINTED (or ERROR). Orders still waiting as NEW
 * are NEVER deleted — so nothing is lost if the shop PC was off.
 *
 * HOW TO ADD (no redeploy needed):
 *   1. Open your project at script.google.com
 *   2. Paste this whole file BELOW your existing code (do not
 *      replace anything — this only ADDS a new function)
 *   3. Save (Ctrl+S)
 *   4. Left sidebar -> Triggers (alarm-clock icon) -> Add Trigger:
 *        - Function to run:        cleanupOldDriveFiles
 *        - Deployment:             Head
 *        - Event source:           Time-driven
 *        - Type of time trigger:   Hour timer
 *        - Interval:               Every hour
 *      -> Save (authorize again if asked)
 *
 * Notes:
 *   - Deleted files go to your Drive bin, and Google permanently
 *     removes them from the bin automatically after 30 days.
 *   - The Sheet keeps the order history (time, token, phone,
 *     settings) — only the PDF itself is removed. The "File URL"
 *     link will stop working after cleanup, which is expected.
 */

var CLEANUP_AFTER_HOURS = 24;

function cleanupOldDriveFiles() {
  var sheet = getOrdersSheet_();
  var last = sheet.getLastRow();
  if (last < 2) return;

  var cutoff = new Date(Date.now() - CLEANUP_AFTER_HOURS * 3600 * 1000);
  var rows = sheet.getRange(2, 1, last - 1, 10).getValues();

  for (var i = 0; i < rows.length; i++) {
    var orderTime = rows[i][0];   // col A: Time
    var fileId = rows[i][8];      // col I: File ID
    var status = String(rows[i][9] || ''); // col J: Status

    var isDone = status === 'PRINTED' || status === 'ERROR';
    var isOld = orderTime instanceof Date && orderTime < cutoff;

    if (isDone && isOld && fileId) {
      try {
        DriveApp.getFileById(fileId).setTrashed(true);
        sheet.getRange(i + 2, 10).setValue(status + ' (file deleted)');
        sheet.getRange(i + 2, 9).setValue('');   // clear File ID
      } catch (e) {
        // file already gone or inaccessible — mark it anyway
        sheet.getRange(i + 2, 10).setValue(status + ' (file deleted)');
        sheet.getRange(i + 2, 9).setValue('');
      }
    }
  }
}

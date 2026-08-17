/**
 * Above & Beyond Fitness — client form receiver.
 *
 * Receives submissions from the branded forms on elliebfit.com and appends each
 * one as a row in a Google Sheet. Each form gets its own tab, and columns are
 * created from the question labels the first time they are seen, so the two
 * questionnaires can have completely different fields without any setup.
 *
 * Deploy: Extensions > Apps Script from the spreadsheet, paste this in, set
 * SHEET_ID below, run testWrite once, then Deploy > New deployment > Web app,
 * "Execute as: Me", "Who has access: Anyone". Steps are in README.md.
 */

// ---------------------------------------------------------------- settings

/** The spreadsheet id — the long part of its URL between /d/ and /edit. */
var SHEET_ID = '15qnDUUHotALcNEq8QhwkVUd2MytJX5NnDbGE269ilK8';

/** Set to '' to turn off the email copy. */
var NOTIFY_EMAIL = 'ellen@elliebfit.com';

/** Only these origins may post. Keeps the endpoint from being used as a
 *  free-for-all writer into the sheet. */
var ALLOWED_ORIGINS = [
  'https://www.elliebfit.com',
  'https://elliebfit.com'
];

// ------------------------------------------------------------------ routes

function doGet() {
  return json({ ok: true, service: 'abf-forms', note: 'POST submissions here.' });
}

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return json({ ok: false, error: 'empty request' });
    }

    var data = JSON.parse(e.postData.contents);

    // Origin is posted by the page: Apps Script does not expose request headers.
    if (ALLOWED_ORIGINS.length && data.origin &&
        ALLOWED_ORIGINS.indexOf(data.origin) === -1) {
      return json({ ok: false, error: 'origin not allowed' });
    }

    // Honeypot: a real person never fills a hidden field.
    if (data.website) {
      return json({ ok: true, skipped: 'spam' });
    }

    var formName = String(data.form || 'Form submission');
    var fields = (Array.isArray(data.fields) ? data.fields : [])
      .filter(function (f) { return f && !f.section; });

    appendRow(formName, fields);

    if (NOTIFY_EMAIL) {
      try {
        MailApp.sendEmail({
          to: NOTIFY_EMAIL,
          subject: formName + ' — ' + firstValue(fields, 'Name'),
          body: plainText(formName, fields)
        });
      } catch (mailErr) {
        // Never fail the submission over a notification; the row is already saved.
      }
    }

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// ----------------------------------------------------------------- helpers

/**
 * Appends one submission to the tab named after the form, widening the header
 * row if the submission carries a question that has not been seen before.
 */
function appendRow(formName, fields) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var tab = tabNameFor(formName);
    var sheet = ss.getSheetByName(tab) || ss.insertSheet(tab);

    var headers = [];
    if (sheet.getLastColumn() > 0) {
      headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    }
    while (headers.length && headers[headers.length - 1] === '') headers.pop();
    if (!headers.length) headers = ['Submitted'];

    for (var i = 0; i < fields.length; i++) {
      var label = String(fields[i].label || '').trim();
      if (label && headers.indexOf(label) === -1) headers.push(label);
    }

    var row = new Array(headers.length).fill('');
    row[0] = Utilities.formatDate(new Date(), 'America/Phoenix', 'yyyy-MM-dd HH:mm:ss');
    for (var j = 0; j < fields.length; j++) {
      var k = headers.indexOf(String(fields[j].label || '').trim());
      if (k > -1) row[k] = String(fields[j].value == null ? '' : fields[j].value);
    }

    sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
    sheet.setFrozenRows(1);
    sheet.appendRow(row);
  } finally {
    lock.releaseLock();
  }
}

/** Sheet tab names cannot exceed 100 chars or contain []*/\? */
function tabNameFor(formName) {
  var name = String(formName).replace(/[\[\]\*\/\\\?:]/g, ' ').trim().slice(0, 90);
  return name || 'Submissions';
}

function plainText(formName, fields) {
  var out = [formName, ''];
  for (var i = 0; i < fields.length; i++) {
    var value = String(fields[i].value == null ? '' : fields[i].value).trim();
    if (value) out.push(fields[i].label + ': ' + value);
  }
  return out.join('\n');
}

function firstValue(fields, label) {
  for (var i = 0; i < fields.length; i++) {
    if (fields[i].label === label && fields[i].value) return String(fields[i].value);
  }
  return 'no name given';
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor to confirm SHEET_ID is reachable before deploying. */
function testWrite() {
  appendRow('Test submission', [
    { label: 'Name', value: 'Test — safe to delete' },
    { label: 'Note', value: 'Written by testWrite in the Apps Script editor.' }
  ]);
  Logger.log('Wrote a test row to the "Test submission" tab. Delete the tab when done.');
}

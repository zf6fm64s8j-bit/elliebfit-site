/**
 * Above & Beyond Fitness — client form receiver.
 *
 * Receives submissions from the branded forms on elliebfit.com and appends each
 * one to a Google Doc. Optionally emails a copy so nothing depends on remembering
 * to open the doc.
 *
 * Deploy: Extensions > Apps Script, paste this in, set the three constants
 * below, then Deploy > New deployment > Web app, "Execute as: Me",
 * "Who has access: Anyone". Copy the /exec URL into the site.
 * Full steps are in README.md next to this file.
 */

// ---------------------------------------------------------------- settings

/** Google Doc that submissions are appended to. Paste the id from the doc URL:
 *  https://docs.google.com/document/d/THIS_PART/edit  */
var DOC_ID = 'PASTE_YOUR_GOOGLE_DOC_ID_HERE';

/** Set to '' to turn off the email copy. */
var NOTIFY_EMAIL = 'ellen@elliebfit.com';

/** Only these origins may post. Keeps the endpoint from being used as a
 *  free-for-all writer into the doc. */
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

    // Origin check. Posted by the page rather than read from a header, because
    // Apps Script does not expose request headers to the script.
    if (ALLOWED_ORIGINS.length && data.origin &&
        ALLOWED_ORIGINS.indexOf(data.origin) === -1) {
      return json({ ok: false, error: 'origin not allowed' });
    }

    // Honeypot: a real person never fills a hidden field.
    if (data.website) {
      return json({ ok: true, skipped: 'spam' });
    }

    var title = String(data.form || 'Form submission');
    var fields = Array.isArray(data.fields) ? data.fields : [];
    var stamp = Utilities.formatDate(new Date(), 'America/Phoenix',
                                     "EEEE d MMMM yyyy 'at' h:mm a");

    appendToDoc(title, stamp, fields);

    if (NOTIFY_EMAIL) {
      try {
        MailApp.sendEmail({
          to: NOTIFY_EMAIL,
          subject: title + ' — ' + firstValue(fields, 'Name'),
          body: plainText(title, stamp, fields)
        });
      } catch (mailErr) {
        // A failed notification must not lose the submission; it is already
        // written to the doc by this point.
      }
    }

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// ----------------------------------------------------------------- helpers

function appendToDoc(title, stamp, fields) {
  var doc = DocumentApp.openById(DOC_ID);
  var body = doc.getBody();

  body.appendParagraph(title).setHeading(DocumentApp.ParagraphHeading.HEADING1);
  body.appendParagraph(stamp).setHeading(DocumentApp.ParagraphHeading.SUBTITLE);

  for (var i = 0; i < fields.length; i++) {
    var label = String(fields[i].label || '').trim();
    var value = String(fields[i].value == null ? '' : fields[i].value).trim();
    if (!value) continue;

    if (fields[i].section) {
      body.appendParagraph(label).setHeading(DocumentApp.ParagraphHeading.HEADING2);
      continue;
    }
    var p = body.appendParagraph('');
    p.appendText(label + ': ').setBold(true);
    p.appendText(value).setBold(false);
  }

  body.appendHorizontalRule();
  doc.saveAndClose();
}

function plainText(title, stamp, fields) {
  var out = [title, stamp, ''];
  for (var i = 0; i < fields.length; i++) {
    var value = String(fields[i].value == null ? '' : fields[i].value).trim();
    if (!value) continue;
    out.push(fields[i].section ? ('\n== ' + fields[i].label + ' ==')
                               : (fields[i].label + ': ' + value));
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

/** Run once from the editor to confirm DOC_ID is reachable before deploying. */
function testWrite() {
  appendToDoc('Test submission', 'run from the Apps Script editor',
              [{ label: 'Name', value: 'Test — safe to delete' }]);
  Logger.log('Wrote a test entry. Open the doc to confirm, then delete it.');
}

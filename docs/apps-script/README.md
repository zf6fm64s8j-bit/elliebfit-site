# Client form receiver — setup

The client forms on the site post to a Google Apps Script web app, which appends
each submission as a row in a Google Sheet and emails a copy. This replaces the
old Google Forms path, which stopped accepting posts from outside Google (every
request returned HTTP 400 and nothing reached the response sheet).

Each form gets its own tab, named after the form. Columns are created from the
question labels the first time they are seen, so the two questionnaires can have
completely different fields with no setup — and adding a question later just adds
a column.

Setup has to be done from Ellen's Google account, since the script runs as her.

## 1. The spreadsheet

Already created:
<https://docs.google.com/spreadsheets/d/15qnDUUHotALcNEq8QhwkVUd2MytJX5NnDbGE269ilK8/edit>

Its id is already filled into `SHEET_ID` in [`Code.gs`](Code.gs). If you ever
switch to a different spreadsheet, copy the long part of its URL between `/d/`
and `/edit` and replace that value.

## 2. The script

1. Open the spreadsheet → **Extensions → Apps Script**.
2. Delete whatever is in the editor.
3. Paste in the entire contents of [`Code.gs`](Code.gs).
4. Save.

> **If you pasted an earlier version of this file:** replace it completely. The
> first version wrote to a Google *Doc* via `DocumentApp`, which throws
> *"Document is missing (perhaps it was deleted, or you don't have read
> access?)"* when the id belongs to a spreadsheet. This version uses
> `SpreadsheetApp` instead.

## 3. Check it can write

1. In the function dropdown pick **`testWrite`**, then **Run**.
2. Approve the authorization prompt the first time. Google will warn that the
   app is unverified — expected for your own script. Choose
   **Advanced → Go to (project name)**.
3. Check the spreadsheet: there should be a new **Test submission** tab with a
   header row and one row. Delete that tab when you're satisfied.

If this fails, fix it here — the deployment will not work either.

## 4. Deploy

1. **Deploy → New deployment**.
2. Gear icon → **Web app**.
3. Set:
   - **Execute as:** Me
   - **Who has access:** Anyone
4. **Deploy**, then copy the **Web app URL**. It ends in `/exec`.

"Anyone" means anyone with the URL can post to it. The script only appends to
this spreadsheet, only accepts posts carrying an approved origin, and drops
anything that trips the hidden honeypot field.

## 5. Put the URL into the site

Paste the `/exec` URL into [`assets/forms.js`](../../assets/forms.js):

```js
var ENDPOINT = 'https://script.google.com/macros/s/AKfy.../exec';
```

Commit and deploy, then submit a test through `/forms/par-q/` and confirm the
row lands.

## Re-deploying after script edits

Editing `Code.gs` does not update the live web app. Use **Deploy → Manage
deployments → edit (pencil) → Version: New version → Deploy**. That keeps the
same `/exec` URL. Creating a *new deployment* instead issues a new URL and would
need the site updated again.

## If a submission ever fails

The page falls back to opening the visitor's email client with the answers
pre-filled, and tells them what happened. A submission is never silently lost.

# Client form receiver — setup

The client forms on the site post to a Google Apps Script web app, which appends
each submission to a Google Doc and emails a copy. This replaces the old Google
Forms path, which stopped accepting posts from outside Google (every request
returned HTTP 400 and nothing reached the response sheet).

Setup takes about five minutes and has to be done from Ellen's Google account,
since it creates a doc and a script that run as her.

## 1. Create the document

1. Go to <https://docs.new> and create a doc. Name it something like
   **Above & Beyond — Client Form Submissions**.
2. Copy its id out of the URL — the long part between `/d/` and `/edit`:

   ```
   https://docs.google.com/document/d/1AbC...XyZ/edit
                                       ^^^^^^^^^^^ this
   ```

## 2. Create the script

1. In that doc: **Extensions → Apps Script**.
2. Delete the placeholder `myFunction` code.
3. Paste in the entire contents of [`Code.gs`](Code.gs).
4. At the top, set `DOC_ID` to the id you copied. Leave `NOTIFY_EMAIL` as is to
   get an email per submission, or set it to `''` to turn that off.
5. Save.

## 3. Check it can write

1. In the editor's function dropdown pick **`testWrite`**, then **Run**.
2. Google will ask for authorization the first time — approve it. It will warn
   that the app is unverified; that is expected for your own script. Choose
   **Advanced → Go to (project name)**.
3. Open the doc. There should be a "Test submission" entry. Delete it.

If this step fails, the deployment will fail too — fix it here first.

## 4. Deploy

1. **Deploy → New deployment**.
2. Gear icon → **Web app**.
3. Set:
   - **Execute as:** Me
   - **Who has access:** Anyone
4. **Deploy**, then copy the **Web app URL**. It ends in `/exec`.

"Anyone" means anyone who knows the URL can post to it. The script only writes
into the doc, only accepts posts carrying an approved origin, and drops anything
that trips the honeypot field.

## 5. Put the URL into the site

Paste the `/exec` URL into `assets/forms.js`:

```js
var ENDPOINT = 'https://script.google.com/macros/s/AKfy.../exec';
```

Commit and deploy. Submit a test through
`/forms/par-q/` and confirm it lands in the doc.

## Re-deploying after script edits

Changing `Code.gs` does not update the live web app on its own. Use
**Deploy → Manage deployments → edit (pencil) → Version: New version → Deploy**.
That keeps the same `/exec` URL. Creating a *new deployment* instead gives a new
URL and would need the site updated again.

## If a submission ever fails

The page falls back to opening the visitor's email client with the answers
pre-filled, so a submission is never silently lost. The visitor is told what
happened and given the address.

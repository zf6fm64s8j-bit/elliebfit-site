# Above & Beyond Fitness — website

Static site for elliebfit.com, hosted on GitHub Pages. No build step: edit, commit, push.

- **Homepage** — `index.html`, a bundled artifact (~180 KB) whose styles, scripts and template are
  inlined. Photos and fonts are **not** inlined: they load from `assets/photos/` and `assets/fonts/`
  so they cache, download in parallel, and lazy-load. It makes no third-party requests.
- **Every other page** — hand-written HTML sharing `assets/site.css` and the self-hosted brand
  fonts in `assets/fonts/`.

> [!IMPORTANT]
> **Do not overwrite `index.html` by re-exporting the design.** That file has been hand-edited since
> the original export — copy changes, the mobile layer, accessibility fixes, the consult-form
> handler and the favicon all live inside it. Treat it as source, not as a build output. If you must
> re-export, diff the two and port changes across deliberately.
>
> When editing the embedded JSON inside it, preserve the `</` escaping. Re-serialising with a
> plain `json.dumps` lets a literal `</script>` in the template close the host `<script>` tag early
> and blanks the page. The helper scripts in `docs/source/` handle this correctly.

## Layout

```
index.html              bundled homepage
assets/                 site.css, forms.js, fonts, photos, apple-touch-icon
forms/                  client forms hub
  client-information/   health history questionnaire
  par-q/                PAR-Q readiness questionnaire
free-class-sign-up/     Friday class sign-up (embeds a Google Form)
recipes/  pwr-moves/    content pages
docs/                   client PDFs, waiver revision log, Apps Script source, brand guide
  source/               PDF + photo generators, photos-src/ originals, counsel review memo
404.html                branded not-found page
<old-slug>/             redirect stubs preserving inbound Google Sites URLs
```

## Forms

| Form | Delivery |
|---|---|
| Consult request (homepage) | Formspree → Ellen's inbox |
| Client Information & Health History | Google Apps Script → Google Sheet, one tab per form |
| PAR-Q | same Apps Script receiver |
| Friday class sign-up | embedded Google Form (unchanged) |

Setup and redeploy instructions for the receiver are in
[`docs/apps-script/README.md`](docs/apps-script/README.md). All forms fall back to opening a
pre-filled email if the request fails, so a submission is never silently lost.

## Homepage photos

The five homepage photos are generated from the originals in `docs/source/photos-src/` — which are
the **only** copies, since they no longer live inside `index.html`. To replace one, drop the new
file into `photos-src/` under the same base name (any of `.jpg/.jpeg/.png/.webp`) and re-run:

```bash
python3 docs/source/optimize-bundle.py
```

That re-encodes every photo to WebP in `assets/photos/`, rewrites the bundle's template and
manifest, and refreshes the hero/font preload hints. It is idempotent.

If the homepage template is re-exported, restore the stable consult-form hooks and dynamic class
time markup after importing the new template:

```bash
python3 docs/source/sync-homepage-runtime.py
python3 docs/source/sync-head-meta.py
```

Both commands are idempotent and fail closed if the generated structure no longer matches the
expected source. The class remains canonical at 10:00 a.m. `America/Phoenix`; `assets/class-time.js`
derives the next Friday's `America/Chicago` time so the displayed abbreviation changes between CST
and CDT without moving the Arizona class time.

## Client PDFs

`docs/liability-waiver.pdf` and `docs/late-cancel-policy.pdf` are generated, not hand-made. Both
require Google Chrome installed.

```bash
python3 docs/source/build-waiver.py        # liability waiver — carries a version + effective date
python3 docs/source/build-client-pdfs.py   # late-cancellation policy
```

The waiver has its own builder because it is versioned: `VERSION` and `EFFECTIVE` in
`build-waiver.py` are stamped onto every page, and every change is recorded in
[`docs/waiver-revisions.md`](docs/waiver-revisions.md). Bump both constants and add a revision entry
when the text changes — never regenerate it silently.

## Deploy

Pages is already configured to serve `main` from the repo root. Push to `main` and it redeploys.

```bash
gh api repos/zf6fm64s8j-bit/elliebfit-site/pages/builds/latest --jq '.status + " " + .commit'
```

Preview locally with `python3 -m http.server 8000`.

## Point elliebfit.com at it — not yet done

`www.elliebfit.com` still serves the old Google Sites site. DNS is managed at **Namecheap**
(nameservers `dns1/dns2.registrar-servers.com`).

The custom domain is currently parked so the `github.io` preview URL stays browsable: the domain
file is `CNAME.golive` rather than `CNAME`. To go live:

1. Restore the domain file and set the custom domain:

   ```bash
   git mv CNAME.golive CNAME
   gh api -X PUT repos/zf6fm64s8j-bit/elliebfit-site/pages \
     -f 'cname=www.elliebfit.com' -f 'source[branch]=main' -f 'source[path]=/'
   ```

2. At Namecheap → Domain List → Manage → **Advanced DNS**, delete the Google Sites records (the
   `www` CNAME to `ghs.googlehosted.com` and the four `@` A records to `216.239.3x.21`), then add:

   | Type | Host | Value |
   |---|---|---|
   | CNAME | `www` | `zf6fm64s8j-bit.github.io.` |
   | A | `@` | `185.199.108.153` |
   | A | `@` | `185.199.109.153` |
   | A | `@` | `185.199.110.153` |
   | A | `@` | `185.199.111.153` |

3. Confirm propagation, then tick **Enforce HTTPS** in Settings → Pages (certificate issuance can
   take up to an hour).

   ```bash
   dig +short www.elliebfit.com; dig +short elliebfit.com A
   ```

4. Unpublish the old Google Site and remove its custom URL, so it cannot be served or indexed.

5. Remove the `zf6fm64s8j-bit.github.io` entry from `ALLOWED_ORIGINS` in
   `docs/apps-script/Code.gs` and redeploy the script (Deploy → Manage deployments → New version,
   which keeps the same URL).

## Branding

The canonical design system is `docs/brand/` — *Desert coral & sage*, the Ascent mark (three
chevrons at 100/62/30 opacity), Barlow Condensed for display and Archivo for text. Tokens are
mirrored in `assets/site.css`; the homepage expresses the same palette in `oklch()`.

## Session handoff

[`HANDOFF.md`](HANDOFF.md) carries current state, outstanding tasks, and a *Do not repeat* list of
approaches already ruled out. Read it before starting work.

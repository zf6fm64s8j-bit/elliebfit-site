# Above & Beyond Fitness — website

Hand-edited static site for elliebfit.com, published through GitHub Pages Actions using an explicit
public-file allowlist. Production and private-review exports share the same source. The reviewed
site was published October 24, 2026; see [the release record](docs/releases/2026-10-24.md).
Validate markup, links, forms, mobile layout, and accessibility before publication; after GitHub
Pages deploys, verify the rendered production URL rather than treating deployment success as visual
readback.

```bash
python3 scripts/validate-site.py
```

GitHub Actions runs this deterministic local validation separately from the Pages deployment.

- **Homepage** — `index.html`, a bundled artifact (~180 KB) whose styles, scripts and template are
  inlined. Photos and fonts are **not** inlined: they load from `assets/photos/` and `assets/fonts/`
  so they cache, download in parallel, and lazy-load. GA4 is the only third-party page-view script;
  the consultation form submits to Formspree.
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

That re-encodes every photo plus responsive below-fold variants to WebP in `assets/photos/`,
rewrites the bundle's template and manifest, and refreshes the hero/font preload hints. It is
idempotent.

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

Pages is configured for **GitHub Actions**, with custom domain `www.elliebfit.com` and HTTPS enforced.
Pushing to main runs validation but does not publish. After review and publication approval, run the
manual workflow on main:

```bash
gh workflow run pages.yml --ref main -f publish=true
```

The workflow's `publish` input defaults to false for artifact-only runs. It builds and validates the
allowlisted output before deployment. Do not restore legacy main-root publishing for normal releases.

Build the production artifact without deploying:

```bash
python3 scripts/build-public-site.py --output /tmp/elliebfit-public-NEW
```

Build the isolated LAN review copy from the same source:

```bash
python3 scripts/build-review-site.py --output /tmp/elliebfit-review-NEW
```

Both outputs must be new directories outside this repository. `site_inventory.py` defines the
public boundary: pages, assets, crawl files, ownership verification and two public PDFs. Workspace
files, editorial notes and source drafts are excluded. Only the review export adds noindex, CSP,
inquiry guards and the review badge. Never publish the review export. Validators accept `--root`
and the production build validates its exact output before writing the success manifest.

```bash
gh run list --workflow pages.yml --limit 3
```

Preview locally with `python3 -m http.server 8000`.

Before committing, run the local SEO and link contract. It validates unique
indexable canonicals against the sitemap, required search/social metadata, one
H1 per indexable page, JSON-LD syntax, and local link targets:

```bash
python3 docs/source/check-seo.py
```

## Historical DNS cutover record

The cutover is complete and `www.elliebfit.com` serves this GitHub Pages repository. DNS is managed
at **Namecheap** (nameservers `dns1/dns2.registrar-servers.com`). The procedure below is retained as
the recovery record; do not repeat it during an ordinary deploy.

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

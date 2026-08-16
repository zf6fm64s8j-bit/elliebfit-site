---
schema: session-handoff/1
updated: 2026-08-16T21:40:00Z
host: claude-code
scope: .
vcs: git
branch: main
head: e225378fc09931aa56ae300038f1ed3bc9b2efe3
worktree:
  staged: 0
  unstaged: 0
  untracked: 0
status: active
verification: pass
next_action: "Wait for counsel's feedback on the waiver draft; when the user is ready to go live, restore CNAME.golive to CNAME and run the DNS cutover."
---

# Handoff — Above & Beyond Fitness website (elliebfit.com)

Static marketing site for a Scottsdale personal-training business, replacing an old Google Sites
site. Deployed to GitHub Pages at
<https://zf6fm64s8j-bit.github.io/elliebfit-site/>. **The custom domain is not cut over yet:**
`www.elliebfit.com` still serves the old Google Sites site.

## State of play

The site is content-complete and deployed to the preview URL. The homepage is a single bundled
artifact (`index.html`, ~1.6 MB, all CSS/JS/fonts/photos inlined, zero external requests at
runtime); every other page is hand-written static HTML sharing `assets/site.css`. All three forms
work end to end and were verified against live endpoints this session. Branding across every page
matches the *Desert coral & sage* brand guide, including the three-chevron Ascent mark, self-hosted
Barlow Condensed + Archivo, and the guide's component rules. An accessibility pass landed: all
coral buttons and links now clear WCAG AA, the homepage has real headings and landmarks, and the
consult form has labels. A rebranded liability waiver and cancellation policy ship as PDFs; a
revised waiver (draft v2) sits unlinked in `docs/draft/` awaiting an Arizona attorney's review.

The remaining work is a go-live sequence (DNS + HTTPS + unpublish Google Sites) plus a short list of
accessibility polish items.

## Next action

Hold for counsel's feedback on the waiver draft. When the user says they are ready to go live,
restore the custom domain and walk the Namecheap DNS change:

```bash
cd ~/AI_projects/elliebfit-site && git mv CNAME.golive CNAME && \
  gh api -X PUT repos/zf6fm64s8j-bit/elliebfit-site/pages \
    -f 'cname=www.elliebfit.com' -f 'source[branch]=main' -f 'source[path]=/'
```

## Verification

All run against the deployed preview this session.

| Check | Command | Result |
|---|---|---|
| Link crawl, all pages | curl each of 54 distinct hrefs | pass — 0 broken; 5 expected 404s are `preconnect` hints and `canonical` URLs on the not-yet-live domain |
| Consult form (Formspree) | live submit in browser | pass — validation + real send |
| PAR-Q form (Apps Script) | live submit in browser | pass — row written, honeypot + required checks hold |
| Client info form (Apps Script) | live submit in browser | pass — 40 fields, partial-date guard fires |
| Apps Script guards | `curl` POST with bad origin / honeypot | pass — `origin not allowed`, `skipped: spam` |
| Contrast (buttons, links) | canvas-resolved ratios in browser | pass — buttons 4.69:1, links 5.31:1 |
| Semantics | DOM query on deployed page | pass — h1×1, h2×9, h3×10; header/nav/main/footer |
| Bundle integrity | JSON parse of all four `__bundler/*` blocks | pass |
| Mobile layout | 375 / 900 / 1280 px viewport probes | pass — 0 horizontal overflow |
| PDF regeneration | `python3 docs/source/build-client-pdfs.py` | pass |
| Automated a11y suite (axe etc.) | — | not run — no tooling installed |
| Cross-browser | — | not run — only Chromium via the browser pane |

## Blockers & risks

- **The bundled `index.html` is hand-edited.** Re-exporting the design from the original tool and
  overwriting it would destroy the copy changes, mobile layer, accessibility fixes, form handler,
  and icons. Treat it as source, not as a build artifact.
- **Editing that file requires preserving `</` escaping.** Re-serialising the embedded JSON
  with plain `json.dumps` lets a literal `</script>` inside the template close the host tag early
  and blanks the whole page. Every helper script in `docs/source/` does this correctly.
- **The Apps Script endpoint URL is public** (it is in `assets/forms.js` in a public repo). Mitigated
  by an origin allow-list and honeypot; it can only append rows to one spreadsheet. Redeploy for a
  fresh URL if abused.
- **`ALLOWED_ORIGINS` in `docs/apps-script/Code.gs` still contains the `zf6fm64s8j-bit.github.io`
  preview origin.** Remove it after cutover.
- **Draft waiver is legally unreviewed.** It carries a draft banner and is deliberately not linked.

## Do not repeat

- **Posting to Google Forms' `/formResponse` endpoint** — rejected: Google now returns HTTP 400 to
  all third-party posts. Every variant was tried (browser headers, cookies, referer, `fbzx`, GET
  form, empty body). Submissions were silently lost for a period because the page showed success
  on an opaque iframe navigation. Replaced by the Apps Script receiver.
- **`DocumentApp` in the Apps Script** — rejected: the target is a Spreadsheet, so it throws
  "Document is missing". Uses `SpreadsheetApp`, one tab per form.
- **Matching bundle card blocks by their shared inline style** — rejected: the step cards carry the
  same style, so a non-greedy match swallowed neighbouring sections and scrambled the DOM. Anchor
  regexes on card *titles* instead.
- **Root-absolute paths (`/assets/...`) on sub-pages** — rejected: correct on the custom domain but
  they resolve to the domain root on the project-pages preview URL, so the stylesheet 404s. All
  sub-pages use relative paths. `404.html` is the deliberate exception (it is served for arbitrary
  paths, so relative links there would resolve against the missing URL).
- **Putting `<link>` tags only in the static `<head>` of `index.html`** — rejected: the bundle
  replaces the whole document on hydration and discards them. Icons live in the template `<helmet>`.
- **The Indigo & Peach "Halo Trail Badge" design guide** — rejected by the user; it is a different
  identity from the one the site follows. The canonical guide is *Desert coral & sage*, mirrored at
  `docs/brand/`.
- **White/cream text on a coral fill** — rejected: 2.92:1, fails AA at any size. Button labels are
  Ink on coral (4.69:1).
- **Trusting a form's success state as proof of delivery** — rejected: a cross-origin iframe
  navigation looks identical whether the server accepted or rejected. Only assert delivery when the
  response body can actually be read.

## Outstanding tasks

| ID | Pri | Status | Task | Done when | Opened |
|----|-----|--------|------|-----------|--------|
| T-20260816-63 | P1 | blocked | Apply counsel's edits to the waiver draft, remove the draft banner, replace the live PDF | Reviewed waiver is linked from `/forms/` | 2026-08-16 |
| T-20260816-yy | P1 | open | DNS cutover: restore `CNAME`, set custom domain, Namecheap records, Enforce HTTPS, unpublish Google Sites | `https://www.elliebfit.com` serves this site over HTTPS | 2026-08-16 |
| T-20260816-o5 | P2 | open | Remove the `github.io` preview origin from `ALLOWED_ORIGINS` and redeploy the Apps Script | Only elliebfit.com origins accepted | 2026-08-16 |
| T-20260816-0z | P2 | open | Label PAR-Q radio groups with `aria-labelledby` so the question is announced with the options | Screen reader reads the question before Yes/No | 2026-08-16 |
| T-20260816-j9 | P3 | open | Add a skip-to-content link and a `prefers-reduced-motion` guard on the smooth scrolls | Both present on every page | 2026-08-16 |
| T-20260816-v5 | P3 | open | Decide whether to restore the 5 testimonials trimmed from the old site, and the dropped bio detail | User has decided either way | 2026-08-16 |

## Open questions

- **Archivo does not embed in the generated PDFs.** Chrome renders it on screen but substitutes a
  system grotesque when printing, so PDF body text is not the brand face (headings are — Barlow
  Condensed embeds fine). Fix is to install Archivo locally so Chrome can embed it. Owner: user.
  Not blocking.
- **Waiver draft is 3 pages** (guide specifies 11pt body; the original was ~9pt on 1 page). Owner:
  user, after counsel's edits.
- **Rates are duplicated** on `/pwr-moves/` and the homepage. Owner: user — link to the rates
  section instead if that duplication is unwanted.

## How to run

No build step. Edit files and push; GitHub Pages redeploys on commit to `main`.

```bash
# preview locally
cd ~/AI_projects/elliebfit-site && python3 -m http.server 8000

# regenerate the client PDFs (needs Google Chrome installed)
python3 docs/source/build-client-pdfs.py

# wait for a deploy to land
gh api repos/zf6fm64s8j-bit/elliebfit-site/pages/builds/latest --jq '.status + " " + .commit'
```

## Environment & preconditions

- **GitHub**: `gh` CLI authenticated as `zf6fm64s8j-bit`. Repo is **public** (required for Pages on
  the free plan).
- **Forms → Google Sheet**: Apps Script web app; script source in `docs/apps-script/Code.gs`, setup
  in the README beside it. Endpoint URL is in `assets/forms.js`. Spreadsheet id is in `Code.gs`.
  One tab per form, columns built from question labels on first sight.
- **Consult form → Formspree**, form id in `assets/forms.js`. Free tier: 50 submissions/month.
- **DNS**: Namecheap (`dns1/dns2.registrar-servers.com`). Apex currently points at Google Sites.
- **PDF generation** requires `/Applications/Google Chrome.app`. `fontTools` is not installed.
- No credentials are stored in this repo. The Apps Script endpoint is a public URL, not a secret.

## Read next

1. `README.md` — deploy and DNS cutover steps, and the warning about overwriting `index.html`.
2. `docs/apps-script/README.md` — how form delivery works and how to redeploy the receiver.
3. `assets/forms.js` — client-side submission, validation, and the email fallback.
4. `docs/brand/Above & Beyond Fitness Brand Guide.dc.html` — the canonical design system.
5. `assets/site.css` — tokens and components for every page except the homepage.
6. `docs/draft/liability-waiver-draft-v2.pdf` — the unreviewed waiver awaiting counsel.
7. `index.html` — the bundled homepage; read the Blockers section above before editing it.

---

### Resuming without the skill

This file follows the [Session Handoff standard](https://github.com/zf6fm64s8j-bit/session-handoff)
and is written to be useful with no tooling installed. To pick up this work:

1. Read **State of play**, then **Next action**.
2. Check whether this handoff is still current — compare `head` in the frontmatter against
   `git rev-parse HEAD`. If they differ, treat every code-state claim as unverified, and run
   `git log --oneline <head>..HEAD` to see what moved.
3. Read **Do not repeat** before proposing an approach.
4. Load the files under **Read next**.
5. When you finish, rewrite this file: update the frontmatter, rewrite State of play, Next action,
   and Verification, and **add to** — never replace — Do not repeat and Outstanding tasks.

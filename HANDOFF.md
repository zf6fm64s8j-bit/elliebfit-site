---
schema: session-handoff/1
updated: 2026-08-17T00:55:00Z
host: claude-code
scope: .
vcs: git
branch: main
head: 47e313934d82365815548e6778b45d470eb98562
worktree:
  staged: 0
  unstaged: 0
  untracked: 0
status: active
verification: pass
next_action: "Wait for the GitHub Pages TLS certificate on www.elliebfit.com, then set https_enforced=true; after that, unpublish the old Google Site and drop the github.io origin from ALLOWED_ORIGINS."
---

# Handoff — Above & Beyond Fitness website (elliebfit.com)

Static marketing site for a Scottsdale personal-training business, replacing an old Google Sites
site. Deployed to GitHub Pages at
<https://www.elliebfit.com>. **The DNS cutover is done** — Namecheap now points at GitHub Pages
and the `github.io` preview URL 301s to the custom domain. Two things remain: the TLS certificate
had not been issued at the end of the session (so `https://` still warns, and Enforce HTTPS is off),
and the old Google Site has not been unpublished yet.

## State of play

The site is content-complete and deployed to the preview URL. Every page except the homepage is
hand-written static HTML sharing `assets/site.css`; the homepage is a bundled artifact
(`index.html`) whose CSS/JS/template are inlined but whose photos and fonts are now real files.
All three forms work end to end and were verified against live endpoints. Branding matches the
*Desert coral & sage* guide throughout, and the accessibility pass (AA contrast, headings,
landmarks, form labels) is in place.

Three things landed this session:

1. **New hero photo.** `hero_dog5.png` replaced the previous grade — the coral tank now agrees with
   the brand coral, and the dog is looking up at Ellen. Source lives in `docs/source/photos-src/`.
2. **Load-time work.** `index.html` went from 1,472 KB to 179 KB (1,063 KB → 90 KB gzipped) by
   externalising the five photos as WebP and the four latin font subsets, and dropping eight
   non-latin subsets the site never uses. First-paint critical path is now ~284 KB against ~1,063 KB
   before, with 163 KB of below-fold photos genuinely deferred. The bundle's main-thread unpack fell
   from 76 ms to 4 ms on desktop. `assets/site.css` also stopped fetching the same variable Archivo
   file four times.
3. **Liability waiver v1.0 published.** The draft banner is gone and `docs/liability-waiver.pdf` is
   the official versioned document, linked from `/forms/`. It applies the drafting review now
   archived at `docs/source/waiver-counsel-review.md`; every change is recorded in
   `docs/waiver-revisions.md`.

4. **Consult form no longer opens a mailto.** The Send button is wired to the bundle's React
   `onClick`, which navigates to `mailto:`; the Formspree handler listened at window capture but
   never stopped the event, so both ran. It now stops the event ahead of every return. The interest
   chips are also reported correctly instead of defaulting to "Not specified".
5. **DNS cutover executed.** `CNAME.golive` became `CNAME`, Pages claims `www.elliebfit.com`, and
   DNS resolves to GitHub on Google/Cloudflare/Quad9. The apex A records redirect to `www`.

The remaining work is HTTPS enforcement once the cert issues, unpublishing Google Sites, removing
the preview origin from the Apps Script, the owner decisions under *Open questions*, plus a short
list of accessibility polish items.

## Next action

Confirm the waiver's open business decisions with Ellen (minors, transportation, fee clause — see
`docs/waiver-revisions.md`). When the user says they are ready to go live, restore the custom
domain and walk the Namecheap DNS change:

```bash
cd ~/AI_projects/elliebfit-site && git mv CNAME.golive CNAME && \
  gh api -X PUT repos/zf6fm64s8j-bit/elliebfit-site/pages \
    -f 'cname=www.elliebfit.com' -f 'source[branch]=main' -f 'source[path]=/'
```

## Verification

The first ten rows were run against the deployed preview in an earlier session; the rows added this
session (from *Homepage after externalising* down) were run against a local `http.server` before
deploying, because the change had to be proven before it went out.

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
| Homepage after externalising | reload, DOM + network probe | pass — 5 photos 200/correct natural size, 4 fonts 200, no bundler error, h1 intact |
| Hero preload | resource timing | pass — hero + 4 fonts start at 20 ms during parse; the 4 below-fold photos deferred to 100 ms |
| Bundle unpack cost | replay of the runtime's atob/Blob loop, 3 runs | pass — 76 ms → 4 ms median (desktop) |
| Sub-pages after font change | fetch + iframe load of 4 pages | pass — 200s, `Archivo 100 900 loaded`, 2 font files instead of 5 |
| Waiver v1.0 | all 4 pages split and rendered | pass — content correct, version footer on every page, no overlap |
| Consult form mailto fix | document-capture probe, before vs after | pass — event reached document before the fix, stops at window capture after; validation still shown |
| Consult form payload | `fetch` stubbed in an iframe, 2 submits | pass — interest `In-home` with no chips touched, `In-home, Virtual` after adding one; nothing sent to Formspree |
| DNS cutover | `dig` against 3 public resolvers + authoritative | pass — `www` → `zf6fm64s8j-bit.github.io`, apex → 4×`185.199.*`, MX for Google Workspace intact |
| Live domain serving | `curl --resolve` to GitHub Pages | pass — HTTP 200, 184 KB, new title, fix present in the served HTML |
| TLS certificate | `gh api .../pages` | **not issued** — still `not requested` >1 h after propagation; Enforce HTTPS off |
| Rendered head metadata | DOM probe on the live page | pass — was 0 title / 2 meta / 0 JSON-LD; now title, `lang=en`, 22 meta, 1 canonical, 3 JSON-LD entities, no duplicates |
| Anchor offset | `scrollIntoView` at 1280 / 375 px | pass — targets land at 88 px / 172 px, clearing the 73 px / 158 px header; no horizontal overflow |
| Target size | measured nav links | pass — 12-13 px → 44 px desktop, 30 px mobile (WCAG 2.2 SC 2.5.8 AA floor is 24 px) |
| Enter-to-submit | synthetic keydown on each field | pass — Enter in name/email runs the send path; textarea keeps Enter for newlines |
| `:focus-visible` ring | cascade inspection | **partial** — rule resolves to `outline: rgb(32,52,46) solid 3px`, but Chrome grants no keyboard modality to a background iframe in a hidden pane, so the ring was never rendered on screen. Confirm with a real Tab press. |
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
- **The published waiver has not been approved by an attorney.** v1.0 applies a drafting review that
  states on its face that it is not legal advice and not a substitute for an Arizona-licensed
  attorney. It was published at the owner's direction. `docs/waiver-revisions.md` records this and
  lists the decisions still open.
- **The photo originals exist only in `docs/source/photos-src/`.** They are no longer inside
  `index.html`. Deleting that directory loses them; it is committed for that reason.
- **`build-waiver.py` owns the waiver; `build-client-pdfs.py` no longer does.** The waiver carries a
  version and effective date and must not be regenerated as a side effect of an unrelated build.

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
- **A `<picture>` element for WebP/JPEG fallback on the homepage photos** — rejected: all five
  `<img>` tags live inside the `<x-dc>` template the DC runtime compiles, and changing their
  structure risks the compiler. WebP alone is Baseline (Safari 14, 2020); plain `<img>` stays.
- **A negative `bottom` on the waiver PDF's running footer** — rejected: Chrome clips `position:
  fixed` content that falls outside the page's content box, so the footer silently disappeared from
  every page. It must sit at `bottom: 0`, with the `@page` bottom margin enlarged to keep flowed
  content clear of it.
- **Leaving anything the page needs at runtime in the static document** — rejected: the runtime ends
  with `document.documentElement.replaceWith()`, which discards the original document wholesale. The
  full SEO head lived there and was gone from the rendered DOM — no `<title>` element at all, 2 meta
  tags, no JSON-LD, no `lang`. Only the template's `<helmet>` survives; `docs/source/sync-head-meta.py`
  mirrors the static head into it. Raw fetches were always fine, which is why this hid for so long.
- **Assuming the homepage inherits `assets/site.css`'s resets** — rejected: it does not load site.css
  at all. `min-height` on a padded element therefore added to the padding and took the header from
  70 px to 97 px. Set `box-sizing` explicitly in any rule added to `abf-responsive`.
- **A bare `required` attribute on the bundle's inputs** — rejected: it does not survive the
  template's React compile, and no `<form>` wraps the fields to enforce it. Use `aria-required`;
  the inline handler already does the validation.
- **Intercepting the bundle's buttons without stopping the event** — rejected: the consult form's
  Send button is wired to the bundle's own React `onClick`, which sets `window.location.href` to a
  `mailto:`. The Formspree handler in the first inline `<script>` listens at *window capture*, which
  runs first but does not by itself prevent React's handler — so both fired and the visitor's mail
  client opened on top of a successful send. Any handler that takes over a bundle control must call
  `e.preventDefault()` **and** `e.stopImmediatePropagation()`, and must do it before every early
  return, not only the success path.
- **Tracking the interest chips from click events alone** — rejected: they are multi-select and the
  build pre-selects "In-home", so a visitor who never touches them produces no click and was
  reported as "Not specified". Read the chips' selected state off the DOM at send time.
- **Timing the bundle's paint in the Browser pane** — rejected as a measurement: the pane reports
  `visibilityState: hidden`, which defers paint and clamps `setInterval` to ~1 s, so FCP/LCP and any
  polling-based A/B are meaningless there. Measure the synchronous unpack cost instead, and read
  layout back from the DOM rather than from screenshots of scrolled content.

## Outstanding tasks

| ID | Pri | Status | Task | Done when | Opened |
|----|-----|--------|------|-----------|--------|
| T-20260816-63 | P1 | done | Apply the review to the waiver, remove the draft banner, replace the live PDF | Waiver v1.0 linked from `/forms/` | 2026-08-16 |
| T-20260816-w1 | P1 | open | Owner decisions on the waiver: accept minors under this form or use a separate minor-participation form; confirm transportation is never provided; keep or drop the fee clause | Each decided, and `build-waiver.py` bumped to v1.1 if the text changes | 2026-08-16 |
| T-20260816-w2 | P2 | open | Version and date the PAR-Q and health questionnaire PDFs the way the waiver now is — § 4 incorporates them by reference | Both carry a version + effective date, retained with the signed waiver | 2026-08-16 |
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
- **The waiver is now 4 pages** (guide specifies 11pt body; the original was ~9pt on 1 page). The
  review's recommendations added length on purpose. Owner: user, if a shorter form is wanted.
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
6. `docs/waiver-revisions.md` — what v1.0 of the waiver changed, why, and what the owner still has
   to decide. `docs/source/waiver-counsel-review.md` is the underlying drafting review.
7. `docs/source/optimize-bundle.py` — how the homepage photos and fonts were moved out of the
   bundle, and how to replace a photo.
8. `index.html` — the bundled homepage; read the Blockers section above before editing it.

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

---
schema: project-plan/2
updated: 2026-10-24T13:59:28Z
scope: .
vcs: git
branch: main
head: 2fd7bbd3bb4428409f99770c8c4b788fb7fbb002
phase: release
status: active
rigor: light
decision_log: docs/adr/
handoff: HANDOFF.md
---

# Plan — Clear, credible personal training and search discovery
## Outcome

Help prospective clients and search assistants accurately understand Ellen's independent service,
its ideal-client fit, practical costs and experience. Prepare changes for private review first.
**Success:** Source-faithful articles and service pages, consistent raw/rendered/schema facts,
a working local preview, adjudicated review, and a recorded discovery baseline when access permits.
## Scope
**In scope:** Existing article drafts; homepage and service-page improvements from the
[local audit](docs/source/llm-discovery-audit-2026-10-23.md); discreet biography wording;
private preview; follow-up checks of existing search/business accounts and measurement.
**Out of scope:** External-account/listing changes beyond the approved Pages cutover,
new rates/services, medical promises, invented client details, outreach, account/listing mutations,
competitor links/logos, new article concepts not selected, or a site redesign.

## Constraints
Keep Above & Beyond Fitness primary; no affiliation links, sameAs additions or employer logos.
The J is current; Fit Family work is valid background, not a claim of current employment.
Use published quotes and actual service facts; no inferred client age, location or diagnosis.
Preserve booking/privacy/analytics behavior in source; isolate preview from external submissions.
No home address or venue coordinates; no AI-placement or search-volume promises.
Publication authorized October 24: switch Pages to Actions before pushing; publish only the public artifact.

## Approach

### Article series — completed; private publication decision remains separate

- [x] Revise older adults, joint replacement, couples/golf and Parkinson's articles and hub.
- [x] Verify quote fidelity, 24 visible/schema FAQ pairs, draft markers and intended route links.
- [x] Run/adjudicate cross-provider councils; record [article evidence](docs/source/articles/REVIEW.md).
- [x] Update five Lula pages for Ellen's review; retain originals and served-byte verification.
- [x] Record [brainstorm concepts](docs/source/articles/SEO-IDEAS.md); do not silently implement them.

### Existing-site improvements — local candidate

- [x] Name older adults, returning exercisers and couples in visible homepage/in-home copy.
- [x] Mirror audience facts in raw fallback, metadata and relevant schema without keyword stuffing.
- [x] Show couples per-person/combined prices and package rules; add faithful couples/virtual proof.
- [x] Link PWR service from relevant formats; unify its ID/provider and homepage offer entry.
- [x] Remove undocumented sports-venue type and precise coordinates; retain truthful service area.
- [x] Add brief biography-only professional background; no affiliation links/logos/endorsement.
- [x] Clarify coaching since 2010 vs Arizona business since 2023; retain route-availability caveat.
- [x] Remove raw loader's technical jargon while retaining its runtime status node.
- [x] Verify source, regeneration idempotence and rendered desktop/narrow layouts.
- [x] Build local review preview with external submissions/tracking blocked; document how to run.
- [x] Run cross-provider review; adjudicate findings and record [candidate evidence](site-review.md).

### Navigation and launch readiness

- [x] Audit source/runtime links, fragments, redirects, canonical routes and draft hub reachability.
- [x] Add direct homepage About/Testimonials links and refresh significant-update sitemap dates.
- [x] Deploy allowlisted LAN copy; quarantine old source files and verify served crawl files/404s.
- [x] Adjudicate independent review and record launch blockers in navigation-review.md.
- [x] Prepare final guide routes, reciprocal links, 16-URL crawl files and email class signup.
- [x] Build/verify separate public and review artifacts; prepare manual publishing workflow.
- [x] Apply Ellen’s bio, badge and three-area service corrections; verify visible/metadata parity.

### Discovery baseline — account evidence still required

- [ ] Inspect existing Search Console/Bing properties, ownership, sitemap and URL indexing.
- [ ] Confirm Ellen's directory/profile activation and exact URL before adding a profile link.
- [ ] Inspect existing Google Business Profile: name, category, website, services, service area.
- [ ] Inspect available analytics and record query/page/consultation baseline without health text.
- [ ] Agree a small fixed buyer-question panel; record assistant, date, context, citations, accuracy.
- [ ] After an approved release, compare observations; distinguish correlation from causation.

## Verification
Run `./scripts/verify.sh` (same HTML/SEO checks as CI); separately validate raw/rendered/schema
facts, preserved quotes, PWR references, prices, no affiliation links and regenerated-head parity.
Run homepage generators twice and compare hashes. Inspect local desktop/narrow pages; do not submit
real forms. Account rows require actual console evidence; public crawl checks do not complete them.

LAN review: <http://10.0.1.5:8080/>. Current evidence: [cutover-review.md](cutover-review.md).

## Publication checklist
Owner/Ellen approve the candidate; obtain explicit publication instruction. Execute the precise
sequence in [cutover-review.md](cutover-review.md): switch legacy Pages source BEFORE pushing,
exclude editorial records, publish only the public artifact, verify live URLs and delivery, retain rollback.
No implementation checkbox authorizes public publication.

## Open questions

Search/account access and baseline are not yet verified. Candidate content and release approval remain pending; no external-account changes are authorized.

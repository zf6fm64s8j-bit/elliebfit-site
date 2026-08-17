# Liability waiver — revision history

The published waiver is `docs/liability-waiver.pdf`, built by
`docs/source/build-waiver.py`. `VERSION` and `EFFECTIVE` in that script are the
single source of truth; both are stamped in the running footer of every page and
beside the signature block, so a signed copy identifies on its face which text
the client agreed to.

**To issue a revision:** bump `VERSION` and `EFFECTIVE`, add an entry at the top
of the table below, re-run the builder, and keep the superseded PDF — signed
copies on file reference it by version number.

| Version | Effective | Summary |
|---|---|---|
| 1.1 | August 17, 2026 | Expanded the minors section now that the business is keeping the advertised ages 8-92 range. |
| 1.0 | August 16, 2026 | First published version. Supersedes the unpublished drafts v1 and v2. |

Superseded PDFs are kept in `docs/archive/`.

---

## v1.1 - August 17, 2026

The owner decided to keep advertising training for ages 8-92, so Section 12 had
to do more than v1.0's bare consent. It was rewritten into six labelled
subsections, and Section 1 now states the age range so the document's scope
matches the marketing copy.

### What changed from v1.0

**Section 1.** States that Above & Beyond accepts clients aged 8 and older, and
that Section 12 also applies and must be signed for anyone under 18.

**Section 12(a) consent and authority.** Unchanged in substance from v1.0.

**Section 12(b) the parent has read the agreement.** New. The parent confirms
they read Sections 1-11, had a chance to ask questions, and understand and
accept the Section 3 risks - including serious injury and death - in deciding to
enroll the minor. This is about proving informed consent, which is the part a
court will actually look at.

**Section 12(c) the parent's own claims are released.** New, and the most
valuable addition. A parent has their *own* claims arising from a child's
injury - most importantly for the child's medical expenses, and for loss of the
child's services or companionship. Those belong to the parent, so the parent can
release them, and this release is on the same ordinary-negligence-only footing
with the same Section 2 exclusions. v1.0 gestured at this in one clause; it is
now explicit about which claims it covers.

**Section 12(d) health, supervision, and safety.** New. Accurate health and
emergency-contact information, prompt updates, compliance with Sections 4, 6 and
7, and a requirement that the parent stay at the session or be immediately
reachable by phone throughout. Above & Beyond may require attendance or medical
clearance where safety warrants.

**Section 12(e) emergency care.** New. Authorizes Above & Beyond to summon
emergency medical services and pass responders the health information on file
when the parent cannot be reached, with the parent responsible for the cost.
Without this, a trainer faces an avoidable hesitation in the one moment that
matters.

**Section 12(f) what this section does not do.** Retained from v1.0, deliberately.
Nothing purports to waive the minor's own claims, and the parent is not asked to
indemnify Above & Beyond for its own negligence.

**Spelling.** "enrol"/"authorises" corrected to US spelling; "Acknowledgement"
to "Acknowledgment".

### What this does and does not achieve

Worth being blunt, because the section reads more protective than it is.

**What it does:** documents informed parental consent; releases the parent's own
derivative claims, which are real and often the larger medical-expense exposure;
creates enforceable operational duties around health disclosure and supervision;
and authorizes emergency care.

**What it cannot do:** it does not eliminate the minor's own claim. Arizona has
no clear rule permitting a parent to waive a child's future ordinary-negligence
claim in a commercial agreement, and A.R.S. Section 12-553's equine carve-out
implies the absence of a general one. A minor's limitations period is generally
tolled until 18, so a claim can surface years later. **Insurance, not drafting,
is the mitigation for that exposure** - confirm the policy covers training
minors, and confirm the age floor it will write to.

Section 12(f) is not a weakness. Overreaching - a purported waiver of the minor's
claim, or a parent indemnity for Above & Beyond's own negligence - risks being
read as an indirect release and can undermine the parts that would otherwise
hold.

---

## v1.0 — August 16, 2026

First version put into use. Applies the drafting review in
`docs/source/waiver-counsel-review.md` to the unpublished draft v2.

### What changed from draft v2

**Release and assumption of risk (§§ 2–3).** The release is now tied to claims
"arising out of or related to Client's participation in the Services" and limited
to what an ordinary-negligence claim actually covers, rather than the previous
open-ended "any and all claims … however caused". Arizona construes releases
strictly against the party relying on them, so narrower, concrete language is
more likely to hold than broad language. "Any and all risks" became "known and
inherent risks … some risks may remain even when reasonable care is used". The
exclusions now name fraud and willful/wanton misconduct alongside gross
negligence, recklessness, and intentional misconduct. The release reaches only
"claims Client owns or has legal authority to release" instead of purporting to
bind heirs and personal representatives.

**Health disclosure (§ 4).** The old text had the client represent they knew of
no condition preventing safe participation. A client with Parkinson's — a core
part of this practice — cannot truthfully sign that. It is now a disclosure
obligation: the client represents they have disclosed known conditions,
medications, injuries, surgeries, symptoms, and where relevant pregnancy or
postpartum status. The section states plainly that the form is not medical
clearance, and that Above & Beyond may require clearance, modify a session, or
decline participation for safety.

**Operational duties (§§ 1, 6–7).** Added the obligations that actually reduce
risk rather than only allocating it: an emergency contact kept current; stating
the client's physical location at the start of every virtual session; a charged
phone within reach; and the option to require another adult present or medical
clearance for higher-risk clients. § 1 now states that transportation of clients
is not part of the Services.

**Indemnity (§ 8).** Narrowed to third-party claims "to the extent caused by" the
client's own negligence or breach, with notice, defense-control, and
mutual-consent-to-settle terms. It says explicitly that it does not require the
client to indemnify Above & Beyond for Above & Beyond's own negligence.

**Attorneys' fees (§ 9).** Split into its own section and limited to a contested
action brought solely to enforce an express contractual obligation. A.R.S.
§ 12-341.01 covers actions arising out of contract, and Arizona courts have held
that a personal-injury action does not become a contract action merely because
the defendant relies on a waiver. The section now says so.

**Governing law (§ 10).** Venue carries an exception where applicable law
requires another forum. The old "reformed to the maximum extent enforceable"
became limitation-then-severance. Added that the waiver does not supersede the
separate payment, scheduling, cancellation, refund, or privacy terms — the
cancellation policy is a separate document.

**Acknowledgement (§ 11).** Adds that the client received a copy before
participating, had a reasonable opportunity to ask questions, understands the
scope, and understands there is no guarantee of any particular fitness, health,
weight, or Parkinson's-related outcome. Dropped "freely and voluntarily", which
carries little weight for a form that is a condition of training.

**Minors (§ 12).** The most substantive change. Draft v2 had the parent agree to
everything on the minor's behalf and indemnify Above & Beyond for any claim
brought by or on behalf of the minor. Arizona has no clear general rule
authorising a parent to waive a minor's future ordinary-negligence claim in a
commercial agreement, and the parent indemnity could be characterised as an
indirect release. § 12 is now consent and accurate-information only: the parent
releases their own claims, nothing purports to waive the minor's substantive
claim, and the parent is not required to indemnify Above & Beyond for its own
negligence. A new agreement is required when the minor turns 18.

**Photo/video consent.** Withdrawal is prospective; Above & Beyond will make
reasonable efforts on its own website and accounts but cannot control third-party
reposts. Consent for a client under 18 moves to a separate parent/guardian form.

**Arbitration.** Deliberately not added. It is a business decision with real
cost — under AAA or JAMS consumer rules the business carries most of the
administrator and arbitrator fees — and it does not cure waiver-language or
minor-authority issues.

**Draft banner.** Removed, and the version/effective-date stamp added in its
place.

### Open decisions for the business owner

These are choices about how the business runs, not drafting problems:

1. **Minors.** Decided: clients from age 8 are accepted, and v1.1 expands
   Section 12 accordingly. Still worth confirming that the insurance policy
   covers training minors and what age floor it will write to.
2. **Transportation.** § 1 states that Above & Beyond does not drive clients.
   If that is ever not true, the sentence must come out and the activity needs
   its own insurance review.
3. **Attorneys' fees.** § 9 is retained but narrow. It could be dropped entirely
   with little practical loss.
4. **Insurance.** Confirm coverage for in-home, outdoor, virtual, contractor,
   minor, and Parkinson's-related exposures.
5. **Attached documents.** The PAR-Q and health questionnaire are incorporated by
   reference in § 4 and should be versioned and retained with each signed waiver.

### Status

This version applies a drafting review that is expressly **not legal advice and
not a substitute for review by an Arizona-licensed attorney** — see the
disclaimer at the top of `docs/source/waiver-counsel-review.md`. It has not been
approved by counsel. Published at the business owner's direction.

# Ellie B Fit Site — Repository Instructions

## 1. Scope & Ownership

This repository contains the static marketing website for Ellie B Fit personal training, deployed directly via GitHub Pages. The driving AI assistant (**Codex**, **Antigravity**, or **Claude Code**) owns implementation, local deterministic verification, and delivery.
Operational posture: **Tier 1 (Light Rigor)** per [ADR 0004](../../docs/adr/0004-lightweight-ergonomics-and-ceremony-reduction-for-personal-projects.md).

## 2. Verification & Delivery

- **Local Check:** Run `./scripts/verify.sh` before committing (validates HTML integrity and all pages via `scripts/validate-site.py`).
- **Solo Delivery:** Direct commits to `main` are authorized once `./scripts/verify.sh` passes and `git status` is clean (Scope → Change → Check).
- **Live Site Readback:** Treat a successful GitHub Pages build separately from rendered browser verification.

## 3. Boundaries & Safety Rules

- Preserve hand-edited HTML structure; never overwrite pages with automated tool exports.
- Keep private client training inquiries, leads, and Formspree secrets outside Git.
- Preserve existing redirect rules, analytics consent boundaries, and embedded JSON-LD schemas.

## 4. Second Opinions (`ask-peer`) & Scaling

- **Routine work:** Do not invoke peers for text copy edits, minor CSS tweaks, or image path adjustments.
- **Two-Failure Rule:** If `./scripts/verify.sh` fails twice consecutively, run `ask-peer --fast "<failing error>"`.
- **Domain Traps:** Query `ask-peer` before finalizing changes to:
  - Mobile viewport layout shifts and responsive CSS grid/flex bugs.
  - WCAG accessibility standards (contrast ratios, aria landmarks, tap targets).
  - Client-side form validation and anti-spam submission handling.

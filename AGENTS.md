# Ellie B Fit Site — agent notes

The workspace rules in `~/AI_projects/AGENTS.md` load automatically and cover workflow, council tools,
and safety. This file holds only what is specific to this repository.

- **Purpose:** static marketing site for Ellie B Fit personal training.
- **Stack:** static HTML/CSS/JS; Python >= 3.10 for the site validator.
- **Verify:** `./scripts/verify.sh` (HTML integrity of every page via `scripts/validate-site.py`).
- **Consequence level:** deploys to GitHub Pages from `main`. A green Pages build is not a rendered-browser
  check; report the two separately.

## Domain traps

Ask for a second opinion (`ask-peer`) before changing:

- mobile viewport layout shifts and responsive grid/flex behaviour;
- WCAG accessibility (contrast, ARIA landmarks, tap targets);
- client-side form validation and anti-spam submission handling.

## Repository rules

- Pages are hand-edited HTML; never overwrite them with tool exports.
- Keep client inquiries, leads, and Formspree secrets outside Git.
- Preserve redirect rules, analytics consent boundaries, and embedded JSON-LD.

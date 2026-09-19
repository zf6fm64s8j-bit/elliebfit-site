#!/usr/bin/env bash
# Fast, deterministic local verification for elliebfit-site
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "== Validating site structure and HTML pages =="
python3 scripts/validate-site.py

echo "== Checking git diff formatting =="
git diff --check

echo "== Verification passed =="

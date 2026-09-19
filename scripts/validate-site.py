#!/usr/bin/env python3
"""Validate repository-local HTML links, assets, and duplicate element IDs."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "sms", "data", "javascript"}


def load_allowlist():
    allowlist = set()
    source = ROOT / ".site-validation-allowlist"
    if not source.exists():
        return allowlist
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        page, reference, _reason = line.split("\t", 2)
        allowlist.add((page, reference))
    return allowlist


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        for attribute in ("href", "src", "poster"):
            if values.get(attribute):
                self.references.append(values[attribute])


def reference_target(page, reference):
    parsed = urlsplit(reference)
    if parsed.scheme.lower() in SKIP_SCHEMES or reference.startswith(("//", "#")):
        return None
    relative = Path(unquote(parsed.path))
    target = ROOT / str(relative).lstrip("/") if parsed.path.startswith("/") else page.parent / relative
    if not parsed.path:
        target = page
    if target.is_dir():
        target = target / "index.html"
    return target.resolve()


def main():
    failures = []
    allowlist = load_allowlist()
    pages = sorted(ROOT.rglob("*.html"))
    if not pages:
        failures.append("no HTML pages found")
    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicates:
            failures.append(f"{page.relative_to(ROOT)}: duplicate ids: {', '.join(duplicates)}")
        for reference in parser.references:
            if (page.relative_to(ROOT).as_posix(), reference) in allowlist:
                continue
            target = reference_target(page, reference)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                failures.append(f"{page.relative_to(ROOT)}: escapes repository: {reference}")
                continue
            if not target.exists():
                failures.append(f"{page.relative_to(ROOT)}: missing target: {reference}")
    if failures:
        print("Site validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Site validation passed: {len(pages)} HTML pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

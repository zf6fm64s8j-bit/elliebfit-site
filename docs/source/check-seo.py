#!/usr/bin/env python3
"""Fail closed on the static site's crawlability and metadata contract.

The homepage has a generated runtime and the rest of the site is hand-written,
so a build system cannot protect SEO invariants for us. This check keeps the
sitemap, canonical URLs, index directives, social cards, headings, JSON-LD,
and internal links synchronized without requiring third-party packages.
"""
from html.parser import HTMLParser
import json
import os
import sys
from urllib.parse import unquote, urljoin, urlparse
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ORIGIN = 'https://www.elliebfit.com/'
SKIP_DIRS = {'.git', 'node_modules'}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.in_title = False
        self.h1_count = 0
        self.meta = []
        self.links = []
        self.canonicals = []
        self.json_ld = []
        self.in_json_ld = False
        self.json_parts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'title':
            self.in_title = True
        elif tag == 'h1':
            self.h1_count += 1
        elif tag == 'meta':
            self.meta.append(values)
        elif tag == 'a' and values.get('href'):
            self.links.append(values['href'])
        elif tag == 'link' and 'canonical' in values.get('rel', '').split():
            self.canonicals.append(values.get('href', ''))
        elif tag == 'script' and values.get('type') == 'application/ld+json':
            self.in_json_ld = True
            self.json_parts = []

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag == 'script' and self.in_json_ld:
            self.json_ld.append(''.join(self.json_parts))
            self.in_json_ld = False
            self.json_parts = []

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.json_parts.append(data)


def parse_page(path):
    parser = PageParser()
    with open(path, encoding='utf-8') as source:
        parser.feed(source.read())
    return parser


def meta_content(page, key, value):
    return [tag.get('content', '') for tag in page.meta if tag.get(key) == value]


def local_path_for(url):
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != 'www.elliebfit.com':
        return None
    path = unquote(parsed.path)
    if path == '/':
        return os.path.join(ROOT, 'index.html')
    candidate = os.path.join(ROOT, path.lstrip('/'))
    if path.endswith('/'):
        candidate = os.path.join(candidate, 'index.html')
    return candidate


def main():
    failures = []
    pages = {}
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        if 'index.html' not in files:
            continue
        path = os.path.join(base, 'index.html')
        rel = os.path.relpath(path, ROOT)
        page = parse_page(path)
        pages[rel] = page

        robots = ' '.join(meta_content(page, 'name', 'robots')).lower()
        indexable = 'noindex' not in robots
        if not indexable:
            continue

        title = ''.join(page.title_parts).strip()
        if not title:
            failures.append(f'{rel}: missing title')
        if len(page.canonicals) != 1 or not page.canonicals[0].startswith(ORIGIN):
            failures.append(f'{rel}: expected one canonical URL on {ORIGIN}')
        if len(meta_content(page, 'name', 'description')) != 1:
            failures.append(f'{rel}: expected one meta description')
        if page.h1_count != 1:
            failures.append(f'{rel}: expected one H1, found {page.h1_count}')
        for prop in ('og:title', 'og:description', 'og:url', 'og:image'):
            if len(meta_content(page, 'property', prop)) != 1:
                failures.append(f'{rel}: expected one {prop}')
        for name in ('twitter:card', 'twitter:title', 'twitter:description', 'twitter:image'):
            if len(meta_content(page, 'name', name)) != 1:
                failures.append(f'{rel}: expected one {name}')
        for number, block in enumerate(page.json_ld, 1):
            try:
                json.loads(block)
            except json.JSONDecodeError as error:
                failures.append(f'{rel}: JSON-LD block {number} is invalid: {error}')

    sitemap = ET.parse(os.path.join(ROOT, 'sitemap.xml'))
    namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap_urls = [node.text for node in sitemap.findall('sm:url/sm:loc', namespace)]
    if len(sitemap_urls) != len(set(sitemap_urls)):
        failures.append('sitemap.xml: duplicate URLs')

    indexable_canonicals = {
        page.canonicals[0]
        for page in pages.values()
        if page.canonicals and 'noindex' not in ' '.join(meta_content(page, 'name', 'robots')).lower()
    }
    indexable_titles = [
        ''.join(page.title_parts).strip()
        for page in pages.values()
        if page.canonicals and 'noindex' not in ' '.join(meta_content(page, 'name', 'robots')).lower()
    ]
    if len(indexable_titles) != len(set(indexable_titles)):
        failures.append('indexable pages: duplicate titles')
    if set(sitemap_urls) != indexable_canonicals:
        missing = sorted(indexable_canonicals - set(sitemap_urls))
        extra = sorted(set(sitemap_urls) - indexable_canonicals)
        if missing:
            failures.append('sitemap.xml: missing ' + ', '.join(missing))
        if extra:
            failures.append('sitemap.xml: contains non-indexable or unknown ' + ', '.join(extra))

    for rel, page in pages.items():
        page_url = ORIGIN if rel == 'index.html' else urljoin(ORIGIN, rel[:-len('index.html')])
        for href in page.links:
            if href.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:')):
                continue
            target_url = urljoin(page_url, href)
            target = local_path_for(target_url)
            if target is not None and not os.path.exists(target):
                failures.append(f'{rel}: broken internal link {href}')

    if failures:
        print('\n'.join(f'FAIL {failure}' for failure in failures))
        return 1
    print(f'PASS {len(pages)} HTML pages; {len(indexable_canonicals)} indexable canonicals; '
          f'{len(sitemap_urls)} sitemap URLs')
    return 0


if __name__ == '__main__':
    sys.exit(main())

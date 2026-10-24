#!/usr/bin/env python3
"""Audit source + bundled homepage navigation; optionally check the served LAN review."""
import argparse
from collections import deque
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
from site_inventory import public_files, ARTICLE_ROUTES

ORIGIN = 'https://www.elliebfit.com'


class Page(HTMLParser):
    def __init__(self, source, include_runtime=True):
        super().__init__(convert_charrefs=True)
        self.ids, self.anchors, self.resources = set(), [], []
        self.canonicals, self.robots, self.redirects = [], [], []
        self.feed(source)
        manifest = re.search(r'<script type="__bundler/manifest">(.*?)</script>', source, re.S)
        bundled = set(json.loads(manifest[1])) if manifest else set()
        match = re.search(r'<script type="__bundler/template">(.*?)</script>', source, re.S)
        if match and include_runtime:
            self.feed(json.loads(match[1]))
        self.resources = [ref for ref in self.resources if ref not in bundled]
        self.canonicals = list(dict.fromkeys(self.canonicals))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href'):
            self.anchors.append(a['href'])
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href', ''))
        elif tag == 'link' and a.get('href'):
            self.resources.append(a['href'])
        for key in ('src', 'poster'):
            if a.get(key):
                self.resources.append(a[key])
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.robots.append(a.get('content', '').lower())
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.redirects.append(a.get('content', '').split('url=')[-1])


def inventory():
    files = sorted(rel for rel in public_files(ROOT) if rel.endswith('.html'))
    pages = {}
    for rel in files:
        if rel.startswith('docs/') or rel.startswith('google'):
            continue
        route = '/' if rel == 'index.html' else '/' + rel.removesuffix('index.html')
        pages[route] = (ROOT / rel, Page((ROOT / rel).read_text()))
    return pages


def main():
    global ROOT
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--base-url', help='Private LAN deployment to verify; no external links fetched')
    cli.add_argument('--json', type=Path, help='Write complete evidence outside the public web root')
    cli.add_argument('--root', type=Path, default=ROOT, help='Launch candidate directory')
    args = cli.parse_args()
    ROOT = args.root.resolve()
    pages = inventory()
    exported = public_files(ROOT)
    failures, external, resources = [], set(), set()
    graph = {route: set() for route in pages}
    for route, (_, page) in pages.items():
        for ref in page.anchors + page.resources + page.redirects:
            parsed = urlsplit(urljoin(ORIGIN + route, ref))
            if parsed.scheme not in ('http', 'https'):
                continue
            if parsed.netloc != urlsplit(ORIGIN).netloc:
                external.add(parsed.geturl())
                continue
            target = unquote(parsed.path)
            if target in pages:
                if ref in page.anchors + page.redirects:
                    graph[route].add(target)
                if parsed.fragment and unquote(parsed.fragment) not in pages[target][1].ids:
                    failures.append(f'{route}: missing fragment {ref}')
            elif target.lstrip('/') in exported and (ROOT / target.lstrip('/')).is_file():
                resources.add(target)
            else:
                failures.append(f'{route}: missing destination {ref}')
    # Manifest icons are dependencies even though HTML does not link them directly.
    manifest = json.loads((ROOT / 'site.webmanifest').read_text())
    for entry in manifest['icons']:
        target = urlsplit(urljoin(ORIGIN + '/', entry['src'])).path
        resources.add(target)
        if target.lstrip('/') not in exported or not (ROOT / target.lstrip('/')).is_file():
            failures.append(f'manifest: missing icon {target}')
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    sitemap_urls = [n.text for n in sitemap.findall('.//{*}loc')]
    launch = {route for route, (path, p) in pages.items()
              if not path.name.endswith('.draft') and 'noindex' not in ' '.join(p.robots)
              and not p.redirects and route != '/404.html'}
    if {ORIGIN + route for route in launch} != set(sitemap_urls):
        failures.append('sitemap: does not exactly match indexable canonical launch routes')
    visited, queue = set(), deque(['/'])
    while queue:
        route = queue.popleft()
        if route in visited:
            continue
        visited.add(route)
        queue.extend(graph.get(route, set()) - visited)
    if launch - visited:
        failures.append('unreachable launch pages: ' + ', '.join(sorted(launch - visited)))
    drafts = {route for route, (path, _) in pages.items() if path.name.endswith('.draft')}
    hub_seen, queue = set(), deque(['/articles/'])
    while queue:
        route = queue.popleft()
        if route in hub_seen:
            continue
        hub_seen.add(route)
        queue.extend(graph.get(route, set()) - hub_seen)
    if drafts - hub_seen:
        failures.append('draft pages unreachable from article hub')
    for route, (_, p) in pages.items():
        if route in launch | drafts and p.canonicals != [ORIGIN + route]:
            failures.append(f'{route}: canonical mismatch {p.canonicals}')
    http = []
    if args.base_url:
        base = args.base_url.rstrip('/')
        for target in sorted(set(pages) | resources | {'/robots.txt', '/sitemap.xml', '/llms.txt'}):
            try:
                with urlopen(base + target, timeout=15) as response:
                    data = response.read()
                    http.append({'path': target, 'status': response.status, 'type': response.headers.get('Content-Type')})
            except (HTTPError, URLError, TimeoutError) as error:
                status = getattr(error, 'code', None)
                http.append({'path': target, 'status': status, 'error': str(error)})
                failures.append(f'{target}: HTTP fetch failed: {error}')
                continue
            if target in pages:
                raw = data.decode()
                documents = [('raw', raw)]
                match = re.search(r'<script type="__bundler/template">(.*?)</script>', raw, re.S)
                if match:
                    documents.append(('runtime', json.loads(match[1])))
                for kind, document in documents:
                    served = Page(document, include_runtime=False)
                    if 'noindex' not in ' '.join(served.robots):
                        failures.append(f'{target}: staging {kind} noindex missing')
            elif target in ('/robots.txt', '/sitemap.xml', '/llms.txt'):
                if data != (ROOT / target.lstrip('/')).read_bytes():
                    failures.append(f'{target}: served crawl file differs from launch candidate')
        for target in ['/does-not-exist-navigation-audit/', '/AGENTS.md', '/HANDOFF.md',
                       '/docs/source/check-seo.py', '/.gitignore', '/scripts/verify.sh',
                       '/.git/HEAD', '/.git/config', '/.env', '/README.md',
                       '/docs/source/articles/articles.html.draft', '/docs/waiver-revisions.md']:
            try:
                with urlopen(base + target, timeout=15) as response:
                    failures.append(f'{target}: unintended 200 response')
            except HTTPError as error:
                if error.code not in (403, 404):
                    failures.append(f'{target}: unexpected status {error.code}')
                http.append({'path': target, 'status': error.code})
            except (URLError, TimeoutError) as error:
                failures.append(f'{target}: exposure check failed: {error}')
    result = {'pages': len(pages), 'launch_pages': sorted(launch), 'drafts': sorted(drafts), 'guide_pages': ['/' + route + '/' for route in ARTICLE_ROUTES],
              'reachable_from_home': sorted(visited), 'resources': sorted(resources),
              'external_links_not_requested': sorted(external), 'http': http, 'failures': failures}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2))
    print(json.dumps({'pages': len(pages), 'launch_pages': len(launch), 'draft_pages': len(drafts),
                      'local_resources': len(resources), 'http_checks': len(http), 'failures': failures}))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())

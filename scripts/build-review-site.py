#!/usr/bin/env python3
"""Export the launch candidate with private-review guards to a new private-review directory.

This is a preview exporter, never a production publishing command. Editorial notes,
source generators, Git/workspace files and source photos are not web content.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from site_inventory import public_files

ROOT = Path(__file__).resolve().parent.parent
POLICY = ("default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
          "style-src 'self' 'unsafe-inline'; connect-src 'self'; "
          "form-action 'none'; object-src 'none'; base-uri 'self'")
ROBOTS = '<meta name="robots" content="noindex, nofollow">'


def guarded_html(source, guard):
    # The bundled homepage replaces the document. Apply noindex to both documents.
    def robots(document):
        document = re.sub(r'<meta\b[^>]*\bname=[\"\']robots[\"\'][^>]*>', '', document, flags=re.I)
        document, count = re.subn(r'<head\b[^>]*>', lambda m: m[0] + ROBOTS, document, count=1, flags=re.I)
        if count != 1:
            raise ValueError('review HTML needs a head element')
        return document
    match = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', source, re.S)
    if match:
        template = robots(json.loads(match[2]))
        encoded = json.dumps(template, ensure_ascii=False).replace('</', '<\\/')
        source = source[:match.start(2)] + encoded + source[match.end(2):]
    source = robots(source)
    source = re.sub(r'<head\b[^>]*>', lambda m: m[0] + '<meta http-equiv="Content-Security-Policy" content="' + POLICY + '">' + guard, source, count=1, flags=re.I)
    if not all(marker in source for marker in (ROBOTS, POLICY, guard)):
        raise ValueError('review isolation injection failed')
    return source


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', required=True, type=Path, help='New directory outside repository')
    args = cli.parse_args()
    out = args.output.resolve()
    if out == ROOT or ROOT in out.parents:
        cli.error('output must be outside the repository')
    out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('preview', ROOT / 'scripts/preview-site.py')
    preview = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preview)
    guard = preview.GUARD.replace('Local review preview', 'LAN review preview')
    guard = guard.replace("badge.textContent = 'LAN review preview · inquiries disabled';", """badge.textContent = 'Review · inquiries disabled';
    [['Site', '/'], ['Articles', '/articles/']].forEach(function (item) {
      badge.appendChild(document.createTextNode(' · '));
      var link = document.createElement('a'); link.textContent = item[0]; link.href = item[1];
      link.style.color = 'white'; badge.appendChild(link);
    });""")
    public = public_files(ROOT)
    manifest = {}
    for rel in public:
        source = ROOT / rel
        data = source.read_bytes()
        if rel.endswith('.html') and not rel.startswith('google'):
            data = guarded_html(data.decode(), guard).encode()
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        manifest[rel] = hashlib.sha256(data).hexdigest()
    # Store receipt alongside (not within) the public output.
    (out.parent / (out.name + '.manifest.json')).write_text(json.dumps(manifest, indent=2))
    print(json.dumps({'directory': str(out), 'files': len(manifest),
                      'manifest': str((out.parent / (out.name + '.manifest.json')))}))


if __name__ == '__main__':
    main()

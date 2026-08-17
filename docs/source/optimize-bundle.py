#!/usr/bin/env python3
"""Move the homepage bundle's photos and fonts out of the inline manifest.

Why this exists
---------------
`index.html` is a self-contained artifact: a `__bundler/manifest` script holds
every asset as base64, and a small runtime base64-decodes all of it on
DOMContentLoaded, mints a blob URL per asset, string-replaces the uuids into the
`__bundler/template`, and swaps the document. Nothing paints until that finishes.

With the photos inline that is ~1.34 MB of base64 to decode before first paint --
measured at 2.3 s on a zero-latency local server, all of it main-thread CPU. The
photos also could not be cached, could not download in parallel, and their
`loading="lazy"` was inert because the blob already existed.

This script rewrites the bundle so that:

  * the five photos become real files in `assets/photos/` (WebP), referenced by
    relative URL in the template, so they download in parallel, cache normally,
    and lazy-load for real;
  * the fonts become the already-present `assets/fonts/*.woff2` files, which the
    sub-pages also load -- so a visitor moving from the homepage to any other
    page gets cache hits;
  * the eight non-latin font subsets (vietnamese, latin-ext) are dropped. The
    site's copy is pure Latin-1, and `font-display: swap` covers any stray glyph.

Relative URLs are required, not root-absolute: the site is also served from the
project-pages preview URL, where `/assets/...` resolves to the wrong root. The
template already uses `assets/apple-touch-icon.png` this way.

Idempotent. Re-run it after replacing a photo in `photos-src/`.

Usage:
    python3 docs/source/optimize-bundle.py
"""
import base64
import io
import json
import os
import re
import shutil
import sys

from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
INDEX = os.path.join(ROOT, 'index.html')
SRC_DIR = os.path.join(os.path.dirname(__file__), 'photos-src')
OUT_DIR = os.path.join(ROOT, 'assets', 'photos')

# uuid prefix -> (stable filename, is_hero). The uuids are the bundler's own
# asset ids; they are stable for as long as the bundle is not re-exported.
PHOTOS = {
    'ff53a2ac': ('hero', True),
    '46f48897': ('plank', False),
    '312ad96f': ('in-home', False),
    '70ab17f2': ('semi-private', False),
    '29c25994': ('virtual', False),
}

# The latin subset of each face is byte-identical to a file already in
# assets/fonts/, so externalising costs no new bytes in the repo.
FONT_BY_UUID = {
    'ec2932f6': 'archivo-400.woff2',       # Archivo variable, all weights
    '40bdf4e2': 'barlow-condensed-500.woff2',
    'c31304c1': 'barlow-condensed-600.woff2',
    '244a1508': 'barlow-condensed-700.woff2',
}

WEBP_QUALITY = 80

# Photos that must survive a print/PDF or a browser with no WebP support are not
# in play here, so a single modern format is enough. WebP is Baseline (Safari 14,
# 2020); every current browser reads it.


def die(msg):
    sys.exit(f'error: {msg}')


def full_uuid(manifest, prefix):
    hits = [k for k in manifest if k.startswith(prefix)]
    if len(hits) != 1:
        die(f'expected exactly one manifest asset for {prefix}, found {len(hits)}')
    return hits[0]


def read_blocks(html):
    """Return (manifest_dict, template_str, span_of_manifest, span_of_template)."""
    m = re.search(r'(<script type="__bundler/manifest">)(.*?)(</script>)', html, re.S)
    t = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', html, re.S)
    if not m or not t:
        die('could not find the bundler manifest or template block')
    return json.loads(m.group(2)), json.loads(t.group(2)), m, t


def encode_json_for_script(obj):
    """Serialise for embedding inside a <script> without closing the host tag.

    A literal `</script>` anywhere in the payload -- inside the template's own
    markup, for instance -- ends the enclosing script element early and blanks
    the page. Escaping every `</` is what the other builders in this directory
    do, and it is what the bundle itself emits.
    """
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


SRC_EXTS = ('.jpg', '.jpeg', '.png', '.webp')


def find_source(name):
    """Path of the source image for `name`, whatever extension it was saved as."""
    for ext in SRC_EXTS:
        cand = os.path.join(SRC_DIR, name + ext)
        if os.path.exists(cand):
            return cand
    return None


def stash_originals(manifest):
    """Extract the original photos out of the manifest once, so they survive.

    After this script runs the bundle no longer carries them, so `photos-src/`
    becomes the only copy. It is committed for that reason.
    """
    os.makedirs(SRC_DIR, exist_ok=True)
    for prefix, (name, _) in PHOTOS.items():
        # Any supported extension counts as "already have a source" -- replacing
        # a photo means dropping in a new file, which need not be a JPEG.
        if find_source(name):
            continue
        dest = os.path.join(SRC_DIR, f'{name}.jpg')
        hits = [k for k in manifest if k.startswith(prefix)]
        if not hits:
            die(f'{name}: not in the manifest and not in photos-src/ -- nothing to build from')
        open(dest, 'wb').write(base64.b64decode(manifest[hits[0]]['data']))
        print(f'  stashed original  photos-src/{name}.jpg')


def build_photos():
    """Encode every photo in photos-src/ to WebP in assets/photos/."""
    os.makedirs(OUT_DIR, exist_ok=True)
    written = {}
    for _, (name, is_hero) in PHOTOS.items():
        src = find_source(name)
        if not src:
            die(f'{name}: no source image in {SRC_DIR}')
        im = Image.open(src)
        # A PNG straight from an editor may carry alpha the JPEG-era layout
        # never had; flatten onto white rather than letting it go transparent.
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA')
            flat = Image.new('RGB', im.size, (255, 255, 255))
            flat.paste(im, mask=im.split()[-1])
            im = flat
        else:
            im = im.convert('RGB')
        out = os.path.join(OUT_DIR, f'{name}.webp')
        im.save(out, 'WEBP', quality=WEBP_QUALITY, method=6)
        written[name] = (im.size, os.path.getsize(src), os.path.getsize(out))
        print(f'  {name:14} {im.size[0]}x{im.size[1]:<5} '
              f'{os.path.getsize(src)/1024:6.0f}K -> {os.path.getsize(out)/1024:6.0f}K webp'
              + ('   [hero]' if is_hero else ''))
    return written


def main():
    html = open(INDEX, encoding='utf-8').read()
    manifest, template, m_match, t_match = read_blocks(html)
    before = len(html)

    print('photos:')
    stash_originals(manifest)
    build_photos()

    # --- rewrite the template ------------------------------------------------
    for prefix, (name, is_hero) in PHOTOS.items():
        uuid = None
        hits = [k for k in manifest if k.startswith(prefix)]
        if hits:
            uuid = hits[0]
            del manifest[uuid]
        if uuid and uuid in template:
            template = template.replace(uuid, f'assets/photos/{name}.webp')
        elif f'assets/photos/{name}.webp' not in template:
            die(f'{name}: neither the uuid nor the new path is in the template')

    # The hero is the LCP element. `decoding="async"` keeps its decode off the
    # critical path; `fetchpriority="high"` outranks the lazy photos below it.
    hero_img = re.search(r'<img src="assets/photos/hero\.webp"(?![^>]*fetchpriority)', template)
    if hero_img:
        template = (template[:hero_img.end()]
                    + ' fetchpriority="high" decoding="async"'
                    + template[hero_img.end():])

    # --- fonts ---------------------------------------------------------------
    print('fonts:')
    kept, dropped = 0, 0
    for prefix, filename in FONT_BY_UUID.items():
        hits = [k for k in manifest if k.startswith(prefix)]
        if not hits:
            continue
        uuid = hits[0]
        disk = os.path.join(ROOT, 'assets', 'fonts', filename)
        if not os.path.exists(disk):
            die(f'{filename} is referenced but missing from assets/fonts/')
        # Guard the assumption that the on-disk file is the same bytes as the
        # inline copy; if the bundle is ever re-exported this is what catches it.
        if base64.b64decode(manifest[uuid]['data']) != open(disk, 'rb').read():
            die(f'{filename} differs from the inline copy of {prefix} -- check before externalising')
        del manifest[uuid]
        template = template.replace(uuid, f'assets/fonts/{filename}')
        kept += 1
        print(f'  externalised  assets/fonts/{filename}')

    # Drop every remaining woff2: those are the vietnamese and latin-ext subsets.
    for uuid in [k for k, v in manifest.items() if v.get('mime') == 'font/woff2']:
        # Remove the whole @font-face rule, not just the url -- a rule pointing at
        # a dead uuid would make the browser fetch a nonexistent relative path.
        template = re.sub(
            r'@font-face\s*\{[^}]*' + re.escape(uuid) + r'[^}]*\}', '', template)
        del manifest[uuid]
        dropped += 1
    print(f'  kept {kept} latin faces, dropped {dropped} non-latin subsets')

    # --- write index.html ----------------------------------------------------
    html = (html[:m_match.start(2)] + encode_json_for_script(manifest) + html[m_match.end(2):])
    # The template block moved: its offsets came from the pre-edit string.
    t_match = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', html, re.S)
    html = (html[:t_match.start(2)] + encode_json_for_script(template) + html[t_match.end(2):])

    # --- preload hints in the static head ------------------------------------
    # These live in the *outer* document, which the hydration discards -- but by
    # then they have done their job. They start the hero and font fetches during
    # the initial HTML parse, in parallel with the unpack, so the assets are warm
    # in the cache by the time the swapped-in DOM asks for them.
    preloads = ['    <link rel="preload" as="image" href="assets/photos/hero.webp" fetchpriority="high">']
    for filename in FONT_BY_UUID.values():
        preloads.append(f'    <link rel="preload" as="font" type="font/woff2" '
                        f'crossorigin href="assets/fonts/{filename}">')
    block = '\n'.join(preloads)
    html = re.sub(r'\n?[ \t]*<link rel="preload" as="(?:image|font)"[^>]*>', '', html)
    head = re.search(r'<head[^>]*>', html, re.I)
    if not head:
        die('no <head> in the static document')
    html = html[:head.end()] + '\n' + block + html[head.end():]

    open(INDEX, 'w', encoding='utf-8').write(html)
    after = len(html)
    print(f'\nindex.html  {before/1024:.0f}K -> {after/1024:.0f}K  '
          f'({(before-after)/1024:.0f}K removed, -{(before-after)/before*100:.0f}%)')


if __name__ == '__main__':
    main()

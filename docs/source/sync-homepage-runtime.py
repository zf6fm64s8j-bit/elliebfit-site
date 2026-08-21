#!/usr/bin/env python3
"""Apply stable runtime hooks to the generated homepage template.

The homepage source is a JSON-encoded HTML document inside index.html. This
script performs exact, idempotent transforms and fails if a future export no
longer contains the expected source. Run it after replacing the bundled
template or re-exporting the design.
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
INDEX = os.path.join(ROOT, 'index.html')


def die(message):
    sys.exit(f'error: {message}')


def encode_for_script(value):
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def replace_once(text, old, new, label):
    old_count = text.count(old)
    new_count = text.count(new)
    # Some additions deliberately retain the old fragment as the first line of
    # the expanded block (for example, appending a footer link). Recognize the
    # complete new block before treating that retained fragment as stale input.
    if new_count == 1:
        return text, False
    if old_count == 1 and new_count == 0:
        return text.replace(old, new), True
    die(f'{label}: expected one old or one new block; found old={old_count}, new={new_count}')


def main():
    html = open(INDEX, encoding='utf-8').read()
    match = re.search(r'(<script type="__bundler/template">)(.*?)(</script>)', html, re.S)
    if not match:
        die('no __bundler/template block')
    template = json.loads(match.group(2))
    changed = []

    transforms = [
        (
            'Friday class time',
            '10:00 a.m. Arizona time · 12:00 p.m. Central time',
            '10:00 a.m. Arizona time · <span data-central-class-time>'
            '11:00 a.m. CST / 12:00 p.m. CDT (Central time)</span>',
        ),
        (
            'in-home service link',
            'text-transform: uppercase;">In-home 1:1</div>',
            'text-transform: uppercase;"><a href="in-home-personal-training/" '
            'style="color: inherit; text-decoration: none;">In-home 1:1</a></div>',
        ),
        (
            'semi-private service link',
            'text-transform: uppercase;">Semi-private</div>',
            'text-transform: uppercase;"><a href="semi-private-personal-training/" '
            'style="color: inherit; text-decoration: none;">Semi-private</a></div>',
        ),
        (
            'virtual service link',
            'text-transform: uppercase;">Virtual</div>',
            'text-transform: uppercase;"><a href="virtual-personal-training/" '
            'style="color: inherit; text-decoration: none;">Virtual</a></div>',
        ),
        (
            'Friday class signup link',
            'href="mailto:ellen@elliebfit.com?subject=Friday%20free%20class&amp;body=Hi%20Ellen%2C%0A%0AI%27d%20like%20to%20join%20the%20free%20Friday%20class%20%2810%3A00%20a.m.%20Arizona%20time%29.%20Please%20send%20me%20the%20link.%0A%0AName%3A%0A" '
            'style="background:',
            'href="free-class-sign-up/" style="background:',
        ),
        (
            'service area footer link',
            '<a href="pwr-moves/" style="color: oklch(0.40 0.04 168);">PWR!Moves®</a>',
            '<a href="pwr-moves/" style="color: oklch(0.40 0.04 168);">PWR!Moves®</a>\n'
            '        <a href="service-areas/" style="color: oklch(0.40 0.04 168);">Service areas</a>',
        ),
        (
            'privacy footer link',
            '<a href="https://www.facebook.com/elliebfit/" style="color: oklch(0.40 0.04 168);">Facebook</a>',
            '<a href="https://www.facebook.com/elliebfit/" style="color: oklch(0.40 0.04 168);">Facebook</a>\n'
            '        <a href="privacy/" style="color: oklch(0.40 0.04 168);">Privacy</a>',
        ),
        (
            'interest group',
            '<div style="display: flex; flex-wrap: wrap; gap: 8px;">\n'
            '            <button type="button" style="{{ chipInHome }}" sc-camel-on-click="{{ pickInHome }}">In-home</button>\n'
            '            <button type="button" style="{{ chipSemi }}" sc-camel-on-click="{{ pickSemi }}">Semi-private</button>\n'
            '            <button type="button" style="{{ chipVirtual }}" sc-camel-on-click="{{ pickVirtual }}">Virtual</button>\n'
            '            <button type="button" style="{{ chipFriday }}" sc-camel-on-click="{{ pickFriday }}">Friday class</button>\n'
            '          </div>',
            '<div id="abf-interest-group" role="group" aria-labelledby="abf-interest-label" '
            'style="display: flex; flex-wrap: wrap; gap: 8px;">\n'
            '            <button type="button" data-abf-interest="In-home" aria-pressed="{{ ariaInHome }}" style="{{ chipInHome }}" sc-camel-on-click="{{ pickInHome }}">In-home</button>\n'
            '            <button type="button" data-abf-interest="Semi-private" aria-pressed="{{ ariaSemi }}" style="{{ chipSemi }}" sc-camel-on-click="{{ pickSemi }}">Semi-private</button>\n'
            '            <button type="button" data-abf-interest="Virtual" aria-pressed="{{ ariaVirtual }}" style="{{ chipVirtual }}" sc-camel-on-click="{{ pickVirtual }}">Virtual</button>\n'
            '            <button type="button" data-abf-interest="Friday class" aria-pressed="{{ ariaFriday }}" style="{{ chipFriday }}" sc-camel-on-click="{{ pickFriday }}">Friday class</button>\n'
            '          </div>',
        ),
        (
            'submit action',
            '<button type="button" sc-camel-on-click="{{ send }}" style="background:',
            '<button type="button" id="abf-send-request" data-abf-action="send-request" '
            'sc-camel-on-click="{{ send }}" style="background:',
        ),
        (
            'component accessibility state',
            "      send: this.send,\n"
            "      chipInHome: this.chipStyle('In-home'), pickInHome: this.toggle('In-home'),\n"
            "      chipSemi: this.chipStyle('Semi-private'), pickSemi: this.toggle('Semi-private'),\n"
            "      chipVirtual: this.chipStyle('Virtual'), pickVirtual: this.toggle('Virtual'),\n"
            "      chipFriday: this.chipStyle('Friday class'), pickFriday: this.toggle('Friday class')",
            "      send: this.send,\n"
            "      chipInHome: this.chipStyle('In-home'), ariaInHome: String(this.state.picks.includes('In-home')), pickInHome: this.toggle('In-home'),\n"
            "      chipSemi: this.chipStyle('Semi-private'), ariaSemi: String(this.state.picks.includes('Semi-private')), pickSemi: this.toggle('Semi-private'),\n"
            "      chipVirtual: this.chipStyle('Virtual'), ariaVirtual: String(this.state.picks.includes('Virtual')), pickVirtual: this.toggle('Virtual'),\n"
            "      chipFriday: this.chipStyle('Friday class'), ariaFriday: String(this.state.picks.includes('Friday class')), pickFriday: this.toggle('Friday class')",
        ),
    ]

    for label, old, new in transforms:
        template, did_change = replace_once(template, old, new, label)
        if did_change:
            changed.append(label)

    encoded = encode_for_script(template)
    updated = html[:match.start(2)] + encoded + html[match.end(2):]
    if updated != html:
        open(INDEX, 'w', encoding='utf-8').write(updated)

    if changed:
        print('updated: ' + ', '.join(changed))
    else:
        print('homepage runtime hooks already current')


if __name__ == '__main__':
    main()

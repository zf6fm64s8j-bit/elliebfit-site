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
    if old_count == 1 and new_count == 0:
        return text.replace(old, new), True
    if old_count == 0 and new_count == 1:
        return text, False
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

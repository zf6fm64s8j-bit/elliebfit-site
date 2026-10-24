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
        ('Chloe testimonial attribution', 'Chloe W. &middot; Virtual client since 2020</div>', 'Chloe W. &middot; Virtual client</div>'),
        ('J-inspired homepage introduction', '          <div>I found my way into personal training while teaching spin at the YMCA in 2006. I loved seeing people discover that they were stronger and more capable than they thought. I certified in 2010 and have been coaching ever since.</div>\n          <div>After 16 years of working with clients ages 8&ndash;92, I&#8217;ve learned that good training is never one-size-fits-all. Some days we build strength from a chair. Other days we lift, sweat, laugh, and leave a busy week behind. The plan should adapt to your body, your goals, and your life&mdash;not the other way around.</div>\n          <div>I currently work as a personal trainer and group fitness instructor at The J. My earlier professional experience includes personal training with Fit Family Physical Therapy. Through Above &amp; Beyond Fitness, I bring adaptable coaching directly to your home or screen.</div>\n          <div>My husband Michael and I moved to Arizona in 2023, and Above &amp; Beyond Fitness began here. When I&#8217;m not training, I&#8217;m usually with my horse Cisco, paddleboarding with Cricket, or baking cookies. Yes, trainers eat cookies.</div>\n          <div><a href="about-me/">More about Ellen &rarr;</a></div>\n', '          <div>I turned a lifelong love of being active into a personal training career in 2010. After more than 13 years at AYC Health &amp; Fitness in Kansas, I started Above &amp; Beyond Fitness in Arizona in 2023.</div>\n          <div>I help older adults, people returning to exercise, and couples build strength and confidence for the things they enjoy. My approach is adaptable, creative and encouraging: sessions should fit your goals, your abilities and the kind of day you&#8217;re having.</div>\n          <div>I also work as a personal trainer and group fitness instructor at The Valley of the Sun J. Through Above &amp; Beyond Fitness, I bring my coaching experience directly to your home or screen.</div>\n          <div><a href="about-me/">More about Ellen &rarr;</a></div>\n'),
        ('neutral degree wording', 'B.A. Kansas State University', 'Bachelor&#8217;s degree &middot; Kansas State University'),
        ('permanent training guides resource link', '<div id="resources" style="max-width: 1240px; margin: 0 auto; padding: 84px 32px 20px;">', '<div id="resources" style="max-width: 1240px; margin: 0 auto; padding: 84px 32px 20px;">\n    <p><a href="articles/">Training &amp; movement guides &rarr;</a> &mdash; answers about everyday strength, training after joint replacement, couples and Parkinson&#8217;s-specific coaching.</p>'),
        ('permanent training guides footer link', '<a href="recipes/" style="color: oklch(0.40 0.04 168);">Recipes</a>', '<a href="articles/" style="color: oklch(0.40 0.04 168);">Training guides</a>\n        <a href="recipes/" style="color: oklch(0.40 0.04 168);">Recipes</a>'),
        ('dedicated Testimonials link', '      </details>\n    </div>\n  </sc-if>', '      </details>\n      <p><a href="testimonials/">Read all client testimonials &rarr;</a></p>\n    </div>\n  </sc-if>'),
        ('qualified service-area FAQ', '>Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe, Glendale, and nearby communities. Virtual sessions are available anywhere.</div>', '>In-home personal training serves Cave Creek, Scottsdale and Northeast Phoenix, subject to address and current scheduling. Live virtual personal training is also available anywhere.</div>'),
        ('PWR formats', 'Parkinson&#8217;s-specific movement training, integrated into personal training or a small-group class. Personal training works alongside&mdash;not instead of&mdash;medical or physical-therapy care.', 'Parkinson&#8217;s-specific movement training, available through 1:1 or semi-private coaching. Personal training works alongside&mdash;not instead of&mdash;medical or physical-therapy care.'),
        ('ideal-client hero', 'I bring practical, upbeat coaching to your home or your screen. Each session is built around your goals, your body, the equipment you have, and the kind of day you&#8217;re having. Whether you&#8217;re starting from scratch, working around an old injury, or training for something you love, we&#8217;ll help you get stronger, move with confidence, and enjoy the process.', 'I bring practical, upbeat personal training to your home or screen. Older adults, people returning to exercise, and couples receive coaching adapted to their goals, abilities, and how they feel that day. Whether you want to feel stronger for everyday life or stay active for travel and hobbies, we&#8217;ll build from where you are.'),
        ('ideal-client fit', 'Above &amp; Beyond may be a good fit if you&#8217;re new to exercise, returning after time away, working around an old injury, looking for better strength or mobility, training with a partner, or simply ready for coaching that is challenging without being punishing.', 'Above &amp; Beyond welcomes older adults, people returning to exercise, and couples with different fitness levels. You may want more strength or mobility, support building a regular routine, or coaching that works around an old injury. Sessions are built around your abilities and goals, with a challenge that fits you.'),
        ('qualified service area', 'Serving Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe, Glendale, and nearby communities.', 'Serving Cave Creek, Scottsdale and Northeast Phoenix. In-home availability depends on your address and current scheduling; live virtual coaching is also available.'),
        ('Friday class time', '10:00 a.m. Arizona time · 12:00 p.m. Central time', '10:00 a.m. Arizona time · <span data-central-class-time>11:00 a.m. CST / 12:00 p.m. CDT (Central time)</span>'),
        ('in-home service link', 'text-transform: uppercase;">In-home 1:1</div>', 'text-transform: uppercase;"><a href="in-home-personal-training/" style="color: inherit; text-decoration: none;">In-home 1:1</a></div>'),
        ('semi-private service link', 'text-transform: uppercase;">Semi-private</div>', 'text-transform: uppercase;"><a href="semi-private-personal-training/" style="color: inherit; text-decoration: none;">Semi-private</a></div>'),
        ('virtual service link', 'text-transform: uppercase;">Virtual</div>', 'text-transform: uppercase;"><a href="virtual-personal-training/" style="color: inherit; text-decoration: none;">Virtual</a></div>'),
        ('Friday class signup link', 'href="mailto:ellen@elliebfit.com?subject=Friday%20free%20class&amp;body=Hi%20Ellen%2C%0A%0AI%27d%20like%20to%20join%20the%20free%20Friday%20class%20%2810%3A00%20a.m.%20Arizona%20time%29.%20Please%20send%20me%20the%20link.%0A%0AName%3A%0A" style="background:', 'href="free-class-sign-up/" style="background:'),
        ('service area footer link', '<a href="pwr-moves/" style="color: oklch(0.40 0.04 168);">PWR!Moves®</a>', '<a href="pwr-moves/" style="color: oklch(0.40 0.04 168);">PWR!Moves®</a>\n        <a href="service-areas/" style="color: oklch(0.40 0.04 168);">Service areas</a>'),
        ('privacy footer link', '<a href="https://www.facebook.com/elliebfit/" style="color: oklch(0.40 0.04 168);">Facebook</a>', '<a href="https://www.facebook.com/elliebfit/" style="color: oklch(0.40 0.04 168);">Facebook</a>\n        <a href="privacy/" style="color: oklch(0.40 0.04 168);">Privacy</a>'),
        ('interest group', '<div style="display: flex; flex-wrap: wrap; gap: 8px;">\n            <button type="button" style="{{ chipInHome }}" sc-camel-on-click="{{ pickInHome }}">In-home</button>\n            <button type="button" style="{{ chipSemi }}" sc-camel-on-click="{{ pickSemi }}">Semi-private</button>\n            <button type="button" style="{{ chipVirtual }}" sc-camel-on-click="{{ pickVirtual }}">Virtual</button>\n            <button type="button" style="{{ chipFriday }}" sc-camel-on-click="{{ pickFriday }}">Friday class</button>\n          </div>', '<div id="abf-interest-group" role="group" aria-labelledby="abf-interest-label" style="display: flex; flex-wrap: wrap; gap: 8px;">\n            <button type="button" data-abf-interest="In-home" aria-pressed="{{ ariaInHome }}" style="{{ chipInHome }}" sc-camel-on-click="{{ pickInHome }}">In-home</button>\n            <button type="button" data-abf-interest="Semi-private" aria-pressed="{{ ariaSemi }}" style="{{ chipSemi }}" sc-camel-on-click="{{ pickSemi }}">Semi-private</button>\n            <button type="button" data-abf-interest="Virtual" aria-pressed="{{ ariaVirtual }}" style="{{ chipVirtual }}" sc-camel-on-click="{{ pickVirtual }}">Virtual</button>\n            <button type="button" data-abf-interest="Friday class" aria-pressed="{{ ariaFriday }}" style="{{ chipFriday }}" sc-camel-on-click="{{ pickFriday }}">Friday class</button>\n          </div>'),
        ('submit action', '<button type="button" sc-camel-on-click="{{ send }}" style="background:', '<button type="button" id="abf-send-request" data-abf-action="send-request" sc-camel-on-click="{{ send }}" style="background:'),
        ('component accessibility state', "      send: this.send,\n      chipInHome: this.chipStyle('In-home'), pickInHome: this.toggle('In-home'),\n      chipSemi: this.chipStyle('Semi-private'), pickSemi: this.toggle('Semi-private'),\n      chipVirtual: this.chipStyle('Virtual'), pickVirtual: this.toggle('Virtual'),\n      chipFriday: this.chipStyle('Friday class'), pickFriday: this.toggle('Friday class')", "      send: this.send,\n      chipInHome: this.chipStyle('In-home'), ariaInHome: String(this.state.picks.includes('In-home')), pickInHome: this.toggle('In-home'),\n      chipSemi: this.chipStyle('Semi-private'), ariaSemi: String(this.state.picks.includes('Semi-private')), pickSemi: this.toggle('Semi-private'),\n      chipVirtual: this.chipStyle('Virtual'), ariaVirtual: String(this.state.picks.includes('Virtual')), pickVirtual: this.toggle('Virtual'),\n      chipFriday: this.chipStyle('Friday class'), ariaFriday: String(this.state.picks.includes('Friday class')), pickFriday: this.toggle('Friday class')"),
        ('experience badge', '16 years &middot; clients ages 8&ndash;92</div>', '16 years experience</div>'),
    ]

    for label, old, new in transforms:
        template, did_change = replace_once(template, old, new, label)
        if did_change:
            changed.append(label)

    # Apply confirmed region/brand wording to remaining runtime display text.
    for old, new in [('Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe, Glendale, and nearby communities', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe, Glendale and nearby communities', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe and Glendale', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Paradise Valley and the Phoenix area', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Paradise Valley, Phoenix, Cave Creek, Mesa, Tempe, and Glendale', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Serving Scottsdale, Phoenix &amp; the East Valley', 'Serving Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale and the Phoenix area', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale and Phoenix', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale and nearby communities', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale &amp; nearby communities', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale &amp; Phoenix', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale & Phoenix', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Phoenix and the East Valley', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Scottsdale, Phoenix &amp; the East Valley', 'Cave Creek, Scottsdale and Northeast Phoenix'), ('Phoenix-area service area', 'Cave Creek, Scottsdale and Northeast Phoenix service area'), ('Fitness &middot; Scottsdale AZ', 'Fitness &middot; Arizona'), ('Fitness · Scottsdale AZ', 'Fitness · Arizona'), ('LLC &middot; Scottsdale, Arizona', 'LLC &middot; Arizona'), ('Fitness LLC · Scottsdale, Arizona', 'Fitness LLC · Arizona'), ('Scottsdale, Phoenix &amp; the East Valley', 'Cave Creek, Scottsdale &amp; Northeast Phoenix'), ('Yes. Yes.', 'Yes.'), ('Can I have Parkinson’s exercise sessions at home in Scottsdale?', 'Can I have Parkinson’s exercise sessions at home?'), ('I also work as a personal trainer and group fitness instructor at The J. My earlier experience includes Fit Family Physical Therapy. Through Above &amp; Beyond, I bring that coaching experience directly to your home or screen.', 'I also work as a personal trainer and group fitness instructor at The Valley of the Sun J. Through Above &amp; Beyond Fitness, I bring my coaching experience directly to your home or screen.')]:
        template = template.replace(old, new)

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

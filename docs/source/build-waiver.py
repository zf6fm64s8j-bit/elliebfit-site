#!/usr/bin/env python3
"""Build the official Above & Beyond Fitness liability waiver PDF.

Supersedes build-waiver-draft-v2.py. The text here applies the drafting review in
`docs/source/waiver-counsel-review.md`; `docs/waiver-revisions.md` records what
changed in each version and why.

Revisioning
-----------
`VERSION` and `EFFECTIVE` below are the single source of truth. They are stamped
into the running footer of every page and next to the signature block, so a
signed copy identifies on its face which text the client agreed to. To issue a
revision: bump both constants, add an entry to `docs/waiver-revisions.md`, and
re-run. Keep the superseded PDF -- signed copies reference it by version.

Usage:
    python3 docs/source/build-waiver.py
"""
import base64
import os
import subprocess
import tempfile

VERSION = '1.0'
EFFECTIVE = 'August 16, 2026'

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FONTS = os.path.join(ROOT, 'assets', 'fonts')
DEST = os.path.join(ROOT, 'docs', 'liability-waiver.pdf')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def face(fam, wt, fn):
    b64 = base64.b64encode(open(os.path.join(FONTS, fn), 'rb').read()).decode()
    return (f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{wt};"
            f"font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


# Archivo is variable: one file serves every weight.
FACES = ''.join([
    face('Barlow Condensed', 700, 'barlow-condensed-700.woff2'),
    face('Archivo', 400, 'archivo-400.woff2'),
    face('Archivo', 600, 'archivo-400.woff2'),
])

MARK = ('<svg viewBox="0 0 100 100" width="34" height="34" fill="none">'
        '<polygon points="50,8 92,50 76,50 50,24 24,50 8,50" fill="currentColor"></polygon>'
        '<polygon points="50,30 92,72 76,72 50,46 24,72 8,72" fill="currentColor" opacity="0.62"></polygon>'
        '<polygon points="50,52 92,94 76,94 50,68 24,94 8,94" fill="currentColor" opacity="0.3"></polygon>'
        '</svg>')

CSS = """
:root{ --coral:#E4795A; --sage-deep:#2E4A42; --ink:#20342E; --peach:#F7DCC9;
       --sage-tint:#CFE2D8; --muted:#6B8078; }
/* The generous bottom margin shortens the content box so flowed content stops
   well above the running footer, which Chrome anchors to the content box's
   bottom edge without reserving space for it. */
@page{ size: Letter; margin: 0.5in 0.68in 0.85in; }
*{ margin:0; padding:0; box-sizing:border-box; }
html,body{ background:#fff; }
body{ font-family:'Archivo','Helvetica Neue',Helvetica,Arial,sans-serif;
  font-size:10.5pt; line-height:1.48; color:var(--ink); }

.letterhead{ display:flex; align-items:flex-end; justify-content:space-between;
  gap:20px; padding-bottom:9px; }
.lockup{ display:flex; align-items:center; gap:10px; color:var(--ink); }
.wm1{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:17pt; line-height:.95; letter-spacing:.02em; text-transform:uppercase; }
.wm2{ font-size:6pt; letter-spacing:.34em; text-transform:uppercase; color:var(--muted); margin-top:3px; }
.contact{ text-align:right; font-size:7.5pt; line-height:1.5; color:var(--muted); }
.rule{ height:1px; background:var(--peach); margin-bottom:14px; }

h1{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:23pt; line-height:.92; letter-spacing:.02em; text-transform:uppercase;
  color:var(--coral); margin-bottom:3px; }
.subtitle{ font-size:8pt; letter-spacing:.18em; text-transform:uppercase;
  font-weight:600; color:var(--muted); margin-bottom:12px; }
h2{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:12.5pt; line-height:1; letter-spacing:.02em; text-transform:uppercase;
  color:var(--coral); margin:12px 0 4px; break-after:avoid; }

p{ margin-bottom:6px; }
strong{ font-weight:600; }
section{ break-inside:avoid; }
ul{ margin:4px 0 6px 16px; }
li{ margin:2px 0; }

.intro{ background:#FBF6F2; border:1px solid var(--peach); border-radius:10px;
  padding:10px 13px; margin-bottom:12px; font-size:10pt; }
.party{ display:flex; gap:14px; margin-top:7px; }
.party .f{ flex:1; }
.party .fl{ border-bottom:1px solid var(--ink); height:20px; }
.party .fc{ font-size:7pt; letter-spacing:.16em; text-transform:uppercase;
  font-weight:600; color:var(--muted); margin-top:3px; }

.initial{ margin-top:5px; display:flex; align-items:center; gap:9px; }
.initial .box{ width:54px; height:18px; border:1px solid var(--sage-tint); border-radius:4px; }
.initial .lbl{ font-size:7pt; letter-spacing:.16em; text-transform:uppercase;
  font-weight:600; color:var(--muted); }

.sigblock{ margin-top:14px; break-inside:avoid; }
.sigrow{ display:flex; gap:16px; margin-top:16px; }
.sig{ flex:1; } .sig.date{ flex:0 0 120px; }
.sigline{ border-bottom:1px solid var(--ink); height:24px; }
.siglabel{ font-size:7pt; letter-spacing:.16em; text-transform:uppercase;
  font-weight:600; color:var(--muted); margin-top:4px; }
.vstamp{ font-size:7.5pt; color:var(--muted); margin-top:9px; }

.optional{ border:1px dashed var(--sage-tint); border-radius:10px; padding:11px 13px;
  margin-top:14px; break-inside:avoid; }
.optbox{ display:flex; gap:20px; margin-top:8px; align-items:center; }
.optbox .opt{ display:flex; align-items:center; gap:7px; font-size:9.5pt; }
.optbox .sq{ width:15px; height:15px; border:1px solid var(--ink); border-radius:3px; }

/* position:fixed repeats on every printed page in Chrome, so the version stamp
   lands on all four -- a page lifted out of a signed copy is identifiable.
   `bottom` must stay >= 0: Chrome clips fixed content that sits outside the
   page's content box, so a negative offset silently drops the footer entirely. */
footer{ position:fixed; bottom:0; left:0; right:0;
  padding-top:7px; border-top:1px solid var(--peach);
  font-size:7pt; letter-spacing:.16em; text-transform:uppercase; color:var(--muted);
  display:flex; justify-content:space-between; }
"""

AB = 'Above &amp; Beyond Fitness'


def ini(who='Client initials'):
    return f'<div class="initial"><span class="lbl">{who}</span><span class="box"></span></div>'


BODY = f"""
<div class="intro">
This Agreement is between <strong>Above &amp; Beyond Fitness LLC</strong> (&ldquo;{AB}&rdquo;) and
the undersigned client (&ldquo;Client&rdquo;). It applies to every session, class, and related
service provided on or after the date signed below, and remains in effect until replaced in writing.
  <div class="party">
    <div class="f"><div class="fl"></div><div class="fc">Client name (please print)</div></div>
    <div class="f"><div class="fl"></div><div class="fc">Date of this agreement</div></div>
  </div>
</div>

<section><h2>1. Services and locations covered</h2>
<p>Client understands that {AB} provides personal training and fitness instruction
(the &ldquo;Services&rdquo;) that may take place: (a) in Client&rsquo;s home or another private
residence; (b) outdoors, including sidewalks, parks, and desert trails; (c) at a gym, studio,
community facility, or other venue; and (d) remotely by live video (&ldquo;virtual training&rdquo;).
<strong>This Agreement applies to all of these settings</strong> and to any equipment used in them,
whether supplied by {AB} or by Client. <strong>Transportation of Client is not part of the
Services</strong>, and {AB} does not drive Client to or from any session.</p>{ini()}</section>

<section><h2>2. Release of liability</h2>
<p>To the fullest extent permitted by Arizona law, Client <strong>releases and covenants not to
sue</strong> Above &amp; Beyond Fitness LLC and its owners, employees, trainers, independent
contractors, and agents (the &ldquo;Released Parties&rdquo;) for Client&rsquo;s claims for bodily
injury, illness, death, or damage to Client&rsquo;s personal property <strong>arising out of or
related to Client&rsquo;s participation in the Services</strong>, but only to the extent caused by a
Released Party&rsquo;s <strong>ordinary negligence, including a negligent act or omission</strong>.
Covered injuries include, by way of example, muscle strains, pulls or tears, broken bones, joint or
soft-tissue injury, aggravation of a pre-existing condition, falls, heat illness, cardiac events, and
other illness, soreness, or injury.</p>
<p><strong>This release does not apply to gross negligence, recklessness, willful or wanton
misconduct, intentional misconduct, fraud, or any liability that Arizona law does not permit to be
released.</strong> It applies only to claims Client owns or has legal authority to release.</p>
{ini()}</section>

<section><h2>3. Assumption of risks</h2>
<p>Client understands that physical activity carries <strong>known and inherent risks, including the
risk of serious injury and death</strong>, and that some risks may remain even when reasonable care
is used. Client specifically acknowledges the risks of training in a private home (including stairs,
flooring, furniture, pets, and limited space), outdoors (including uneven ground, heat, and sun
exposure), and by live video, where a trainer cannot physically assist. Client is participating
voluntarily with knowledge of these risks and accepts them.</p>{ini()}</section>

<section><h2>4. Health status, screening, and disclosure</h2>
<p>Client represents that Client <strong>has disclosed</strong> to {AB} the known medical conditions,
medications, injuries, surgeries, symptoms, and &mdash; where relevant to safe programming &mdash;
pregnancy or postpartum status that are material to safe exercise, and that the information given in
the <strong>Client Information &amp; Health History questionnaire and the PAR-Q</strong> is true and
complete to the best of Client&rsquo;s knowledge. Those documents are incorporated by reference.</p>
<p><strong>This Agreement is not medical clearance.</strong> Where the PAR-Q or a medical provider
indicates that clearance is advisable, Client will obtain it before participating. {AB} may require
clearance, modify a session, or decline participation where reasonably necessary for safety. Client
will <strong>promptly notify {AB} of any change</strong> in health, medication, injury, surgery, or
pregnancy, and will stop exercising and tell the trainer immediately if Client feels pain, dizziness,
shortness of breath, or any other concerning symptom.</p>{ini()}</section>

<section><h2>5. Scope of practice</h2>
<p>Client understands that {AB} provides fitness instruction only. <strong>{AB} is not a licensed
physician, physical therapist, occupational therapist, or dietitian</strong>, and nothing provided is
medical advice, diagnosis, treatment, rehabilitation, or medical nutrition therapy. Specialized
programming, including PWR!Moves&reg; for Parkinson&rsquo;s, is designed to
<strong>complement &mdash; not replace &mdash;</strong> care directed by Client&rsquo;s medical
providers. Any general nutrition guidance is educational only.</p>{ini()}</section>

<section><h2>6. Training environment and Client responsibilities</h2>
<p>For sessions at a location provided by Client, Client agrees to: provide a reasonably safe space
with adequate clear floor area, lighting, and ventilation; secure pets; remove obvious trip hazards;
and <strong>disclose known hazards</strong>. Any equipment supplied by Client must be in sound
working order and appropriate for its use. Client agrees to provide an
<strong>emergency contact</strong> and to keep it current.</p>
<p><strong>{AB} may modify, postpone, or end a session at any time</strong> &mdash; including for
heat, weather, unsafe conditions, equipment problems, symptoms, or technology limitations &mdash; and
doing so is not a breach of this Agreement.</p>{ini()}</section>

<section><h2>7. Virtual training</h2>
<p>For sessions delivered by live video, Client acknowledges that <strong>the trainer cannot
physically spot, assist, or intervene</strong>, and may be unable to summon help. Client agrees to:
<strong>state Client&rsquo;s current physical location at the start of every virtual session</strong>;
keep a charged phone and a means of contacting emergency services within reach; and ensure the
training space and equipment are safe. Where Client has a fall risk, a balance or cardiac condition,
or trains at higher intensity, {AB} may require that another adult be present or that Client obtain
medical clearance. Client accepts that technology may interrupt or degrade a session.</p>
{ini()}</section>

<section><h2>8. Indemnification</h2>
<p>Client agrees to indemnify and hold harmless {AB} from third-party claims
<strong>to the extent caused by</strong> Client&rsquo;s own negligence or Client&rsquo;s breach of
this Agreement. {AB} will give Client prompt written notice of any such claim, and Client may assume
its defense with counsel reasonably acceptable to {AB}. <strong>Neither party will settle a claim in
a way that imposes an obligation on the other without that party&rsquo;s written consent.</strong>
This Section does not require Client to indemnify {AB} for {AB}&rsquo;s own negligence.</p>
{ini()}</section>

<section><h2>9. Attorneys&rsquo; fees</h2>
<p>In a contested action brought <strong>solely to enforce an express contractual obligation under
this Agreement</strong> &mdash; such as the indemnity in Section 8 or an obligation to pay
&mdash; the prevailing party may recover its reasonable attorneys&rsquo; fees and costs to the extent
a court awards them. <strong>This Section does not create any entitlement to fees merely because
{AB} prevails in a claim for personal injury or property damage.</strong></p>{ini()}</section>

<section><h2>10. Governing law, venue, and construction</h2>
<p>This Agreement is governed by the law of the State of Arizona. Any legal action must be brought in
Maricopa County, Arizona, <strong>except where applicable law requires another forum</strong>. If any
provision is held invalid or unenforceable, <strong>that provision shall be limited only to the
extent necessary</strong> to make it enforceable, or severed if it cannot be, and the remainder shall
continue in full force and effect. An electronic or scanned signature has the same effect as an
original.</p>
<p>This Agreement covers liability, risk, and safety. It <strong>does not supersede</strong> the
separate payment, scheduling, cancellation, refund, or privacy terms between the parties, which
remain in effect on their own terms.</p>{ini()}</section>

<section><h2>11. Acknowledgement of understanding</h2>
<p>Client acknowledges that Client: has read this Agreement and understands its terms;
<strong>received a copy before participating</strong>; had a reasonable opportunity to ask questions;
understands it applies only to the Services and the parties identified in it; and understands
that <strong>there is no guarantee of any particular fitness, health, weight, or
Parkinson&rsquo;s-related outcome</strong>.</p>
<p><strong>Client understands that Client is giving up substantial rights, including the right to sue
for ordinary negligence</strong>, to the fullest extent permitted by Arizona law and subject to the
exclusions stated in Section 2.</p></section>

<div class="sigblock">
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
  <div class="vstamp">Waiver of Liability, version {VERSION} &middot; effective {EFFECTIVE}.
  Retain a signed copy with the Client Information &amp; Health History questionnaire and the PAR-Q.</div>
</div>

<section><h2>12. If the client is under 18</h2>
<p>Parent/Guardian consents to Minor&rsquo;s participation in the Services and represents that
Parent/Guardian has legal authority to provide that consent. Parent/Guardian agrees to provide
accurate health, emergency, and safety information and to comply with the applicable safety
requirements in this Agreement.</p>
<p><strong>Parent/Guardian releases only Parent/Guardian&rsquo;s own claims, if any. Nothing in this
Section purports to release, waive, or limit any substantive claim belonging to Minor, and
Parent/Guardian is not required to indemnify {AB} for {AB}&rsquo;s own negligence.</strong> A new
agreement in the Client&rsquo;s own name is required when Minor turns 18.</p>
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Minor&rsquo;s name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Parent/guardian signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
</section>

<div class="optional">
  <h2 style="margin-top:0">Optional &mdash; photo and video consent</h2>
  <p>This section is <strong>entirely optional and separate</strong> from the agreement above.
  Declining has no effect on training, pricing, or scheduling. If you consent, you allow {AB} to
  photograph or record you during sessions and to use those images on its website and social media.</p>
  <p style="margin-bottom:0">You may <strong>withdraw consent at any time in writing</strong>.
  Withdrawal applies going forward: {AB} will make reasonable efforts to remove the images from its
  own website and accounts, but <strong>cannot control copies or reposts by third parties</strong>.
  Consent for a client under 18 is handled on a separate parent/guardian marketing consent form.</p>
  <div class="optbox">
    <div class="opt"><span class="sq"></span> I consent</div>
    <div class="opt"><span class="sq"></span> I do not consent</div>
    <div class="sig" style="max-width:210px"><div class="sigline"></div>
      <div class="siglabel">Signature &middot; date</div></div>
  </div>
</div>
"""

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Waiver of Liability — v{VERSION}</title><style>{FACES}{CSS}</style></head><body>
<div class="letterhead">
  <div class="lockup">{MARK}<div><div class="wm1">Above &amp; Beyond</div>
  <div class="wm2">Fitness &middot; Scottsdale AZ</div></div></div>
  <div class="contact">Above &amp; Beyond Fitness LLC<br>Scottsdale, Arizona<br>
  ellen@elliebfit.com &middot; elliebfit.com</div>
</div>
<div class="rule"></div>
<h1>Waiver of Liability, Indemnity Agreement and Assumption of Risk</h1>
<div class="subtitle">Please read carefully &middot; Initial each section &middot; Sign below</div>
{BODY}
<footer><span>Above &amp; Beyond Fitness LLC</span>
<span>Liability Waiver &middot; v{VERSION} &middot; Effective {EFFECTIVE}</span></footer>
</body></html>"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, 'waiver.html')
        pdf = os.path.join(tmp, 'waiver.pdf')
        open(src, 'w', encoding='utf-8').write(HTML)
        subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--allow-file-access-from-files', '--no-pdf-header-footer',
                        f'--print-to-pdf={pdf}', 'file://' + src],
                       check=True, capture_output=True, timeout=120)
        os.replace(pdf, DEST)
    print(f'built docs/liability-waiver.pdf  v{VERSION}  '
          f'effective {EFFECTIVE}  {os.path.getsize(DEST):,} bytes')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Draft v2 of the liability waiver, adapted to Ellen's actual delivery model.

NOT legal advice and NOT ready for use. Carries a draft marker until an Arizona
attorney has reviewed it. Built on the brand guide's client-document spec.
"""
import base64, os, subprocess

SC = '/private/tmp/claude-501/-Users-michaeldevore-AI-projects/7cae8275-8233-41e3-ba89-1776a37bb027/scratchpad'
FONTS = '/Users/michaeldevore/AI_projects/elliebfit-site/assets/fonts'
OUT = SC + '/pdfout3'
os.makedirs(OUT, exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def face(fam, wt, fn):
    b64 = base64.b64encode(open(os.path.join(FONTS, fn), 'rb').read()).decode()
    return (f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{wt};"
            f"font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


FACES = ''.join([
    face('Barlow Condensed', 700, 'barlow-condensed-700.woff2'),
    face('Archivo', 400, 'archivo-400.woff2'),
    face('Archivo', 600, 'archivo-600.woff2'),
])

MARK = ('<svg viewBox="0 0 100 100" width="34" height="34" fill="none">'
        '<polygon points="50,8 92,50 76,50 50,24 24,50 8,50" fill="currentColor"></polygon>'
        '<polygon points="50,30 92,72 76,72 50,46 24,72 8,72" fill="currentColor" opacity="0.62"></polygon>'
        '<polygon points="50,52 92,94 76,94 50,68 24,94 8,94" fill="currentColor" opacity="0.3"></polygon>'
        '</svg>')

CSS = """
:root{ --coral:#E4795A; --sage-deep:#2E4A42; --ink:#20342E; --peach:#F7DCC9;
       --sage-tint:#CFE2D8; --muted:#6B8078; }
@page{ size: Letter; margin: 0.5in 0.68in 0.6in; }
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

.draft{ background:#FDECE7; border-left:3px solid var(--coral); padding:7px 11px;
  font-size:8.5pt; color:var(--ink); margin-bottom:12px; }

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

.optional{ border:1px dashed var(--sage-tint); border-radius:10px; padding:11px 13px;
  margin-top:14px; break-inside:avoid; }
.optbox{ display:flex; gap:20px; margin-top:8px; align-items:center; }
.optbox .opt{ display:flex; align-items:center; gap:7px; font-size:9.5pt; }
.optbox .sq{ width:15px; height:15px; border:1px solid var(--ink); border-radius:3px; }

footer{ margin-top:16px; padding-top:7px; border-top:1px solid var(--peach);
  font-size:7pt; letter-spacing:.16em; text-transform:uppercase; color:var(--muted);
  display:flex; justify-content:space-between; }
"""

AB = 'Above &amp; Beyond Fitness'


def ini(who='Client initials'):
    return f'<div class="initial"><span class="lbl">{who}</span><span class="box"></span></div>'


BODY = f"""
<div class="draft"><strong>DRAFT v2 &mdash; pending legal review.</strong> Prepared for review by an
Arizona attorney. Do not put into use, and remove this notice only after counsel has approved the
final text.</div>

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
<p>Client understands that {AB} provides personal training and fitness instruction that may take
place: (a) in Client&rsquo;s home or another private residence; (b) outdoors, including sidewalks,
parks, and desert trails; (c) at a gym, studio, community facility, or other venue; and (d) remotely
by live video (&ldquo;virtual training&rdquo;). <strong>This Agreement applies to all of these
settings</strong>, to any equipment used in them &mdash; whether supplied by {AB} or by Client
&mdash; and to travel by {AB} to and from any session location.</p>{ini()}</section>

<section><h2>2. Waiver of liability</h2>
<p>Client, for Client and for Client&rsquo;s heirs, personal representatives, and assigns, in
consideration of being permitted to participate in the services described in Section 1, and in
addition to the payment of any fee or charge, <strong>does hereby release, waive, covenant not to sue,
and discharge</strong> {AB}, its owner, employees, trainers, independent contractors,
representatives, and agents <strong>from any and all claims, demands, and causes of action arising
from the ordinary negligence or omission</strong> of {AB} or any of those parties. This applies to:</p>
<ul>
<li><strong>Personal injury</strong> &mdash; including but not limited to death, heart attack, stroke,
muscle strains, pulls or tears, broken bones, joint or soft-tissue injury, aggravation of a
pre-existing condition, falls, heat illness, or any other illness, soreness, or injury &mdash;
however caused, occurring during or after participation in any service described in Section 1; and</li>
<li><strong>Property</strong> &mdash; any claim for damage to, loss of, or theft of Client&rsquo;s
property in connection with those services.</li>
</ul>
<p><strong>This release does not apply to gross negligence, recklessness, or intentional misconduct,
or to any liability that cannot lawfully be released under Arizona law.</strong></p>{ini()}</section>

<section><h2>3. Assumption of risks</h2>
<p>Client understands that physical activity carries inherently dangerous risks that cannot be
eliminated regardless of the care taken. <strong>These risks include the risk of serious injury and
even death.</strong> Client specifically acknowledges the risks of training in a private home
(including stairs, flooring, furniture, pets, and limited space), outdoors (including uneven ground,
heat, and sun exposure), and by live video, where a trainer cannot physically assist. Client is
voluntarily participating with knowledge of these risks and <strong>expressly assumes and accepts
any and all risks of injury or death.</strong></p>{ini()}</section>

<section><h2>4. Health status, screening, and disclosure</h2>
<p>Client represents that Client knows of no medical or physical condition that would prevent safe
participation, and that the information given in the <strong>Client Information &amp; Health History
questionnaire and the PAR-Q</strong> is true and complete. Those documents are incorporated into
this Agreement by reference. Where the PAR-Q or any medical provider indicates that clearance is
advisable, Client will obtain it before participating. <strong>Client will promptly notify {AB} of
any change in health, medication, injury, surgery, or pregnancy</strong>, and will stop exercising
and tell the trainer immediately if Client feels pain, dizziness, shortness of breath, or any other
concerning symptom.</p>{ini()}</section>

<section><h2>5. Scope of practice</h2>
<p>Client understands that {AB} provides fitness instruction only. <strong>{AB} is not a licensed
physician, physical therapist, occupational therapist, or dietitian</strong>, and nothing provided is
medical advice, diagnosis, treatment, rehabilitation, or medical nutrition therapy. Specialized
programming, including PWR!Moves&reg; for Parkinson&rsquo;s, is designed to
<strong>complement &mdash; not replace &mdash;</strong> care directed by Client&rsquo;s medical
providers. Any general nutrition guidance is educational only.</p>{ini()}</section>

<section><h2>6. Training environment and Client responsibilities</h2>
<p>For sessions at a location provided by Client, Client agrees to provide a reasonably safe space
with adequate clear floor area, lighting, and ventilation; to secure pets; to remove obvious trip
hazards; and to disclose known hazards. Any equipment supplied by Client must be in sound working
order and appropriate for its use. <strong>{AB} may modify, postpone, or end a session at any time if
conditions are judged unsafe</strong>, and doing so is not a breach of this Agreement.</p>{ini()}</section>

<section><h2>7. Virtual training</h2>
<p>For sessions delivered by live video, Client acknowledges that <strong>the trainer cannot
physically spot, assist, or intervene</strong>, and may be unable to summon help. Client is
responsible for the safety of the training space and equipment and for having a means to call for
assistance. Client is encouraged to have another adult present if Client has a fall risk, a balance
or cardiac condition, or is training at higher intensity. Client accepts that technology may
interrupt or degrade a session.</p>{ini()}</section>

<section><h2>8. Indemnification</h2>
<p>Client agrees to indemnify and hold harmless {AB} from claims brought by third parties arising out
of Client&rsquo;s own negligence or Client&rsquo;s breach of this Agreement. To the extent permitted
by Arizona law, the party that prevails in any action to enforce this Agreement may recover its
reasonable attorneys&rsquo; fees and costs.</p>{ini()}</section>

<section><h2>9. Governing law, venue, and construction</h2>
<p>This Agreement is governed by the law of the State of Arizona, and any legal action must be
brought in Maricopa County, Arizona. It is intended to be as broad and inclusive as Arizona law
permits. If any provision is held invalid or unenforceable, it shall be reformed to the maximum
extent enforceable, and the remainder shall continue in full force and effect. This Agreement,
together with the health documents incorporated in Section 4, is the entire agreement between the
parties on this subject. An electronic or scanned signature has the same effect as an original.</p>
{ini()}</section>

<section><h2>10. Acknowledgement of understanding</h2>
<p>Client has read this Agreement and fully understands its terms. <strong>Client understands that
Client is giving up substantial rights, including the right to sue for ordinary negligence.</strong>
Client acknowledges signing freely and voluntarily, and intends this to be a release and assumption
of risk <strong>to the fullest extent permitted by Arizona law, subject to the exclusions stated in
Section 2.</strong></p></section>

<div class="sigblock">
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
</div>

<section><h2>11. If the client is under 18</h2>
<p>The parent or legal guardian signing below represents that they have legal authority to act for
the minor, and they agree to everything above on the minor&rsquo;s behalf and on their own behalf.
<strong>The parent or guardian further agrees to indemnify and hold harmless {AB} from any claim
brought by or on behalf of the minor arising from ordinary negligence, to the fullest extent
permitted by Arizona law.</strong> The parties understand that some rights of a minor may not be
waivable in advance, and that this Section applies only so far as the law allows.</p>
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Parent/guardian name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Parent/guardian signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
</section>

<div class="optional">
  <h2 style="margin-top:0">Optional &mdash; photo and video consent</h2>
  <p style="margin-bottom:0">This section is <strong>entirely optional and separate</strong> from the
  agreement above. Declining has no effect on training, pricing, or scheduling. If you consent, you
  allow {AB} to photograph or record you during sessions and to use those images on its website and
  social media. You may withdraw consent at any time in writing.</p>
  <div class="optbox">
    <div class="opt"><span class="sq"></span> I consent</div>
    <div class="opt"><span class="sq"></span> I do not consent</div>
    <div class="sig" style="max-width:210px"><div class="sigline"></div>
      <div class="siglabel">Signature &middot; date</div></div>
  </div>
</div>
"""

HTML = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>Waiver of Liability — Draft v2</title><style>{FACES}{CSS}</style></head><body>
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
<footer><span>Above &amp; Beyond Fitness LLC</span><span>Liability Waiver &middot; Draft v2</span></footer>
</body></html>"""

src = os.path.join(OUT, 'liability-waiver-draft-v2.html')
pdf = os.path.join(OUT, 'liability-waiver-draft-v2.pdf')
open(src, 'w', encoding='utf-8').write(HTML)
subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                '--allow-file-access-from-files', '--no-pdf-header-footer',
                f'--print-to-pdf={pdf}', 'file://' + src],
               check=True, capture_output=True, timeout=120)
print(f'built {os.path.basename(pdf)}  {os.path.getsize(pdf):,} bytes')

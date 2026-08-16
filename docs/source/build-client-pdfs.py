#!/usr/bin/env python3
"""Rebuild the two client PDFs on the Desert coral & sage brand guide.

Guide, section 07: "Client documents — One-ink mark, white paper, Archivo 11pt
body, coral for headings only."
"""
import base64, os, subprocess

SC = '/private/tmp/claude-501/-Users-michaeldevore-AI-projects/7cae8275-8233-41e3-ba89-1776a37bb027/scratchpad'
FONTS = '/Users/michaeldevore/AI_projects/elliebfit-site/assets/fonts'
OUT = SC + '/pdfout2'
os.makedirs(OUT, exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def face(family, weight, filename):
    b64 = base64.b64encode(open(os.path.join(FONTS, filename), 'rb').read()).decode()
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


FACES = ''.join([
    face('Barlow Condensed', 600, 'barlow-condensed-600.woff2'),
    face('Barlow Condensed', 700, 'barlow-condensed-700.woff2'),
    face('Archivo', 400, 'archivo-400.woff2'),
    face('Archivo', 500, 'archivo-500.woff2'),
    face('Archivo', 600, 'archivo-600.woff2'),
])

# One-ink Ascent mark: a single ink at the brand's three tints.
MARK = ('<svg class="mark" viewBox="0 0 100 100" width="34" height="34" fill="none">'
        '<polygon points="50,8 92,50 76,50 50,24 24,50 8,50" fill="currentColor"></polygon>'
        '<polygon points="50,30 92,72 76,72 50,46 24,72 8,72" fill="currentColor" opacity="0.62"></polygon>'
        '<polygon points="50,52 92,94 76,94 50,68 24,94 8,94" fill="currentColor" opacity="0.3"></polygon>'
        '</svg>')

CSS = """
:root{
  --coral:#E4795A; --coral-deep:#D46B4D; --sage-deep:#2E4A42; --ink:#20342E;
  --peach:#F7DCC9; --sage-tint:#CFE2D8; --muted:#6B8078;
}
@page{ size: Letter; margin: 0.5in 0.68in 0.55in; }
*{ margin:0; padding:0; box-sizing:border-box; }
html,body{ background:#fff; }            /* white paper */
body{
  font-family:'Archivo','Helvetica Neue',Helvetica,Arial,sans-serif;
  font-size:11pt; line-height:1.5; color:var(--ink);
  -webkit-font-smoothing:antialiased;
}

/* ---- letterhead: one-ink mark ---- */
.letterhead{ display:flex; align-items:flex-end; justify-content:space-between;
  gap:20px; padding-bottom:10px; }
.lockup{ display:flex; align-items:center; gap:10px; color:var(--ink); }
.lockup .mark{ flex:none; }
.wm1{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:17pt; line-height:.95; letter-spacing:.02em; text-transform:uppercase; }
.wm2{ font-size:6pt; letter-spacing:.34em; text-transform:uppercase;
  color:var(--muted); margin-top:3px; }
.contact{ text-align:right; font-size:7.5pt; line-height:1.5; color:var(--muted); }
.rule{ height:1px; background:var(--peach); margin-bottom:16px; }

/* ---- headings: coral only ---- */
h1{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:24pt; line-height:.92; letter-spacing:.02em; text-transform:uppercase;
  color:var(--coral); margin-bottom:3px; }
.subtitle{ font-size:8pt; letter-spacing:.18em; text-transform:uppercase;
  font-weight:600; color:var(--muted); margin-bottom:15px; }
h2{ font-family:'Barlow Condensed',Arial Narrow,sans-serif; font-weight:700;
  font-size:13pt; line-height:1; letter-spacing:.02em; text-transform:uppercase;
  color:var(--coral); margin:13px 0 5px; break-after:avoid; }

/* ---- body ---- */
p{ margin-bottom:7px; }
strong{ font-weight:600; }
section{ break-inside:avoid; }

.initial{ margin-top:6px; display:flex; align-items:center; gap:9px; }
.initial .box{ width:56px; height:19px; border:1px solid var(--sage-tint); border-radius:4px; }
.initial .lbl{ font-size:7pt; letter-spacing:.18em; text-transform:uppercase;
  font-weight:600; color:var(--muted); }

/* ---- signatures ---- */
.sigblock{ margin-top:16px; break-inside:avoid; }
.sigrow{ display:flex; gap:18px; margin-top:18px; }
.sig{ flex:1; } .sig.date{ flex:0 0 128px; }
.sigline{ border-bottom:1px solid var(--ink); height:25px; }
.siglabel{ font-size:7pt; letter-spacing:.18em; text-transform:uppercase;
  font-weight:600; color:var(--muted); margin-top:4px; }
.minor{ margin-top:15px; border-left:3px solid var(--sage-tint);
  padding:2px 0 2px 11px; font-size:9pt; color:var(--ink); }

/* ---- policy ---- */
.policy p{ font-size:11.5pt; line-height:1.62; margin-bottom:13px; max-width:640px; }
.callout{ border-left:3px solid var(--coral); padding:3px 0 3px 13px;
  margin:15px 0; font-size:11.5pt; line-height:1.62; max-width:640px; }
.signoff{ margin-top:24px; font-family:'Barlow Condensed',Arial Narrow,sans-serif;
  font-weight:700; font-size:13pt; letter-spacing:.02em; text-transform:uppercase;
  color:var(--coral); }

footer{ margin-top:20px; padding-top:8px; border-top:1px solid var(--peach);
  font-size:7pt; letter-spacing:.18em; text-transform:uppercase; color:var(--muted);
  display:flex; justify-content:space-between; }
"""

CONTACT = ("<div class='contact'>Above &amp; Beyond Fitness LLC<br>Scottsdale, Arizona<br>"
           "ellen@elliebfit.com &middot; elliebfit.com</div>")


def shell(title, subtitle, body, doc_id):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>{title}</title><style>{FACES}{CSS}</style></head><body>
<div class="letterhead">
  <div class="lockup">{MARK}<div><div class="wm1">Above &amp; Beyond</div>
  <div class="wm2">Fitness &middot; Scottsdale AZ</div></div></div>
  {CONTACT}
</div>
<div class="rule"></div>
<h1>{title}</h1>
<div class="subtitle">{subtitle}</div>
{body}
<footer><span>Above &amp; Beyond Fitness LLC</span><span>{doc_id}</span></footer>
</body></html>"""


def ini():
    return ('<div class="initial"><span class="lbl">Please initial</span>'
            '<span class="box"></span></div>')


AB = 'Above &amp; Beyond Fitness'
waiver = f"""
<section><h2>Waiver of Liability</h2>
<p>I, the undersigned (&ldquo;Client&rdquo;), for myself, my heirs, personal representatives and
assigns, in consideration of authorization to use, today and on all future dates, the property,
facilities, and services of Above &amp; Beyond Fitness LLC (hereinafter referred to as {AB}), in
addition to the payment of any fee or charge, <strong>do hereby release, waive, covenant not to sue
and discharge</strong> {AB}, its owners, employees, trainers, contractors, representatives,
volunteers, agents and all others <strong>from any and all claims, demands and causes of action
arising from the ordinary negligence or omission</strong> of {AB} or any of the aforementioned
parties. This agreement applies to 1) personal injury (including, but not limited to, death, heart
attacks, muscle strains, pulls or tears, broken bones, shin splints, heat prostration, knee/lower
back/foot injuries, or any other illness, soreness, or injury), however caused, occurring during or
after my participation in {AB} exercise programs or activities including, but not limited to,
aerobic dance, weight training, stationary bicycling, organized activities, classes, observation,
and individual use of, facilities, premises, aerobic-conditioning machinery or equipment; and to 2)
any and all claims resulting from damages to, loss of, or theft of property.</p>{ini()}</section>

<section><h2>Indemnification and Hold Harmless</h2>
<p>I, the undersigned (&ldquo;Client&rdquo;), also agree to HOLD HARMLESS AND INDEMNIFY {AB} from
ordinary negligence and to reimburse them for any expenses incurred as a result of my participation
in exercise, training, and fitness activities at or facilitated by {AB}. I further agree to pay all
costs and attorneys&rsquo; fees incurred by {AB} in investigating and defending a claim or suit if
my claim is withdrawn, or to the extent a court or arbitration determines that {AB} is not
responsible for the injury or loss.</p>{ini()}</section>

<section><h2>Assumption of Risks</h2>
<p>I, the undersigned (&ldquo;Client&rdquo;), understand and am aware that physical activity,
including the use of facilities, equipment and machinery, carries with it inherently dangerous risks
that cannot be eliminated regardless of the care taken to avoid injuries. <strong>These inherently
dangerous physical activities involve a risk of injury and even death</strong> and I am voluntarily
participating in these inherently dangerous activities offered through {AB} with the knowledge of
the inherent dangers involved. I fully understand the nature of physical activity at or facilitated
by {AB}, the physical demand of activities made possible by {AB}, and I may injure myself as a
result of my participation in {AB}&rsquo;s exercise and fitness training program. <strong>I hereby
affirm that my participation at {AB} is voluntary and expressly assume and accept any and all risks
of injury or death.</strong></p>{ini()}</section>

<section><h2>Severability and Venue</h2>
<p>The undersigned further expressly agrees that the foregoing waiver of liability, indemnity, and
assumption of risks agreement is intended to be as broad and inclusive as is permitted by the law of
the State of Arizona and that if any portion thereof is held invalid, it is agreed that the balance
shall, notwithstanding, continue in full legal force and effect. Likewise, I agree that if legal
action is brought, it must be brought in Maricopa County, Arizona.</p>{ini()}</section>

<section><h2>Acknowledgement of Understanding</h2>
<p>I have read this waiver of liability, indemnification and assumption of risks agreement and fully
understand its terms. I understand that I am giving up substantial rights, including my right to
sue. I acknowledge that I am signing the agreement freely and voluntarily, and intend my signature
to be a complete and unconditional release of all liability and assumption of the inherent risks of
participating in or observing recreational, fitness, and training activities at {AB} to the greatest
extent allowed by law in the State of Arizona.</p></section>

<div class="sigblock">
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Client signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
  <div class="minor">If under 18, a parent or legal guardian must sign below and initial above as
  authorization of this waiver.</div>
  <div class="sigrow">
    <div class="sig"><div class="sigline"></div><div class="siglabel">Parent/guardian name (please print)</div></div>
    <div class="sig"><div class="sigline"></div><div class="siglabel">Parent/guardian signature</div></div>
    <div class="sig date"><div class="sigline"></div><div class="siglabel">Date</div></div>
  </div>
</div>
"""

policy = """
<div class="policy">
<p>I understand that plans change. If you need to cancel or reschedule, please provide at least
24&nbsp;hours&rsquo; notice. Cancellations made with less than 24&nbsp;hours&rsquo; notice will be
charged as scheduled.</p>
<div class="callout">If Ellen has availability, you may reschedule the session before the end of
that same week and use it instead of losing it.</div>
<p>Thank you for respecting the schedule and helping keep training times available for everyone.</p>
<div class="signoff">Progress has a path.</div>
</div>
"""

for name, html in [
    ('liability-waiver', shell('Waiver of Liability, Indemnity Agreement and Assumption of Risk',
                               'Please read carefully &middot; Initial each section &middot; Sign below',
                               waiver, 'Liability Waiver')),
    ('late-cancel-policy', shell('Late Cancellation Policy',
                                 '24 hours&rsquo; notice &middot; All scheduled sessions',
                                 policy, 'Cancellation Policy')),
]:
    src = os.path.join(OUT, name + '.html')
    pdf = os.path.join(OUT, name + '.pdf')
    open(src, 'w', encoding='utf-8').write(html)
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                    '--allow-file-access-from-files', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', 'file://' + src],
                   check=True, capture_output=True, timeout=120)
    print(f'{name}.pdf  {os.path.getsize(pdf):,} bytes')

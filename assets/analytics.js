/* Google Analytics 4 for elliebfit.com.
 *
 * Paste the Measurement ID below and analytics turns on everywhere at once --
 * this file is the single source of truth for it, loaded by the homepage bundle
 * and by every hand-written page. Leave it blank and nothing loads: no script,
 * no cookie, no third-party request. That is the deliberate default, so the site
 * never ships a half-configured tag.
 *
 *     var GA_MEASUREMENT_ID = 'G-XXXXXXXXXX';
 *
 * PRIVACY RULE, non-negotiable: never pass free text from the consult form to
 * an event. The "working toward" textarea routinely contains injuries and
 * health conditions. Event parameters here are fixed strings and enums only --
 * never a name, an email address, or anything the visitor typed in prose.
 */
(function () {
  'use strict';

  var GA_MEASUREMENT_ID = '';   // <- paste G-XXXXXXXXXX here

  if (!GA_MEASUREMENT_ID) return;

  // The homepage runs this twice: it is referenced from the bundle template's
  // <helmet>, and the runtime both re-creates scripts to make them execute and
  // hoists the helmet into <head>. Only one tag survives in the DOM, but the
  // file evaluates twice -- which sent two page_view hits and would have
  // doubled every traffic number. Guard on window, which outlives the document
  // swap that causes the problem in the first place.
  if (window.__abfAnalyticsLoaded) return;
  window.__abfAnalyticsLoaded = true;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  gtag('js', new Date());
  gtag('config', GA_MEASUREMENT_ID, {
    // No advertising features: this is a local service business measuring
    // whether its own pages convert, not building audiences.
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
  document.head.appendChild(s);

  // Client PDFs -- the waiver and the cancellation policy -- are a real signal
  // that someone is about to become a client. Filenames only, never a query.
  document.addEventListener('click', function (e) {
    for (var n = e.target, i = 0; n && i < 5; n = n.parentElement, i++) {
      if (n.tagName === 'A' && /\.pdf(\?|$)/i.test(n.getAttribute('href') || '')) {
        gtag('event', 'pdf_open', {
          file_name: n.getAttribute('href').split('/').pop().split('?')[0]
        });
        return;
      }
    }
  }, true);
})();

/* Events emitted elsewhere, all parameter-free or enum-only:
 *
 *   consult_submit   index.html inline handler   the consult request sent
 *   consult_error    index.html inline handler   { reason: 'validation' | 'transport' }
 *   form_submit      assets/forms.js             { form_name: <fixed label> }
 *   pdf_open         here                        { file_name }
 */

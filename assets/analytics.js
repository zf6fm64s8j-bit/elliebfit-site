/* Cloudflare Web Analytics for elliebfit.com.
 *
 * Paste the site token below and analytics turns on everywhere at once -- this
 * file is the single source of truth for it, loaded by the homepage bundle and
 * by every hand-written page. Leave it blank and nothing loads: no script, no
 * cookie, no third-party request. That is the deliberate default, so the site
 * never ships a half-configured tag.
 *
 *     var CF_BEACON_TOKEN = '0123456789abcdef0123456789abcdef';
 *
 * Get it from dash.cloudflare.com -> Analytics & Logs -> Web Analytics ->
 * Add a site -> www.elliebfit.com -> Manage site. The token is the hex string
 * inside the data-cf-beacon JSON of the snippet Cloudflare shows you; this file
 * builds the tag itself, so only the token is needed.
 *
 * No cookies, no fingerprinting, no personal data -- which is why the site
 * carries no consent banner. Nothing here needs one.
 *
 * WHAT THIS CANNOT DO: Cloudflare Web Analytics is dashboard-only and has no
 * programmatic API, so there is no way to record a conversion. Page views,
 * referrers, countries, and Core Web Vitals only. The consult-form and
 * questionnaire submissions that used to be tracked are counted instead by
 * Ellen's inbox (Formspree) and the Google Sheet (Apps Script) -- see the note
 * at the bottom of this file for where the call sites were, if a tool that can
 * receive conversions is ever added.
 */
(function () {
  'use strict';

  var CF_BEACON_TOKEN = '';   // <- paste the Cloudflare site token here

  if (!CF_BEACON_TOKEN) return;

  // The homepage runs this twice: it is referenced from the bundle template's
  // <helmet>, and the runtime both re-creates scripts to make them execute and
  // hoists the helmet into <head>. Only one tag survives in the DOM, but the
  // file evaluates twice -- which would double every page-view figure. Guard on
  // window, which outlives the document swap that causes the problem.
  if (window.__abfAnalyticsLoaded) return;
  window.__abfAnalyticsLoaded = true;

  var s = document.createElement('script');
  s.defer = true;
  s.src = 'https://static.cloudflareinsights.com/beacon.min.js';
  // The beacon reads its own tag's attribute, so it has to be set before the
  // element is inserted. "spa" stays false: the homepage swaps its document
  // once during hydration but never changes route, so it is not a router app
  // and a second view would be counted for a page nobody navigated to.
  s.setAttribute('data-cf-beacon', JSON.stringify({ token: CF_BEACON_TOKEN, spa: false }));
  (document.body || document.head || document.documentElement).appendChild(s);
})();

/* Conversion call sites, removed when this moved from GA4 to Cloudflare.
 * Re-add these four if a tool that can receive events is ever introduced --
 * and keep the rule that made them safe: never pass free text, a name, or an
 * email. The consult form's "working toward" textarea routinely carries
 * injuries and health conditions.
 *
 *   index.html   consult sent OK          -> after the "on its way" flash()
 *   index.html   validation refused       -> in the missing name/email branch
 *   index.html   transport failed         -> in the fetch .catch()
 *   forms.js     questionnaire submitted  -> in succeed(), form label only
 */

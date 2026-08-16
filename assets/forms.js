/**
 * Client form submission.
 *
 * Posts to the Apps Script web app in docs/apps-script/, which appends the
 * submission to a Google Doc. The previous Google Forms path was abandoned:
 * /formResponse now rejects third-party posts with HTTP 400 and submissions
 * were being silently dropped.
 *
 * Content-Type is text/plain on purpose. It keeps the request a CORS "simple
 * request", so the browser skips the preflight that Apps Script cannot answer.
 */
(function () {
  'use strict';

  // Paste the Apps Script /exec URL here. Blank = email fallback only.
  var ENDPOINT = '';

  var CONTACT = 'ellen@elliebfit.com';

  function collect(form) {
    var fields = [];
    var seenGroups = {};

    form.querySelectorAll('[data-section], [data-label]').forEach(function (el) {
      if (el.hasAttribute('data-section')) {
        fields.push({ label: el.getAttribute('data-section'), value: '—', section: true });
        return;
      }

      var label = el.getAttribute('data-label');
      var value = '';

      if (el.hasAttribute('data-group')) {
        var group = el.getAttribute('data-group');
        if (seenGroups[group]) return;
        seenGroups[group] = true;
        var picked = form.querySelector('input[name="' + group + '"]:checked');
        value = picked ? picked.value : '';
      } else if (el.hasAttribute('data-date')) {
        var parts = el.querySelectorAll('select');
        var vals = [];
        for (var i = 0; i < parts.length; i++) {
          if (!parts[i].value) { vals = []; break; }
          vals.push(parts[i].value);
        }
        value = vals.length ? vals.join(' / ') : '';
      } else {
        value = el.value || '';
      }

      fields.push({ label: label, value: value.trim ? value.trim() : value });
    });

    return fields;
  }

  function mailtoFallback(formName, fields) {
    var lines = fields.filter(function (f) { return f.value && f.value !== '—'; })
      .map(function (f) { return f.section ? ('\n== ' + f.label + ' ==') : (f.label + ': ' + f.value); });
    window.location.href = 'mailto:' + CONTACT +
      '?subject=' + encodeURIComponent(formName) +
      '&body=' + encodeURIComponent(lines.join('\n'));
  }

  function init() {
    var form = document.getElementById('abfform');
    if (!form) return;

    var card = document.getElementById('formcard');
    var status = document.getElementById('status');
    var btn = document.getElementById('submitbtn');
    var formName = form.getAttribute('data-form') || 'Form submission';
    var busy = false;

    function setStatus(msg, kind) {
      status.className = 'formstatus show ' + (kind || '');
      status.textContent = msg;
    }

    function succeed() {
      card.innerHTML = window.__DONE__;
      card.scrollIntoView({ block: 'start', behavior: 'smooth' });
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (busy) return;

      // Dates are three selects: all or nothing.
      var dates = form.querySelectorAll('[data-date]');
      for (var i = 0; i < dates.length; i++) {
        var sels = dates[i].querySelectorAll('select');
        var filled = 0;
        for (var j = 0; j < sels.length; j++) if (sels[j].value) filled++;
        if (filled && filled < sels.length) {
          dates[i].classList.add('invalid');
          setStatus('Please choose a full date — month, day and year.', 'err');
          dates[i].scrollIntoView({ block: 'center', behavior: 'smooth' });
          return;
        }
        dates[i].classList.remove('invalid');
      }

      var fields = collect(form);
      var hp = form.querySelector('input[name="website"]');

      if (!ENDPOINT) {
        setStatus('Opening your email app with the answers filled in…', 'pending');
        mailtoFallback(formName, fields);
        return;
      }

      busy = true;
      btn.disabled = true;
      setStatus('Sending…', 'pending');

      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify({
          form: formName,
          origin: window.location.origin,
          website: hp ? hp.value : '',
          fields: fields
        })
      }).then(function (r) {
        return r.json().catch(function () { return { ok: r.ok }; });
      }).then(function (res) {
        if (!res || !res.ok) throw new Error(res && res.error ? res.error : 'rejected');
        succeed();
      }).catch(function () {
        setStatus("That didn't go through — opening your email app instead so nothing is lost.", 'err');
        mailtoFallback(formName, fields);
      }).then(function () {
        busy = false;
        btn.disabled = false;
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

(function () {
  'use strict';

  // The homepage runtime replaces documentElement after this asset loads. Keep
  // one document-level observer alive long enough to update either that
  // replacement DOM or an ordinary static page.
  if (window.__abfClassTimeLoaded) return;
  window.__abfClassTimeLoaded = true;

  var ARIZONA_ZONE = 'America/Phoenix';
  var CENTRAL_ZONE = 'America/Chicago';
  var FALLBACK = '11:00 a.m. CST / 12:00 p.m. CDT (Central time)';

  function partsFor(date, zone, options) {
    var values = {};
    new Intl.DateTimeFormat('en-US', Object.assign({ timeZone: zone }, options))
      .formatToParts(date)
      .forEach(function (part) {
        if (part.type !== 'literal') values[part.type] = part.value;
      });
    return values;
  }

  function nextFridayInstant(now) {
    var arizona = partsFor(now, ARIZONA_ZONE, {
      weekday: 'short', year: 'numeric', month: 'numeric', day: 'numeric',
      hour: 'numeric', hourCycle: 'h23'
    });
    var weekday = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(arizona.weekday);
    if (weekday < 0) throw new Error('Unsupported Arizona weekday');

    var daysUntilFriday = (5 - weekday + 7) % 7;
    if (daysUntilFriday === 0 && Number(arizona.hour) >= 10) daysUntilFriday = 7;

    // Phoenix stays at UTC-07:00 year-round, so 10:00 Arizona is always 17:00Z.
    return new Date(Date.UTC(
      Number(arizona.year), Number(arizona.month) - 1,
      Number(arizona.day) + daysUntilFriday, 17, 0, 0
    ));
  }

  function centralLabel(now) {
    var central = partsFor(nextFridayInstant(now), CENTRAL_ZONE, {
      hour: 'numeric', minute: '2-digit', hour12: true, timeZoneName: 'short'
    });
    var period = central.dayPeriod === 'AM' ? 'a.m.' : 'p.m.';
    return central.hour + ':' + central.minute + ' ' + period + ' ' +
      central.timeZoneName + ' (Central time)';
  }

  function update() {
    var nodes = document.querySelectorAll('[data-central-class-time]');
    if (!nodes.length) return false;

    var label = FALLBACK;
    try {
      label = centralLabel(new Date());
    } catch (error) {
      // The explicit CST/CDT fallback remains seasonally correct even if an old
      // browser lacks Intl time-zone support.
    }
    for (var i = 0; i < nodes.length; i++) {
      // Avoid retriggering the MutationObserver when the rendered value is
      // already current. Unconditional textContent writes create a microtask
      // loop and can starve the page's load/render work.
      if (nodes[i].textContent !== label) nodes[i].textContent = label;
    }
    return true;
  }

  var observer = new MutationObserver(update);
  observer.observe(document, { childList: true, subtree: true });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', update, { once: true });
  } else {
    update();
  }

  // The bundle swap is immediate; this prevents a permanent observer if the
  // generated runtime ever fails before producing the class-time element.
  window.setTimeout(function () {
    update();
    observer.disconnect();
  }, 10000);
})();

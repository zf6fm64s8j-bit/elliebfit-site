#!/usr/bin/env python3
"""Serve an isolated localhost-only review copy without external submissions/tracking."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, unquote

GUARD = r'''<script>
(function () {
  function block(event) { event.preventDefault(); event.stopImmediatePropagation(); }
  window.addEventListener('submit', block, true);
  window.addEventListener('click', function (event) {
    var target = event.target.closest && event.target.closest('a,button,input');
    if (!target) return;
    if ((target.href && (/^(mailto:|tel:)/.test(target.href) || /^https?:\/\/docs\.google\.com\/forms\//.test(target.href))) ||
        target.id === 'abf-send-request' || target.dataset.abfAction === 'send-request' || target.type === 'submit') block(event);
  }, true);
  function label() {
    if (!document.body || !document.querySelector('main,[role="main"],#dc-root')) return;
    if (document.getElementById('abf-local-preview-badge')) return;
    var badge = document.createElement('div');
    badge.id = 'abf-local-preview-badge';
    badge.textContent = 'Local review preview · inquiries disabled';
    badge.style.cssText = 'position:fixed;bottom:8px;right:8px;z-index:2147483647;background:#20342E;color:white;padding:8px 12px;border-radius:6px;font:12px sans-serif;max-width:90vw';
    document.body.appendChild(badge);

  }
  var observer = new MutationObserver(label);
  observer.observe(document, {childList:true,subtree:true});
  label();
})();
</script>'''


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy',
                         "default-src 'self' data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:; "
                         "style-src 'self' 'unsafe-inline'; connect-src 'self'; "
                         "form-action 'none'; object-src 'none'; base-uri 'self'")
        super().end_headers()

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if any(part.startswith('.') for part in Path(unquote(urlsplit(self.path).path)).parts):
            self.send_error(404)
            return None
        if path.is_dir():
            parsed = urlsplit(self.path)
            if not parsed.path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', urlunsplit(('', '', parsed.path + '/', parsed.query, '')))
                self.end_headers()
                return None
            path = path / 'index.html'
            if not path.is_file():
                self.send_error(404)
                return None
        if path.is_file() and path.suffix == '.html':
            data = path.read_text(encoding='utf-8')
            data = data.replace('<head>', '<head>' + GUARD, 1)
            payload = data.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            return BytesIO(payload)
        return super().send_head()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    directory = args.directory.resolve(strict=True)
    handler = partial(PreviewHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    print(f'Local preview: http://127.0.0.1:{args.port}/ (external requests blocked)', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Render a draft page through an aem-boilerplate repo and screenshot one block.

Serves the repo the way `aem up --html-folder drafts` would (no AEM CLI or network
needed): /drafts/<page> is the drafts/<page>.plain.html file wrapped in head.html,
code is served straight from the repo, and Section Metadata is turned into section
classes / data attributes the way the Edge Delivery backend does.

Usage:
  python preview_block.py --repo <repo> --page drafts/<name>.plain.html \
      --block <name> --out <dir> [--widths 375,768,1280]

Writes to <out>:
  <block>-<width>.png        the section holding the first instance of the block
  <block>-<width>-<n>.png    every section holding an instance (n = 0, 1, ...)
  <block>-<width>-full.png   the whole page
  report.json                per width: decorated?, console errors, failed requests,
                             horizontal overflow in px

Needs Playwright with Chromium:
  pip install playwright beautifulsoup4 && playwright install chromium
"""
import argparse
import functools
import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit('Playwright is missing: pip install playwright && playwright install chromium')
try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit('BeautifulSoup is missing: pip install beautifulsoup4')


def apply_section_metadata(html):
    """Mimic the backend: Section Metadata -> classes (Style) and data-* attributes."""
    soup = BeautifulSoup(html, 'html.parser')
    for meta in soup.select('div.section-metadata'):
        section = meta.parent
        for row in meta.find_all('div', recursive=False):
            cells = row.find_all('div', recursive=False)
            if len(cells) < 2:
                continue
            key = cells[0].get_text(strip=True).lower().replace(' ', '-')
            value = cells[1].get_text(strip=True)
            if key == 'style':
                styles = [s.strip().lower().replace(' ', '-') for s in value.split(',') if s.strip()]
                section['class'] = section.get('class', []) + styles
            elif key:
                section[f'data-{key}'] = value
        meta.decompose()
    return str(soup)


def make_handler(repo, head):
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send_html(self, body, status=200):
            data = body.encode()
            self.send_response(status)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            path = urlparse(self.path).path
            # pages: /drafts/foo -> drafts/foo.plain.html wrapped like a real page
            if '.' not in os.path.basename(path):
                plain = os.path.join(repo, path.strip('/') + '.plain.html')
                if path.endswith('/'):
                    plain = os.path.join(repo, path.strip('/'), 'index.plain.html')
                if os.path.isfile(plain):
                    with open(plain, encoding='utf-8') as f:
                        main = apply_section_metadata(f.read())
                    return self.send_html(
                        '<!doctype html><html><head><title>Block preview</title>'
                        f'{head}</head><body><header></header><main>{main}</main>'
                        '<footer></footer></body></html>')
            # header/footer fragments: serve the repo's if present, else an empty stub
            if path in ('/nav.plain.html', '/footer.plain.html') and not os.path.isfile(
                    os.path.join(repo, path.lstrip('/'))):
                return self.send_html('<div><p></p></div>')
            return super().do_GET()

    return functools.partial(Handler, directory=repo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--repo', required=True, help='aem-boilerplate checkout')
    ap.add_argument('--page', required=True, help='e.g. drafts/my-block.plain.html')
    ap.add_argument('--block', required=True, help='block name, e.g. my-block')
    ap.add_argument('--out', required=True, help='output directory')
    ap.add_argument('--widths', default='375,768,1280')
    ap.add_argument('--height', type=int, default=900)
    a = ap.parse_args()

    repo = os.path.abspath(a.repo)
    for needed in ('head.html', 'scripts/aem.js'):
        if not os.path.isfile(os.path.join(repo, needed)):
            sys.exit(f'{repo} does not look like an aem-boilerplate repo (no {needed})')
    if not os.path.isfile(os.path.join(repo, a.page)):
        sys.exit(f'page not found: {a.page}')
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(repo, 'head.html'), encoding='utf-8') as f:
        head = f.read()

    server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(repo, head))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    page_path = '/' + a.page.replace('\\', '/').lstrip('/').removesuffix('.plain.html')
    url = f'http://127.0.0.1:{server.server_port}{page_path}'

    report = {'url': page_path, 'block': a.block, 'widths': {}}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in [int(w) for w in a.widths.split(',')]:
            page = browser.new_page(viewport={'width': width, 'height': a.height})
            errors, failed = [], []
            page.on('console', lambda m, e=errors: m.type == 'error' and e.append(m.text))
            page.on('pageerror', lambda exc, e=errors: e.append(str(exc)))
            page.on('requestfailed', lambda r, f=failed: f.append(f'failed {r.url}'))
            page.on('response', lambda r, f=failed: r.status >= 400 and f.append(f'{r.status} {r.url}'))
            page.goto(url, wait_until='networkidle')
            # scroll through so lazy sections load, then back to the top
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(800)
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(400)
            info = page.evaluate(
                """(name) => {
                  const blocks = [...document.querySelectorAll(`main .${name}`)];
                  return {
                    instances: blocks.length,
                    decorated: blocks.length > 0
                      && blocks.every((b) => b.dataset.blockStatus === 'loaded'),
                    classes: blocks.map((b) => b.className),
                    overflow: document.documentElement.scrollWidth - window.innerWidth,
                  };
                }""", a.block)
            page.screenshot(path=os.path.join(a.out, f'{a.block}-{width}-full.png'), full_page=True)
            sections = page.query_selector_all(f'main > .section:has(.{a.block})')
            for i, section in enumerate(sections):
                section.screenshot(path=os.path.join(a.out, f'{a.block}-{width}-{i}.png'))
                if i == 0:
                    section.screenshot(path=os.path.join(a.out, f'{a.block}-{width}.png'))
            report['widths'][width] = {**info, 'console_errors': errors, 'failed_requests': failed}
            page.close()
        browser.close()
    server.shutdown()

    with open(os.path.join(a.out, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    ok = True
    for width, r in report['widths'].items():
        problems = []
        if not r['decorated']:
            problems.append('NOT DECORATED' if r['instances'] else 'BLOCK NOT FOUND')
        if r['overflow'] > 0:
            problems.append(f"overflow {r['overflow']}px")
        if r['console_errors']:
            problems.append(f"{len(r['console_errors'])} console error(s)")
        if r['failed_requests']:
            problems.append(f"{len(r['failed_requests'])} failed request(s)")
        ok = ok and not problems
        print(f"{width}px: {r['instances']} instance(s), " + (', '.join(problems) or 'ok'))
    print(f"screenshots and report.json in {a.out}")
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()

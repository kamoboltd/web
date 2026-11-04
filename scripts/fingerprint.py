# -*- coding: utf-8 -*-
"""Stamp a content hash onto styles.css and main.js in every page.

Cloudflare caches CSS and JS for four hours but HTML for ten seconds, so a
deploy that changes the stylesheet will otherwise serve new HTML against the
old CSS. The query string changes only when the asset bytes change.

Run this on any deploy that touches styles.css or main.js.
"""
import hashlib, io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sig(name):
    with io.open(os.path.join(ROOT, name), "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]

css_v, js_v = sig("styles.css"), sig("main.js")
print("styles.css -> %s   main.js -> %s" % (css_v, js_v))

# Every page, not a hand-maintained list. og-card.html is standalone artwork.
pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
         if os.path.basename(os.path.dirname(p)) != "assets"]

CSS = re.compile(r'href="(/?(?:\.\./)*styles\.css)(\?v=[0-9a-f]+)?"')
JS  = re.compile(r'src="(/?(?:\.\./)*main\.js)(\?v=[0-9a-f]+)?"')

changed, stamped, missing = 0, 0, []
for f in pages:
    s = o = io.open(f, encoding="utf-8").read()
    s, nc = CSS.subn(lambda m: 'href="%s?v=%s"' % (m.group(1), css_v), s)
    s, nj = JS.subn(lambda m: 'src="%s?v=%s"' % (m.group(1), js_v), s)
    rel = os.path.relpath(f, ROOT).replace("\\", "/")
    if not nc:
        missing.append(rel)
    stamped += nc
    if s != o:
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        changed += 1

print("stamped %d stylesheet refs across %d pages (%d rewritten)"
      % (stamped, len(pages), changed))
if missing:
    print("ABORT: no stylesheet link found in:")
    for m in missing:
        print("   ", m)
    sys.exit(1)

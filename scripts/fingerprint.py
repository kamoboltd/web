# -*- coding: utf-8 -*-
"""Stamp a content hash onto every static asset referenced by a page.

Cloudflare caches HTML for ten seconds but assets for four hours at the browser
and twenty-four at the edge (max-age=14400, s-maxage=86400). Any asset without
a cache-busting query therefore keeps serving its old bytes long after a deploy.

This bit twice:

  4 Nov  a brand pass went live as new HTML against a four-hour-old stylesheet
         and rendered unstyled.
  5 Nov  the rebuilt flat logo was deployed, and kamobo.co.uk carried on
         serving the old gradient mark from the edge for 23 hours
         (cf-cache-status: HIT, Age: 83061). Nobody saw the new brand.

The first fix only covered styles.css and main.js, which is why the second
happened. This version stamps everything under /assets/ as well, so images,
icons and logos cannot go stale either.

Run it last, after any page generation. It exits non-zero if a page has no
stylesheet link, which is how a page that lost its <head> would get caught.
"""
import hashlib, io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# href="/x" or src="/x", with an optional existing ?v=; the query is dropped
# and rewritten so repeated runs stay idempotent.
REF = re.compile(r'((?:href|src)=")(/(?:assets/[^"?]+|styles\.css|main\.js))(\?v=[0-9a-f]+)?(")')

_cache = {}


def sig(path):
    if path not in _cache:
        full = os.path.join(ROOT, path.lstrip("/").replace("/", os.sep))
        if not os.path.exists(full):
            _cache[path] = None
        else:
            with io.open(full, "rb") as fh:
                _cache[path] = hashlib.sha1(fh.read()).hexdigest()[:8]
    return _cache[path]


pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
         if os.path.basename(os.path.dirname(p)) != "assets"]

changed, stamped, missing, no_css = 0, 0, set(), []
for f in pages:
    s = o = io.open(f, encoding="utf-8").read()

    def stamp(m):
        global stamped
        v = sig(m.group(2))
        if v is None:
            missing.add(m.group(2))
            return m.group(0)
        stamped += 1
        return "%s%s?v=%s%s" % (m.group(1), m.group(2), v, m.group(4))

    s = REF.sub(stamp, s)
    if "styles.css?v=" not in s:
        no_css.append(os.path.relpath(f, ROOT).replace("\\", "/"))
    if s != o:
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        changed += 1

print("stamped %d references across %d pages (%d rewritten)" % (stamped, len(pages), changed))
for name in ("styles.css", "main.js", "assets/logo.svg", "assets/favicon.svg"):
    v = sig("/" + name)
    if v:
        print("   %-22s %s" % (name, v))

if missing:
    print("WARNING: referenced but not on disk:")
    for m in sorted(missing):
        print("   ", m)
if no_css:
    print("ABORT: no stylesheet link found in:")
    for m in no_css:
        print("   ", m)
    sys.exit(1)

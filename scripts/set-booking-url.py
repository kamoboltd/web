# -*- coding: utf-8 -*-
"""Point every "Book a call" button at a booking calendar, or back at email.

Every booking call to action on the site carries a bare `data-book` attribute.
Nothing else does, so swapping calendar providers, or reverting to email, is
one command rather than an edit across 28 pages.

    python scripts/set-booking-url.py https://cal.com/james/20min
    python scripts/set-booking-url.py --mailto        # revert
    python scripts/set-booking-url.py --status        # show current target

A real URL also gets target="_blank" rel="noopener", because the calendar is
somebody else's site; a mailto must not, or the browser opens a blank tab
alongside the mail client.

Run scripts/protect-email.py and scripts/fingerprint.py after this, in that
order. protect-email.py is what keeps a mailto target out of Cloudflare's
rewriter; see the README.
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAILTO = ("mailto:hello@kamobo.co.uk?subject=Book%20a%20call"
          "&body=Rough%20idea%20of%20the%20problem%3A%0A%0A"
          "When%20suits%20for%2020%20minutes%3A%0A")

# <a ...data-book... href="..."> with the attributes in any order.
TAG = re.compile(r'<a\b(?=[^>]*\bdata-book\b)[^>]*>')
HREF = re.compile(r'\shref="[^"]*"')
REL = re.compile(r'\s(?:target|rel)="[^"]*"')

def usage():
    print(__doc__)
    sys.exit(2)

if len(sys.argv) != 2:
    usage()
arg = sys.argv[1]

pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
         if os.path.basename(os.path.dirname(p)) != "assets"]

if arg == "--status":
    seen = {}
    for f in pages:
        for tag in TAG.findall(io.open(f, encoding="utf-8").read()):
            m = HREF.search(tag)
            href = m.group(0)[7:-1] if m else "(none)"
            seen[href] = seen.get(href, 0) + 1
    if not seen:
        print("no booking links found: is data-book still on the buttons?")
        sys.exit(1)
    for href, n in sorted(seen.items(), key=lambda kv: -kv[1]):
        print("%4d  %s" % (n, href[:96]))
    sys.exit(0)

if arg == "--mailto":
    target, external = MAILTO, False
elif arg.startswith("https://"):
    target, external = arg, True
else:
    print("ABORT: pass an https:// URL, or --mailto, or --status")
    usage()

extra = ' target="_blank" rel="noopener"' if external else ""

def rewrite(m):
    tag = REL.sub("", HREF.sub("", m.group(0)))
    return tag[:-1].rstrip() + ' href="%s"%s>' % (target, extra)

changed = total = 0
for f in pages:
    s = o = io.open(f, encoding="utf-8").read()
    s, n = TAG.subn(rewrite, s)
    total += n
    if s != o:
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        changed += 1

if not total:
    print("ABORT: no data-book links found, nothing was changed")
    sys.exit(1)
print("pointed %d booking links in %d pages at %s" % (total, changed, target[:70]))
print("now run: python scripts/protect-email.py && python scripts/fingerprint.py")

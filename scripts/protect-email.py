# -*- coding: utf-8 -*-
"""Keep Cloudflare's Email Address Obfuscation off our contact links.

The zone has Scrape Shield's Email Address Obfuscation switched on. It rewrites
every href="mailto:..." to /cdn-cgi/l/email-protection and replaces the visible
address with "[email protected]", so the contact page's own heading rendered as
that string and every call to action on the site only worked if Cloudflare's
decode script ran. The documented <!--email_off--> opt-out does not work here:
the comment is stripped from the response without being honoured.

Measured on a probe page against the live zone (2026-11-04):

    mailto:hello@kamobo.co.uk              rewritten
    mailto:hello&#64;kamobo.co.uk          rewritten
    &#109;ailto:hello&#64;kamobo.co.uk     SURVIVES
    mailto:hello&#x40;kamobo&#x2E;co&#x2E;uk   rewritten
    text  hello@kamobo.co.uk               rewritten
    text  hello&#64;kamobo.co.uk           SURVIVES

So encode the scheme's first letter and the @. The HTML parser resolves
character references in attribute values and text before anything uses them,
so links work natively with JavaScript disabled. Cloudflare's scanner misses
them.

The proper fix is to turn Email Address Obfuscation off under Scrape Shield in
the Cloudflare dashboard. If that happens, this script becomes a no-op worth
keeping, because it is idempotent.

Run it after any page generation, before scripts/fingerprint.py.
"""
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDR = "hello@kamobo.co.uk"
SAFE = "hello&#64;kamobo.co.uk"

# Never rewrite inside <script>: character references are not resolved there,
# so encoding an address in JSON-LD would corrupt the JSON.
SCRIPT = re.compile(r"(<script\b.*?</script>)", re.S | re.I)
DEAD = re.compile(r"<!--/?email_off-->")

def protect(chunk):
    # href="mailto:... -> href="&#109;ailto:...
    chunk = re.sub(r'(href=")mailto:', r"\1&#109;ailto:", chunk)
    # the address itself, wherever it still appears literally
    chunk = chunk.replace(ADDR, SAFE)
    return chunk

pages = [p for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
         if os.path.basename(os.path.dirname(p)) != "assets"]

changed = 0
left = []
for f in pages:
    s = o = io.open(f, encoding="utf-8").read()
    s = DEAD.sub("", s)
    s = "".join(part if SCRIPT.match(part) else protect(part)
                for part in SCRIPT.split(s))
    if s != o:
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        changed += 1
    # anything still exposed outside a script block is a miss
    bare = sum(part.count(ADDR) + len(re.findall(r'href="mailto:', part))
               for part in SCRIPT.split(s) if not SCRIPT.match(part))
    if bare:
        left.append((os.path.relpath(f, ROOT).replace("\\", "/"), bare))

print("protected addresses in %d of %d pages" % (changed, len(pages)))
if left:
    print("ABORT: unprotected addresses remain:")
    for rel, n in left:
        print("   %s (%d)" % (rel, n))
    sys.exit(1)

# -*- coding: utf-8 -*-
import io, re, glob, os, subprocess

root = r"E:\GitHub\kamobo\web"
files = [os.path.join(root, "index.html"), os.path.join(root, "services", "index.html")] + \
        sorted(glob.glob(os.path.join(root, "services", "*", "index.html")))
files = sorted(set(files))

# Fingerprint from the current content of each asset, so the query only changes
# when the asset does.
import hashlib
def sig(name):
    b = io.open(os.path.join(root, name), "rb").read()
    return hashlib.sha1(b).hexdigest()[:8]

css_v, js_v = sig("styles.css"), sig("main.js")
print("styles.css ->", css_v, " main.js ->", js_v)

n = 0
for f in files:
    s = io.open(f, encoding="utf-8").read()
    orig = s
    # stylesheet href, absolute or relative, with or without an existing query
    s = re.sub(r'href="(/?styles\.css)(\?v=[0-9a-f]+)?"', r'href="\1?v=' + css_v + '"', s)
    s = re.sub(r'src="(/?main\.js)(\?v=[0-9a-f]+)?"', r'src="\1?v=' + js_v + '"', s)
    if s != orig:
        io.open(f, "w", encoding="utf-8", newline="\n").write(s)
        n += 1

print("fingerprinted in", n, "files")
for f in files[:2]:
    for line in io.open(f, encoding="utf-8"):
        if "styles.css" in line or "main.js" in line:
            print("  ", os.path.relpath(f, root), "|", line.strip()[:110])

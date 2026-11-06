"""Tell Bing, Yandex, Seznam and Naver which pages changed, via IndexNow.

Bing's index feeds ChatGPT search and Copilot, so this is the quickest way to
get a new or reworded page in front of them. Google does not use IndexNow;
it reads sitemap.xml.

The key is the 32-character hex file in the site root (<key>.txt holding the
key itself). Run after a deploy has gone live, never before: the engines fetch
the pages straight away.

    python -I scripts/indexnow.py                 # pages whose lastmod is today
    python -I scripts/indexnow.py --since 2026-11-01
    python -I scripts/indexnow.py --all
"""
import datetime, glob, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "kamobo.co.uk"


def main(argv):
    keys = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "*.txt"))
            if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(p))]
    if len(keys) != 1:
        raise SystemExit("expected exactly one <key>.txt in the site root, found %d" % len(keys))
    key = keys[0]
    sitemap = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    entries = re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", sitemap)
    if "--all" in argv:
        urls = [u for u, _ in entries]
    else:
        since = argv[argv.index("--since") + 1] if "--since" in argv else datetime.date.today().isoformat()
        urls = [u for u, d in entries if d >= since]
    if not urls:
        print("nothing changed since then; pass --since or --all")
        return
    body = json.dumps({"host": HOST, "key": key,
                       "keyLocation": "https://%s/%s.txt" % (HOST, key),
                       "urlList": urls}).encode("utf-8")
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow: HTTP %d for %d URLs" % (r.status, len(urls)))
        for u in urls:
            print("  " + u)


if __name__ == "__main__":
    main(sys.argv[1:])

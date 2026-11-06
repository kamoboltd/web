# -*- coding: utf-8 -*-
"""Machine-readable layer for kamobo.co.uk: JSON-LD, sitemap, robots, llms.txt.

Added 6 November 2026. Before this the site carried no structured data at all,
no llms.txt, and a hand-written sitemap that had already drifted (two pages
missing, no lastmod). The doctrine follows the volorai SEO brief
(volorai-wt/infra-k8s-risk/apps/volorai-site/SEO_CONVERSION_BRIEF.md): welcome
LLM crawlers, publish llms.txt, emit per-page-type JSON-LD, and only mark up
FAQs a visitor can actually see.

Everything here is generated from the pages themselves on every build, so it
cannot drift from what the site says. build.py calls jsonld_for() from page()
and write_all() once every page exists.
"""
import datetime, hashlib, html, io, json, os, re, subprocess

SITE = "https://kamobo.co.uk"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORG_ID = SITE + "/#org"
PERSON_ID = SITE + "/#james"
WEBSITE_ID = SITE + "/#website"
BOOK = "https://cal.com/kamobo/30min"
EMAIL = "hello@kamobo.co.uk"
COMPANY_NO = "16579058"
COMPANIES_HOUSE = "https://find-and-update.company-information.service.gov.uk/company/" + COMPANY_NO

ORG_DESCRIPTION = (
    "Kamobo is a UK-based Azure consultancy for platform engineering, AI and data platforms. "
    "It designs, builds and recovers Azure estates as code, in the client's own tenant, and every "
    "engagement is led hands-on by the engineer doing the work.")

# What the firm can be asked about. Each item is backed by delivered work in
# freelance/proposals/_facts-pack.md; nothing here may be added without that.
KNOWS_ABOUT = [
    "Microsoft Azure", "Azure landing zones", "Terraform", "Ansible", "Azure DevOps",
    "GitHub Actions", "CI/CD", "GitOps", "Kubernetes", "Docker", "Azure cost optimisation",
    "FinOps", "Azure Synapse Analytics", "Azure Data Factory", "Azure Databricks",
    "Microsoft Dataverse", "Azure Synapse Link for Dataverse", "Link to Microsoft Fabric",
    "Microsoft Fabric", "Dynamics 365 data integration", "Private LLM deployment",
    "Retrieval-augmented generation", "vLLM", "AI agents", "Anthropic Claude",
    "PostgreSQL", "pgvector", "Redis", "RabbitMQ", "NGINX", "Load testing with K6",
    "Application performance troubleshooting", "Entra ID", "ISO 27001",
]

TOPIC_OF = {  # breadcrumb label for each top-level section
    "services": ("What we do", "/services/"), "work": ("Our work", "/work/"),
    "insights": ("Insights", "/insights/"), "sectors": ("Sectors", "/sectors/"),
}

MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"], 1)}

FAQ_RE = re.compile(r'<details class="faq-item"><summary>(.*?)</summary>(.*?)</details>', re.S)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S)
DATE_RE = re.compile(r'class="article-meta">.*?(\d{1,2}) (January|February|March|April|May|June|July|'
                     r'August|September|October|November|December) (\d{4})', re.S)


def text(fragment):
    """Visible text of an HTML fragment, entities decoded, whitespace collapsed."""
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def strip_title(title):
    return html.unescape(re.sub(r"\s*\|\s*Kamobo\s*$", "", title)).strip()


def asset_version(rel):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    with io.open(p, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


def og_image():
    return "%s/assets/og-card.png?v=%s" % (SITE, asset_version("assets/og-card.png"))


# ------------------------------------------------------------------ entities

def organisation(services):
    return {
        "@type": ["ProfessionalService", "Organization"],
        "@id": ORG_ID,
        "name": "Kamobo",
        "legalName": "Kamobo Ltd",
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo-512.png", "width": 512, "height": 512},
        "image": og_image(),
        "description": ORG_DESCRIPTION,
        "slogan": "UK-based Azure consultancy. Platform engineering, AI and data platforms.",
        "email": EMAIL,
        "identifier": {"@type": "PropertyValue", "propertyID": "Companies House", "value": COMPANY_NO},
        "address": {"@type": "PostalAddress", "streetAddress": "124-128 City Road",
                    "addressLocality": "London", "postalCode": "EC1V 2NX", "addressCountry": "GB"},
        "areaServed": [{"@type": "Country", "name": "United Kingdom"}, "Worldwide (remote)"],
        "founder": {"@id": PERSON_ID},
        "employee": {"@id": PERSON_ID},
        "knowsAbout": KNOWS_ABOUT,
        "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "email": EMAIL,
                          "url": BOOK, "availableLanguage": "en-GB",
                          "areaServed": ["GB", "Worldwide"]}],
        "sameAs": [COMPANIES_HOUSE],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Azure consultancy services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": name,
                                                   "url": "%s/services/%s/" % (SITE, slug)}}
                for slug, name, _d in services] + [
                {"@type": "Offer", "name": "The Azure Review", "url": SITE + "/azure-review/",
                 "price": "2500", "priceCurrency": "GBP",
                 "itemOffered": {"@type": "Service", "name": "The Azure Review",
                                 "url": SITE + "/azure-review/"}}],
        },
    }


def person():
    return {
        "@type": "Person", "@id": PERSON_ID, "name": "James Dettmer", "jobTitle": "Principal",
        "worksFor": {"@id": ORG_ID}, "url": SITE + "/about/",
        "description": ("Principal at Kamobo Ltd. Eighteen years in infrastructure, cloud and "
                        "platform engineering: Azure, Terraform, DevOps, data platforms and "
                        "private AI platforms."),
        "knowsAbout": KNOWS_ABOUT,
    }


def website():
    return {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE + "/", "name": "Kamobo",
            "publisher": {"@id": ORG_ID}, "inLanguage": "en-GB"}


def breadcrumbs(path, name):
    items = [("Home", "/")]
    parts = [p for p in path.split("/") if p]
    if parts:
        if parts[0] in TOPIC_OF and len(parts) > 1:
            items.append(TOPIC_OF[parts[0]])
        items.append((name, path))
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p}
        for i, (n, p) in enumerate(items)]}


def faqs(body):
    """Only FAQs a visitor can see on the page. Phantom FAQ markup is spam."""
    out = []
    for q, a in FAQ_RE.findall(body):
        q, a = text(q), text(a)
        if q and a:
            out.append({"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}})
    return out


def post_date(body):
    m = DATE_RE.search(body)
    if not m:
        return None
    d, mon, y = m.groups()
    return "%s-%02d-%02d" % (y, MONTHS[mon], int(d))


def jsonld_for(path, title, desc, body, services, lastmod=None):
    """The @graph for one page, chosen by page type."""
    url = SITE + path
    h1 = H1_RE.search(body)
    name = text(h1.group(1)) if h1 else strip_title(title)
    desc = html.unescape(desc)
    parts = [p for p in path.split("/") if p]
    graph = [organisation(services), person(), website(), breadcrumbs(path, name)]

    page = {"@type": "WebPage", "@id": url + "#page", "url": url, "name": strip_title(title),
            "description": desc, "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": ORG_ID},
            "inLanguage": "en-GB", "primaryImageOfPage": og_image()}
    if lastmod:
        page["dateModified"] = lastmod

    if path == "/":
        page["@type"] = "WebPage"
        page["mainEntity"] = {"@id": ORG_ID}
    elif path == "/about/":
        page["@type"] = "AboutPage"
        page["mainEntity"] = {"@id": ORG_ID}
    elif path == "/contact/":
        page["@type"] = "ContactPage"
    elif path in ("/insights/", "/work/", "/services/", "/sectors/"):
        page["@type"] = "CollectionPage"
    elif parts and parts[0] == "services" and len(parts) == 2:
        graph.append({"@type": "Service", "@id": url + "#service", "name": name, "url": url,
                      "description": desc, "provider": {"@id": ORG_ID},
                      "areaServed": [{"@type": "Country", "name": "United Kingdom"},
                                     "Worldwide (remote)"],
                      "serviceType": strip_title(title)})
        page["mainEntity"] = {"@id": url + "#service"}
    elif path == "/azure-review/":
        graph.append({"@type": "Service", "@id": url + "#service", "name": "The Azure Review",
                      "url": url, "description": desc, "provider": {"@id": ORG_ID},
                      "offers": {"@type": "Offer", "price": "2500", "priceCurrency": "GBP",
                                 "url": url}})
        page["mainEntity"] = {"@id": url + "#service"}
    elif parts and parts[0] in ("insights", "work") and len(parts) == 2:
        published = post_date(body) or lastmod
        art = {"@type": "BlogPosting" if parts[0] == "insights" else "Article",
               "@id": url + "#article", "headline": name[:110], "description": desc,
               "url": url, "mainEntityOfPage": {"@id": url + "#page"},
               "author": {"@id": PERSON_ID} if parts[0] == "insights" else {"@id": ORG_ID},
               "publisher": {"@id": ORG_ID}, "image": og_image(), "inLanguage": "en-GB"}
        if published:
            art["datePublished"] = published
            art["dateModified"] = max(published, lastmod or published)
        graph.append(art)
        page["mainEntity"] = {"@id": url + "#article"}

    graph.insert(0, page)
    qa = faqs(body)
    if qa:
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": qa,
                      "isPartOf": {"@id": url + "#page"}})
    return {"@context": "https://schema.org", "@graph": graph}


def jsonld_tag(data):
    # Escape "</" so a stray closing tag in text can never end the script early.
    s = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return '  <script type="application/ld+json">%s</script>\n' % s


# ------------------------------------------------------------------ lastmod ledger

LEDGER = os.path.join(ROOT, "scripts", "lastmod.json")


def _git_date(rel):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return out or None
    except Exception:
        return None


def lastmod_for(path, body, ledger):
    """Date the page's visible content last changed, not the date the file was
    last rewritten. Fingerprinting rewrites every page whenever the stylesheet
    changes; that must not reset lastmod across the site."""
    digest = hashlib.sha1(text(body).encode("utf-8")).hexdigest()
    entry = ledger.get(path)
    if entry and entry["hash"] == digest:
        return entry["date"]
    rel = (path.strip("/") + "/index.html") if path != "/" else "index.html"
    if entry is None:
        date = _git_date(rel) or datetime.date.today().isoformat()
    else:
        date = datetime.date.today().isoformat()
    ledger[path] = {"hash": digest, "date": date}
    return date


def load_ledger():
    try:
        return json.load(io.open(LEDGER, encoding="utf-8"))
    except Exception:
        return {}


def save_ledger(ledger):
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(
        json.dumps(dict(sorted(ledger.items())), indent=1) + "\n")


# ------------------------------------------------------------------ site files

ROBOTS = """# Kamobo welcomes search engines and AI assistants. This file is generated by
# scripts/seo.py. If Cloudflare's managed robots.txt or "Block AI bots" is on
# for this zone, its rules are added in front of these at the edge; see README.

User-agent: *
Allow: /

# AI search, answer and assistant crawlers: allowed on purpose, so that
# assistants can describe and recommend Kamobo accurately.
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: GPTBot
User-agent: Claude-SearchBot
User-agent: Claude-User
User-agent: ClaudeBot
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: DuckAssistBot
User-agent: CCBot
Allow: /

Sitemap: https://kamobo.co.uk/sitemap.xml
# Plain-language map for language models: https://kamobo.co.uk/llms.txt
"""


def write_sitemap(entries):
    rows = "\n".join("  <url><loc>%s%s</loc><lastmod>%s</lastmod></url>" % (SITE, p, d)
                     for p, d in sorted(entries.items(), key=lambda kv: (kv[0] != "/", kv[0])))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % rows)
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(xml)


def _md(fragment):
    """Readable markdown from a page body, for llms-full.txt."""
    f = re.sub(r'<section class="cta".*?</section>', "", fragment, flags=re.S)
    f = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", f, flags=re.S)
    f = re.sub(r"<h1[^>]*>(.*?)</h1>", lambda m: "\n# " + text(m.group(1)) + "\n", f, flags=re.S)
    f = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n## " + text(m.group(1)) + "\n", f, flags=re.S)
    f = re.sub(r"<h3[^>]*>(.*?)</h3>", lambda m: "\n### " + text(m.group(1)) + "\n", f, flags=re.S)
    f = re.sub(r"<summary>(.*?)</summary>", lambda m: "\nQ: " + text(m.group(1)) + "\n", f, flags=re.S)
    f = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "\n- " + text(m.group(1)), f, flags=re.S)
    f = re.sub(r"<(p|dd|dt|tr)[^>]*>(.*?)</\1>", lambda m: "\n" + text(m.group(2)) + "\n", f, flags=re.S)
    f = text_keep_lines(f)
    return re.sub(r"\n{3,}", "\n\n", f).strip()


def text_keep_lines(f):
    f = re.sub(r"<[^>]+>", " ", f)
    f = html.unescape(f)
    return "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in f.split("\n"))


def write_llms(pages, services, studies):
    """pages: {path: (title, desc, body)}. llms.txt follows llmstxt.org."""
    def link(path):
        t, d, _b = pages[path]
        return "- [%s](%s%s): %s" % (strip_title(t), SITE, path, html.unescape(d))

    insights = sorted((p for p in pages if p.startswith("/insights/") and p != "/insights/"),
                      key=lambda p: (0 if "synapse" in p else 1, p))
    out = ["# Kamobo", "",
           "> " + ORG_DESCRIPTION, "",
           "Kamobo Ltd is registered in England and Wales (company %s). Based in Hertfordshire, "
           "working remotely across the UK and worldwide. Principal: James Dettmer, 18+ years in "
           "infrastructure, cloud and platform engineering. Contact: %s. Book a 30-minute call: %s"
           % (COMPANY_NO, EMAIL, BOOK), "",
           "Engagements: the Azure Review (fixed price, GBP 2,500, three days, read-only), project "
           "work from GBP 850 a day or fixed price, and monthly retainers from GBP 595. Clients are "
           "described anonymously on the site because most work is under NDA.", "",
           "## Services"]
    out += [link("/services/%s/" % s) for s, _n, _d in services if "/services/%s/" % s in pages]
    out += ["", "## Engagement and pricing"]
    out += [link(p) for p in ("/azure-review/", "/pricing/", "/retainers/", "/how-we-work/") if p in pages]
    out += ["", "## Case studies"]
    out += [link("/work/%s/" % s) for s, _n, _d in studies if "/work/%s/" % s in pages]
    out += ["", "## Insights"]
    out += [link(p) for p in insights]
    out += ["", "## Company"]
    out += [link(p) for p in ("/about/", "/sectors/", "/contact/") if p in pages]
    out += ["", "## Optional",
            "- [Full text of every page](%s/llms-full.txt): the same content as the pages above, as "
            "plain markdown." % SITE, ""]
    io.open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(out))

    order = ["/"] + [p for p in sorted(pages) if p not in ("/", "/privacy/")]
    full = ["# Kamobo: full site text", "", "> " + ORG_DESCRIPTION, "",
            "Source: %s. Generated from the live pages on every build." % SITE, ""]
    for p in order:
        t, d, b = pages[p]
        full += ["", "---", "", "URL: %s%s" % (SITE, p), "Title: %s" % strip_title(t), "", _md(b)]
    io.open(os.path.join(ROOT, "llms-full.txt"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(full) + "\n")


def write_all(pages, services, studies, lastmods):
    io.open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(ROBOTS)
    write_sitemap(lastmods)
    write_llms(pages, services, studies)

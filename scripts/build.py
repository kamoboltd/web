# -*- coding: utf-8 -*-
"""Rebuild the Kamobo site shell: chrome, homepage, sectors page.

Rebuilt 5 November 2026. The site kept reading as a design studio rather than a
consultancy. Measured the reference class (Equal Experts, CGI, Made Tech) and
followed their structure rather than inventing one:

  positioning sentence -> capabilities -> sectors -> proof -> how we engage
  -> clients -> insights -> contact

Pages that already hold fact-checked prose (services, case studies, insights,
about, pricing and the rest) are re-housed in the new chrome rather than
rewritten, because that prose was written against freelance/proposals/
_facts-pack.md and is the only claim set allowed.

Run:  python scripts/build.py && python scripts/protect-email.py \
      && python scripts/fingerprint.py
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOOK = ("mailto:hello@kamobo.co.uk?subject=Book%20a%20call"
        "&body=Rough%20idea%20of%20the%20problem%3A%0A%0A"
        "When%20suits%20for%2020%20minutes%3A%0A")
MAIL = "mailto:hello@kamobo.co.uk?subject=Enquiry%20via%20kamobo.co.uk"

NAV = [
    ("/services/", "What we do"),
    ("/sectors/", "Sectors"),
    ("/work/", "Our work"),
    ("/insights/", "Insights"),
    ("/pricing/", "Pricing"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
]

SERVICES = [
    ("azure-cost-optimization", "Cloud cost reduction",
     "Find the spend that is doing nothing, and stop it recurring."),
    ("azure-data-engineering", "Azure data platforms",
     "Synapse, Data Factory and Databricks, built to run efficiently."),
    ("private-llm-rag", "Private LLM and RAG",
     "Self-hosted inference for documents that cannot leave the estate."),
    ("ai-agent-development", "AI agents in production",
     "Agents that run unattended, with approval gates and logging."),
    ("terraform-azure-landing-zones", "Landing zones and Terraform",
     "Subscription vending, hub-spoke, private endpoints, policy and RBAC."),
    ("application-performance-troubleshooting", "Performance and root-cause",
     "Load testing and forensics on systems nobody left can explain."),
    ("devops-cicd-gitops", "DevOps, CI/CD and GitOps",
     "Pipelines that take minutes instead of hours, across five toolchains."),
    ("api-development", "APIs and integration",
     "Service layers, hybrid connectivity and integration that holds up."),
    ("saas-software-development", "Software and SaaS",
     "Multi-tenant products, built and operated end to end."),
]

STUDIES = [
    ("azure-bill-six-figures", "&pound;150,000 a year",
     "removed from one Azure bill, by interviewing the people who knew where the spend went."),
    ("streaming-platform-nobody-could-explain", "70% lower",
     "total cost of ownership over three years, on a streaming platform nobody could explain."),
    ("private-ai-platform-zero-trust", "Zero",
     "third-party inference calls, on a private AI platform for documents that cannot leave."),
]

# Descriptors here are the anonymised ones permitted by the facts pack. Nothing
# in this list may be made more specific without checking that file first.
SECTORS = [
    ("Financial services",
     "For a UK financial services firm, &pound;250,000 a year of Azure spend identified through "
     "zombie-resource removal, VM restructuring and reserved instances, with 15+ Azure Workbooks "
     "built for cost and performance visibility."),
    ("Energy and utilities",
     "For a European energy supplier, Synapse workspaces with self-hosted integration runtimes, "
     "Data Factory orchestration and Databricks across dev through production, in centralised "
     "Terraform modules with least-privilege networking throughout."),
    ("Professional education and training",
     "For a global professional education body, a zero-trust private LLM and RAG platform on "
     "GPU-accelerated Azure, where each use case runs on its own isolated vector store so data "
     "never crosses between them."),
    ("Media and streaming",
     "On a self-hosted media and video-streaming platform we did not build, the architecture was "
     "reverse-engineered, load tested with K6 and moved to autoscaling Azure. Total cost of "
     "ownership fell 70% over three years."),
    ("Legal and professional services",
     "For a 250-staff UK law firm, three VMware environments audited out of hours, sized and "
     "consolidated onto a single Nutanix AHV cluster alongside Azure services."),
    ("Employment and public services",
     "For a UK employment-services provider, Kubernetes and Docker Enterprise across five "
     "environments, 23 GitLab CI/CD projects, and 35 to 40% taken off the Azure bill."),
]

STATS = [
    ("18+ years", "in cloud, platform and infrastructure engineering"),
    ("&pound;150k", "a year removed from a single Azure bill"),
    ("70%", "lower total cost of ownership over three years"),
    ("18,000+", "users on an AI platform we build and operate"),
]

# The hero's second column. This was a topology diagram, which depicted nothing
# real: generic boxes labelled ingress / compute / data / cache. A client learned
# nothing from it, so it was decoration. Replaced with the offer most engagements
# actually start from, which is a conversion asset rather than an illustration.
FIGURE = '''        <aside class="hero-offer" aria-label="Where most engagements start">
          <p class="trust-label">Where most engagements start</p>
          <h2>The Azure Review</h2>
          <p>A read-only assessment of your Azure estate: what it costs, what it is running, where the risk sits, and what we would fix first. You get written findings and a priced plan.</p>
          <dl class="offer-spec">
            <div><dt>Price</dt><dd>&pound;2,500</dd></div>
            <div><dt>Duration</dt><dd>3 working days</dd></div>
            <div><dt>Access</dt><dd>Read-only</dd></div>
          </dl>
          <p class="offer-note">If you go on to have us do the work and we start within 30 days, the fee is credited in full against it.</p>
          <a class="btn btn-ghost" href="/azure-review/">What the review covers</a>
        </aside>
'''


CLIENT_LOGOS = [
    ("acca.svg", "ACCA"), ("lme.svg", "London Metal Exchange"), ("segro.png", "SEGRO"),
    ("guardian.svg", "Guardian Financial Services"), ("sefe.svg", "SEFE Energy"),
    ("ingeus.svg", "Ingeus"), ("stone-king.svg", "Stone King LLP"), ("zones.svg", "Zones UK"),
    ("glisser.svg", "Glisser"), ("is2.svg", "IS2"),
]


def clients():
    """A logo band. Every firm in the reference class carries one, and it is the
    strongest trust signal on the site. The list is duplicated because the
    marquee translates by -50%."""
    def row(hidden):
        return "\n".join(
            '            <li><img src="/assets/logos/%s" alt="%s" loading="lazy" /></li>'
            % (f, "" if hidden else n) for f, n in CLIENT_LOGOS)
    return '''
    <section class="clients" aria-label="Organisations we have worked with">
      <div class="wrap">
        <p class="trust-label">Organisations we have worked with</p>
      </div>
      <div class="marquee">
        <div class="marquee-track">
          <ul class="marquee-list">
%s
          </ul>
          <ul class="marquee-list" aria-hidden="true">
%s
          </ul>
        </div>
      </div>
    </section>
''' % (row(False), row(True))


def head(title, desc, canonical):
    return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>%s</title>
  <meta name="description" content="%s" />
  <meta name="theme-color" content="#0C1F2C" />
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml" />
  <link rel="canonical" href="https://kamobo.co.uk%s" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="%s" />
  <meta property="og:description" content="%s" />
  <meta property="og:url" content="https://kamobo.co.uk%s" />
  <meta property="og:image" content="https://kamobo.co.uk/assets/og-card.png" />
  <meta property="og:site_name" content="Kamobo" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/styles.css" />
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
''' % (title, desc, canonical, title, desc, canonical)


def header(active=""):
    links = "\n".join(
        '        <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == active else "", t)
        for h, t in NAV)
    return '''
  <header class="site-header" id="top">
    <div class="wrap header-inner">
      <a class="brand" href="/" aria-label="Kamobo home">
        <img src="/assets/logo.svg" alt="Kamobo" width="152" height="37" />
      </a>
      <nav class="nav" aria-label="Primary">
%s
      </nav>
      <p class="availability">Available now</p>
      <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </header>
''' % links


def footer():
    svc = "\n".join('          <a href="/services/%s/">%s</a>' % (s, t) for s, t, _d in SERVICES)
    return '''
  <footer class="site-footer">
    <div class="wrap footer-sitemap">
      <div>
        <p class="trust-label">What we do</p>
%s
      </div>
      <div>
        <p class="trust-label">Our work</p>
          <a href="/work/azure-bill-six-figures/">Cloud cost recovery</a>
          <a href="/work/streaming-platform-nobody-could-explain/">Platform forensics</a>
          <a href="/work/private-ai-platform-zero-trust/">Private AI platform</a>
          <a href="/work/">All case studies</a>
          <a href="/sectors/">Sectors</a>
      </div>
      <div>
        <p class="trust-label">How we work</p>
          <a href="/azure-review/">The Azure Review</a>
          <a href="/retainers/">Retainers</a>
          <a href="/pricing/">Pricing</a>
          <a href="/how-we-work/">Our approach</a>
          <a href="/insights/">Insights</a>
      </div>
      <div>
        <p class="trust-label">Company</p>
          <a href="/about/">About Kamobo</a>
          <a href="/contact/">Contact</a>
          <a href="mailto:hello@kamobo.co.uk">hello@kamobo.co.uk</a>
      </div>
      <div>
        <p class="trust-label">Legal</p>
          <a href="/privacy/">Privacy notice</a>
          <a href="/privacy/#cookies">Cookies</a>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <span>&copy; <span id="year">2026</span> Kamobo Ltd. Registered in England and Wales, company number <a href="https://find-and-update.company-information.service.gov.uk/company/16579058">16579058</a>. Registered office: 124-128 City Road, London EC1V 2NX.</span>
      <span>hello@kamobo.co.uk</span>
    </div>
  </footer>

  <script src="/main.js" defer></script>
</body>
</html>
''' % svc


CTA = '''
    <section class="cta" id="contact">
      <div class="wrap cta-inner">
        <h2>Tell us what is actually going wrong.</h2>
        <p>One email, a couple of paragraphs. We will come back with whether we can help, roughly what it would take and what it would cost. If we are not the right people for it we will say so, and point you at who is.</p>
        <div class="cta-actions">
          <a class="btn btn-primary btn-lg" data-book href="%s">Book a call</a>
          <a class="btn btn-ghost btn-lg" href="%s">Email instead</a>
        </div>
        <p class="cta-sub">No sales sequence. A reply from the engineer who would do the work.</p>
      </div>
    </section>
''' % (BOOK, MAIL)


def page(path, title, desc, body, active=""):
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" \
        else os.path.join(ROOT, "index.html")
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    html = (head(title, desc, path) + header(active) +
            '\n  <main id="main">\n' + body + CTA + "  </main>\n" + footer())
    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    return out


# ---------------------------------------------------------------- homepage

def homepage():
    svc = "\n".join(
        '          <a href="/services/%s/"><strong>%s</strong><span>%s</span></a>'
        % (s, t, d) for s, t, d in SERVICES)
    proof = "\n".join(
        '          <a href="/work/%s/"><strong>%s</strong><span>%s</span></a>'
        % (s, n, d) for s, n, d in STUDIES)
    stats = "\n".join(
        '          <div><strong>%s</strong><span>%s</span></div>' % (n, d) for n, d in STATS)
    sectors = "\n".join(
        '          <article class="sector"><h3>%s</h3><p>%s</p></article>' % (t, d)
        for t, d in SECTORS[:6])

    body = '''    <section class="hero">
      <div class="wrap">
        <div class="hero-inner">
          <div>
            <p class="kicker">UK technology consultancy</p>
            <h1>Azure, data and AI platforms, engineered to run in production.</h1>
            <p class="lede">Kamobo designs, builds and recovers the cloud platforms, data pipelines and AI systems that businesses depend on. Every engagement is led hands-on by the engineer doing the work, not handed to a delivery team you have not met.</p>
            <div class="hero-cta">
              <a class="btn btn-primary btn-lg" data-book href="%s">Book a call</a>
              <a class="btn btn-ghost btn-lg" href="/work/">See the work</a>
            </div>
          </div>
%s        </div>
        <div class="hero-meta">
%s
        </div>
      </div>
    </section>
%s
    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">What we do</p>
          <h2>Nine capabilities, one engineer accountable for each</h2>
          <p class="section-sub">Most engagements start in one of these and widen once we are in the estate and can see what is actually there.</p>
        </div>
        <div class="svc">
%s
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">Who we work with</p>
          <h2>Regulated and operationally complex estates</h2>
          <p class="section-sub">Clients are described here without naming them. We will talk about any of this work in detail on a call, under NDA where that is needed.</p>
        </div>
        <div class="sectors">
%s
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">Our work</p>
          <h2>Outcomes, with the number first</h2>
          <p class="section-sub">Three engagements written up in full, including what was tried that did not work.</p>
        </div>
        <div class="proof">
%s
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head">
          <p class="kicker">How we engage</p>
          <h2>Three ways to start</h2>
        </div>
        <div class="engage-grid">
          <article class="engage-card featured">
            <span class="engage-badge">Most common</span>
            <h3>The Azure Review</h3>
            <p>A fixed-price, read-only assessment of an Azure estate: cost, architecture, security posture and the things nobody has looked at in two years. You get a findings review and a priced plan for anything worth fixing.</p>
            <p class="engage-for">&pound;2,500 fixed. Two weeks. No access beyond read-only.</p>
          </article>
          <article class="engage-card">
            <h3>Project work</h3>
            <p>A defined piece of engineering with an outcome we both agree on up front: a landing zone, a data platform, a private LLM deployment, a migration, a performance recovery.</p>
            <p class="engage-for">From &pound;850 a day, or fixed price where the scope allows it.</p>
          </article>
          <article class="engage-card">
            <h3>Retained capacity</h3>
            <p>A standing allocation each month for the work that cannot be scoped in advance: break-fix, reviews, access and governance, and the questions that never become tickets.</p>
            <p class="engage-for">From &pound;595 a month. Three-month minimum, then thirty days' notice.</p>
          </article>
        </div>
        <p class="engage-note">Kamobo Ltd is a UK limited company, registered number 16579058. We carry our own insurance, sign your NDA and work to your change process.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="book">
          <div>
            <h2>Not sure which of those it is?</h2>
            <p>Describe the problem in a couple of paragraphs. We will tell you which one it needs.</p>
          </div>
          <a class="btn btn-primary btn-lg" data-book href="%s">Book a call</a>
        </div>
      </div>
    </section>
''' % (BOOK, FIGURE, stats, clients(), svc, sectors, proof, BOOK)

    return page("/", "Kamobo | Azure, data and AI consultancy, UK",
                "Kamobo is a UK technology consultancy. We design, build and recover Azure "
                "platforms, data pipelines and AI systems, led hands-on by the engineer doing "
                "the work.", body)


# ---------------------------------------------------------------- sectors

def sectors_page():
    # h2, not h3: these are the page's first content level, and jumping h1 -> h3
    # is the outline defect promote_headings() exists to stop.
    items = "\n".join(
        '''          <article class="case">
            <h2>%s</h2>
            <p>%s</p>
          </article>''' % (t, d) for t, d in SECTORS)
    body = '''    <section class="section service-hero">
      <div class="wrap">
        <p class="kicker">Sectors</p>
        <h1>Where this work has already been done</h1>
        <p class="section-sub">Clients are described rather than named. Every engagement below was delivered by the same engineer who would lead yours, and we will go through any of it in detail on a call.</p>
      </div>
    </section>

    <section class="section">
      <div class="wrap">
        <div class="cases">
%s
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head">
          <h2>What these estates have in common</h2>
          <p class="section-sub">The sector matters less than the shape of the problem.</p>
        </div>
        <div class="principles">
          <article class="principle">
            <p class="principle-no">01</p>
            <div>
              <h3>Nobody left can explain it</h3>
              <p>The people who built it have gone, the documentation is stale, and the risk of touching it is unknown. Reverse-engineering an estate is a large part of this work.</p>
            </div>
          </article>
          <article class="principle">
            <p class="principle-no">02</p>
            <div>
              <h3>The bill grew quietly</h3>
              <p>Cloud spend rarely spikes. It accretes, through orphaned resources, over-provisioning and instances nobody owns. Finding it means talking to people, not just reading a dashboard.</p>
            </div>
          </article>
          <article class="principle">
            <p class="principle-no">03</p>
            <div>
              <h3>Data cannot leave</h3>
              <p>Regulated estates cannot send documents to a third-party inference API. That constraint drives the whole architecture, and it is one we have already built against.</p>
            </div>
          </article>
          <article class="principle">
            <p class="principle-no">04</p>
            <div>
              <h3>It has to keep running</h3>
              <p>None of this happens on a greenfield site. The platform is live, it has users, and the work has to land without an outage.</p>
            </div>
          </article>
        </div>
      </div>
    </section>
''' % items
    return page("/sectors/", "Sectors | Kamobo",
                "Azure, data and AI engagements delivered across financial services, energy, "
                "professional education, media and streaming, legal and employment services.",
                body, "/sectors/")


# ---------------------------------------------------------------- re-house

HEADING = re.compile(r"<(/?)h([1-4])\b")


def promote_headings(body):
    """Lift a page's first content heading level to h2.

    Eleven pages jumped straight from h1 to h3, and three case studies from h1
    to h4, because their section headings were styled rather than structured.
    That is a real accessibility and search defect, and screen readers and
    search engines both read the outline. Everything before the first h2 is
    shifted up by the same delta, so relative nesting is preserved.
    """
    opens = [int(m.group(2)) for m in HEADING.finditer(body) if not m.group(1)]
    before = []
    for lv in opens:
        if lv == 2:
            break
        if lv > 1:
            before.append(lv)
    if not before:
        return body
    delta = min(before) - 2
    if delta <= 0:
        return body
    out, idx, seen_h2 = [], 0, False
    for m in HEADING.finditer(body):
        lv, closing = int(m.group(2)), m.group(1)
        if lv == 2 and not closing:
            seen_h2 = True
        out.append(body[idx:m.start()])
        out.append("<%sh%d" % (closing, max(2, lv - delta) if (not seen_h2 and lv > 1) else lv))
        idx = m.end()
    out.append(body[idx:])
    return "".join(out)


TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)"', re.S)
CANON = re.compile(r'<link rel="canonical" href="https://kamobo\.co\.uk(.*?)"', re.S)
MAIN = re.compile(r'<main id="main">(.*)</main>', re.S)
OLD_CTA = re.compile(r'\s*<section class="cta"[^>]*>.*?</section>\s*$', re.S)


def rehouse():
    done, skipped = 0, []
    for f in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = "/" + os.path.relpath(f, ROOT).replace("\\", "/").replace("index.html", "")
        if rel.startswith("/assets") or rel in ("/", "/sectors/"):
            continue
        s = io.open(f, encoding="utf-8").read()
        mt, md, mc, mm = TITLE.search(s), DESC.search(s), CANON.search(s), MAIN.search(s)
        if not (mt and md and mm):
            skipped.append(rel)
            continue
        body = OLD_CTA.sub("\n", mm.group(1))          # the shared CTA is re-added by page()
        body = promote_headings(body)
        canonical = mc.group(1) if mc else rel
        active = next((h for h, _t in NAV if h == rel), "")
        page(rel, mt.group(1), md.group(1), body, active)
        done += 1
    return done, skipped


if __name__ == "__main__":
    homepage()
    sectors_page()
    n, skipped = rehouse()
    print("built homepage + sectors, re-housed %d pages" % n)
    if skipped:
        print("ABORT: could not parse:")
        for s in skipped:
            print("   ", s)
        sys.exit(1)

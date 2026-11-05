# -*- coding: utf-8 -*-
"""Build the Kamobo site shell: chrome, homepage, sectors page.

Rebuilt 5 November 2026 against real renders of the Azure and DevOps consultancy
reference class (Transparity, Kainos, Version 1, Coeo, Equal Experts,
Thoughtworks). Every one of them opens on a dark or coloured full-bleed hero
with a large image, carries a contact action in the header, and stacks
full-width bands. The previous homepage was a white page of text blocks and at
1920px its hero was two-thirds empty, which is what "looks broken" meant.

No stock photography is licensed and stock team photos are a named tell in the
design research, so the hero image is the one honest visual an engineering
consultancy has: a labelled architecture of a platform we actually built, drawn
from freelance/proposals/_facts-pack.md and captioned as exactly that.

Pages holding fact-checked prose (services, case studies, insights, about,
pricing and the rest) are re-housed in the new chrome rather than rewritten,
because that prose was written against the facts pack, which is the only claim
set allowed.

Run:  python scripts/build.py && python scripts/protect-email.py \
      && python scripts/fingerprint.py
"""
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Every booking action on the site. scripts/set-booking-url.py can repoint
# these afterwards; the build emits the live Cal.com link directly so a fresh
# build is never a regression to mailto.
BOOK = "https://cal.com/kamobo/30min"
BOOK_ATTRS = 'data-book href="%s" target="_blank" rel="noopener"' % BOOK
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
     "Find what you are paying for and no longer use, and stop it coming back."),
    ("azure-data-engineering", "Azure data platforms",
     "Reporting and analytics pipelines that run reliably and cost what they should."),
    ("private-llm-rag", "Private LLM and RAG",
     "AI across your own documents, without any of it leaving your tenant."),
    ("ai-agent-development", "AI agents in production",
     "Software that handles the repetitive work, with a person approving anything that matters."),
    ("terraform-azure-landing-zones", "Landing zones and Terraform",
     "A clean, governed Azure foundation so teams can build without creating risk."),
    ("application-performance-troubleshooting", "Performance and root-cause",
     "Work out why it is slow or failing, and prove it, before anyone pays for a rebuild."),
    ("devops-cicd-gitops", "DevOps, CI/CD and GitOps",
     "Ship changes in minutes rather than hours, without the release-day drama."),
    ("api-development", "APIs and integration",
     "Get your systems talking to each other reliably, including the awkward old ones."),
    ("saas-software-development", "Software and SaaS",
     "Build and run the product itself, from the database to the billing."),
]
SERVICE_TITLE = {s: t for s, t, _d in SERVICES}

# Four practice areas on the homepage, the nine service pages beneath them.
# Everything here is supported by the facts pack.
PRACTICES = [
    ("01", "Azure platforms and DevOps",
     "The governed foundation and the pipeline that ships to it: landing zones in Terraform, "
     "CI/CD and GitOps, and the cost discipline that keeps the bill honest.",
     ["terraform-azure-landing-zones", "devops-cicd-gitops", "azure-cost-optimization"]),
    ("02", "Data platforms",
     "Synapse, Data Factory and Databricks estates built as code from dev through to "
     "production, with least-privilege networking throughout.",
     ["azure-data-engineering"]),
    ("03", "Private AI",
     "Self-hosted models and agents on infrastructure you control, with nothing leaving the "
     "tenant and a person approving anything that matters.",
     ["private-llm-rag", "ai-agent-development"]),
    ("04", "Recovery and software",
     "Taking over systems nobody left can explain, finding the real bottleneck before anyone "
     "pays for a rebuild, and building the product itself.",
     ["application-performance-troubleshooting", "api-development", "saas-software-development"]),
]

STUDIES = [
    ("azure-bill-six-figures", "&pound;150,000 a year",
     "taken off an Azure bill and kept off, after a full audit of what the estate was "
     "actually running and paying for."),
    ("streaming-platform-nobody-could-explain", "70% cheaper to run",
     "over three years, on a streaming platform we took over, diagnosed and rebuilt without "
     "taking it offline."),
    ("private-ai-platform-zero-trust", "Nothing leaves the tenant",
     "on a private AI platform for confidential documents that cannot legally be sent to a "
     "public AI service."),
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
     "reverse-engineered, load tested with K6 and moved to autoscaling Azure. The cost of running "
     "it fell 70% over three years."),
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
    ("70%", "cheaper to run, on a platform we rebuilt"),
    ("18,000+", "users on an AI platform we build and operate"),
]

# IS2 is not here: its mark has white foreground paths and cannot render as a
# silhouette on white. Nine logos in one row is also a cleaner band than ten
# across two.
CLIENT_LOGOS = [
    ("acca.svg", "ACCA"), ("lme.svg", "London Metal Exchange"), ("segro.png", "SEGRO"),
    ("guardian.svg", "Guardian Financial Services"), ("sefe.svg", "SEFE Energy"),
    ("ingeus.svg", "Ingeus"), ("stone-king.svg", "Stone King LLP"), ("zones.svg", "Zones UK"),
    ("glisser.svg", "Glisser"),
]

# The private AI platform from the facts pack, as a labelled architecture. Every
# box is a component that exists on that platform; the three separate stores
# are the point of the design and the thing a security review asks about.
FIGURE = '''        <figure class="hero-figure">
          <svg viewBox="0 0 600 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="archTitle">
            <title id="archTitle">Architecture of the private AI platform: users through SSO, a clustered NGINX ingress, an API layer with RabbitMQ and Redis, self-hosted inference on GPU nodes, and one isolated vector store per use case, all built with Terraform, Ansible and GitHub Actions and observed with Grafana.</title>
            <defs>
              <style>
                .f-box{fill:rgba(255,255,255,0.045);stroke:rgba(255,255,255,0.3);stroke-width:1}
                .f-iso{fill:rgba(52,184,143,0.08);stroke:#34B88F;stroke-width:1.2}
                .f-line{stroke:rgba(255,255,255,0.3);stroke-width:1}
                .f-t{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-size:11px;fill:rgba(255,255,255,0.9);letter-spacing:0.04em}
                .f-s{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-size:9.5px;fill:rgba(255,255,255,0.55);letter-spacing:0.06em}
                .f-a{fill:#34B88F}
              </style>
            </defs>
            <rect x="8" y="8" width="584" height="424" rx="3" fill="none" stroke="rgba(255,255,255,0.18)" stroke-dasharray="4 4"/>
            <text x="24" y="30" class="f-s">AZURE &#183; PRIVATE NETWORK &#183; ZERO TRUST</text>

            <rect x="200" y="46" width="200" height="32" rx="2" class="f-box"/>
            <text x="300" y="66" class="f-t" text-anchor="middle">USERS &#183; SSO &#183; REACT CHAT</text>
            <line x1="300" y1="78" x2="300" y2="104" class="f-line"/>

            <rect x="60" y="104" width="480" height="34" rx="2" class="f-box"/>
            <text x="300" y="125" class="f-t" text-anchor="middle">NGINX INGRESS &#183; CLUSTERED</text>
            <line x1="135" y1="138" x2="135" y2="166" class="f-line"/>
            <line x1="300" y1="138" x2="300" y2="166" class="f-line"/>
            <line x1="465" y1="138" x2="465" y2="166" class="f-line"/>

            <rect x="60" y="166" width="150" height="34" rx="2" class="f-box"/>
            <text x="135" y="187" class="f-t" text-anchor="middle">API LAYER</text>
            <rect x="225" y="166" width="150" height="34" rx="2" class="f-box"/>
            <text x="300" y="187" class="f-t" text-anchor="middle">RABBITMQ</text>
            <rect x="390" y="166" width="150" height="34" rx="2" class="f-box"/>
            <text x="465" y="187" class="f-t" text-anchor="middle">REDIS</text>
            <line x1="135" y1="200" x2="135" y2="228" class="f-line"/>
            <line x1="300" y1="200" x2="300" y2="228" class="f-line"/>
            <line x1="465" y1="200" x2="465" y2="228" class="f-line"/>

            <rect x="60" y="228" width="480" height="34" rx="2" class="f-box"/>
            <text x="300" y="249" class="f-t" text-anchor="middle">INFERENCE &#183; vLLM / OLLAMA / LLAMA.CPP &#183; GPU NODES</text>
            <line x1="135" y1="262" x2="135" y2="292" class="f-line"/>
            <line x1="300" y1="262" x2="300" y2="292" class="f-line"/>
            <line x1="465" y1="262" x2="465" y2="292" class="f-line"/>

            <rect x="60" y="292" width="150" height="56" rx="2" class="f-iso"/>
            <text x="135" y="314" class="f-t" text-anchor="middle">USE CASE A</text>
            <text x="135" y="334" class="f-s" text-anchor="middle">PGVECTOR &#183; ISOLATED</text>
            <rect x="225" y="292" width="150" height="56" rx="2" class="f-iso"/>
            <text x="300" y="314" class="f-t" text-anchor="middle">USE CASE B</text>
            <text x="300" y="334" class="f-s" text-anchor="middle">CHROMA &#183; ISOLATED</text>
            <rect x="390" y="292" width="150" height="56" rx="2" class="f-iso"/>
            <text x="465" y="314" class="f-t" text-anchor="middle">USE CASE C</text>
            <text x="465" y="334" class="f-s" text-anchor="middle">LANCEDB &#183; ISOLATED</text>
            <text x="300" y="368" class="f-s f-a" text-anchor="middle">ONE STORE PER USE CASE &#183; NO PATH BETWEEN THEM</text>

            <line x1="60" y1="392" x2="540" y2="392" class="f-line"/>
            <text x="300" y="414" class="f-s" text-anchor="middle">TERRAFORM &#183; ANSIBLE &#183; GITHUB ACTIONS &#183; GRAFANA</text>
          </svg>
          <figcaption>The private AI platform we built and run for a global professional education body. Self-hosted inference on GPU Azure, one isolated store per use case, nothing leaving the tenant.</figcaption>
        </figure>
'''

OFFER = '''
    <section class="section offer-band">
      <div class="wrap offer-inner">
        <div class="offer-lede">
          <p class="kicker">Where most engagements start</p>
          <h2>The Azure Review</h2>
          <p>A read-only assessment of your Azure estate: what it costs, what it is running, where the risk sits, and what we would fix first. You get written findings and a priced plan. If you go on to have us do the work and we start within 30 days, the fee is credited in full against it.</p>
        </div>
        <div class="offer-side">
          <dl class="offer-spec">
            <div><dt>Price</dt><dd>&pound;2,500</dd></div>
            <div><dt>Duration</dt><dd>3 working days</dd></div>
            <div><dt>Access</dt><dd>Read-only</dd></div>
            <div><dt>Output</dt><dd>Written findings</dd></div>
          </dl>
          <a class="btn btn-ghost" href="/azure-review/">What the review covers</a>
        </div>
      </div>
    </section>
'''


def clients():
    """One static row of uniform logo silhouettes. The earlier marquee is a
    named tell in the design research, and a five-by-two grid left the second
    row half empty."""
    return """
    <section class="clients" aria-label="Organisations we have worked with">
      <div class="wrap">
        <p class="trust-label">Organisations we have worked with</p>
        <ul class="logo-row">
%s
        </ul>
      </div>
    </section>
""" % "\n".join(
        '          <li><img src="/assets/logos/%s" alt="%s" height="22" /></li>'
        % (f, n) for f, n in CLIENT_LOGOS)


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
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />
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
        <img src="/assets/logo.svg" alt="Kamobo" width="150" height="36" />
      </a>
      <nav class="nav" aria-label="Primary">
%s
      </nav>
      <div class="header-cta"><a class="btn btn-primary btn-sm" %s>Book a call</a></div>
      <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </header>
''' % (links, BOOK_ATTRS)


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
          <a class="btn btn-primary btn-lg" %s>Book a call</a>
          <a class="btn btn-ghost btn-lg" href="%s">Email instead</a>
        </div>
        <p class="cta-sub">No sales sequence. A reply from the engineer who would do the work.</p>
      </div>
    </section>
''' % (BOOK_ATTRS, MAIL)


# The contact page's own hero says the same thing as the global band, word for
# word, so the band is pure duplication there. It closes with the action only.
CONTACT_CLOSE = '''
    <section class="section section-alt">
      <div class="wrap">
        <div class="cta-actions" style="margin-top:0">
          <a class="btn btn-primary btn-lg" %s>Book a call</a>
          <a class="btn btn-ghost btn-lg" href="%s">Send an email</a>
        </div>
        <p class="meta" style="margin-top:18px">Either way it reaches the same inbox.</p>
      </div>
    </section>
''' % (BOOK_ATTRS, MAIL)


def page(path, title, desc, body, active="", closer=None):
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" \
        else os.path.join(ROOT, "index.html")
    d = os.path.dirname(out)
    if d:
        os.makedirs(d, exist_ok=True)
    html = (head(title, desc, path) + header(active) +
            '\n  <main id="main">\n' + body + (CTA if closer is None else closer) +
            "  </main>\n" + footer())
    io.open(out, "w", encoding="utf-8", newline="\n").write(html)
    return out


# ---------------------------------------------------------------- homepage

INSIGHT_ROW = re.compile(
    r'<h[23]><a href="/insights/([a-z0-9-]+)/">(.*?)</a></h[23]>\s*<div class="row-body">\s*<p>(.*?)</p>', re.S)
HOME_INSIGHTS = ["interviews-find-more-savings-than-tooling",
                 "load-test-before-you-re-architect",
                 "taking-over-a-system-nobody-can-explain"]


def insight_rows():
    """Three posts for the homepage, read from the insights index so a retitle
    there is picked up here, in the order that suits a platform buyer."""
    src = io.open(os.path.join(ROOT, "insights", "index.html"), encoding="utf-8").read()
    found = {slug: (title, sf) for slug, title, sf in INSIGHT_ROW.findall(src)}
    rows = []
    for i, slug in enumerate(HOME_INSIGHTS):
        if slug not in found:
            continue
        title, sf = found[slug]
        rows.append('''          <article class="row">
            <p class="row-no">%02d</p>
            <h3><a href="/insights/%s/">%s</a></h3>
            <div class="row-body"><p>%s</p></div>
          </article>''' % (i + 1, slug, title, sf))
    return "\n".join(rows)


def homepage():
    practices = "\n".join('''          <article class="practice">
            <p class="practice-no">%s</p>
            <h3>%s</h3>
            <p>%s</p>
            <ul>
%s
            </ul>
          </article>''' % (no, title, desc, "\n".join(
        '              <li><a href="/services/%s/">%s</a></li>' % (s, SERVICE_TITLE[s]) for s in links))
        for no, title, desc, links in PRACTICES)
    proof = "\n".join(
        '          <a href="/work/%s/"><strong>%s</strong><span>%s</span><em>Read the story</em></a>'
        % (s, n, d) for s, n, d in STUDIES)
    stats = "\n".join(
        '          <div><strong>%s</strong><span>%s</span></div>' % (n, d) for n, d in STATS)

    body = '''    <section class="hero">
      <div class="wrap">
        <div class="hero-inner">
          <div>
            <p class="kicker">UK Azure and DevOps consultancy</p>
            <h1>Azure platforms, built to keep running.</h1>
            <p class="lede">Kamobo designs, builds and recovers cloud platforms, data pipelines and AI systems: as code, in your own tenant, and handed over in a state your team can run. Every engagement is led hands-on by the engineer doing the work.</p>
            <div class="hero-cta">
              <a class="btn btn-primary btn-lg" %s>Book a call</a>
              <a class="quiet-link" href="/work/">See the work</a>
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
          <h2>Four practice areas, one engineer accountable for each</h2>
          <p class="section-sub">Most engagements start in one of these and widen once we are in the estate and can see what is actually there.</p>
        </div>
        <div class="practices">
%s
        </div>
      </div>
    </section>
%s
    <section class="section">
      <div class="wrap">
        <div class="section-head-row">
          <div class="section-head">
            <p class="kicker">Our work</p>
            <h2>What these engagements were worth</h2>
          </div>
          <a href="/work/">All case studies &#8594;</a>
        </div>
        <div class="proof">
%s
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head-row">
          <div class="section-head">
            <p class="kicker">Insights</p>
            <h2>Things worth writing down</h2>
          </div>
          <a href="/insights/">All insights &#8594;</a>
        </div>
        <div class="rows">
%s
        </div>
      </div>
    </section>

''' % (BOOK_ATTRS, FIGURE, stats, clients(), practices, OFFER, proof, insight_rows())

    return page("/", "Kamobo | Azure and DevOps consultancy, UK",
                "Kamobo is a UK Azure and DevOps consultancy. We design, build and recover cloud "
                "platforms, data pipelines and AI systems as code, led hands-on by the engineer "
                "doing the work.", body)


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
              <p>Cloud spend rarely spikes. It accretes, through orphaned resources, over-provisioning and instances nobody owns. An audit finds it; the people who own it tell you what is safe to remove.</p>
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
    That is a real accessibility and search defect. Everything before the first
    h2 is shifted up by the same delta, so relative nesting is preserved.
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
        active = next((h for h, _t in NAV if h == rel), "")
        page(rel, mt.group(1), md.group(1), body, active,
             closer=CONTACT_CLOSE if rel == "/contact/" else None)
        done += 1
    return done, skipped


if __name__ == "__main__":
    n, skipped = rehouse()          # insights index must exist before homepage() reads it
    homepage()
    sectors_page()
    print("re-housed %d pages, built homepage + sectors" % n)
    if skipped:
        print("ABORT: could not parse:")
        for s in skipped:
            print("   ", s)
        sys.exit(1)

# Kamobo, public website

Marketing site for **Kamobo Ltd**, a UK cloud, data and AI consultancy. The site sells
services rather than products: engagements by the day, as a fixed-price project, or on a
monthly retainer.

Rebuilt 4 November 2026: light theme, service-led positioning, published pricing, and a
"straight answers" section that names what Kamobo does not do. Copy is constrained by
`../freelance/proposals/_facts-pack.md`, which is the only set of claims permitted. No em
dashes anywhere, per house style.

## Stack

Zero-build static site — plain HTML, CSS and vanilla JS. No dependencies, no toolchain.

| File | Purpose |
|------|---------|
| `index.html` | Single-page site (hero, services, products, approach, proof, about, contact) |
| `styles.css` | Design system + responsive layout |
| `main.js` | Scroll reveals, mobile menu, animated hero particle field |
| `assets/logo.svg` | Primary logo (mark + wordmark) |
| `assets/favicon.svg` | Favicon |

## Run locally

Just open `index.html`, or serve the folder:

```bash
python -m http.server 8000
# then visit http://localhost:8000
```

## Deploy

**Hosted on DigitalOcean App Platform**, static site `kamobo-web`, app id
`266261e0-953f-4627-acd2-b47921716243`, region `lon`, serving `kamobo.co.uk` (primary) and
`www.kamobo.co.uk` (alias) through Cloudflare. The app builds this repo from `main`.

Pushing to `main` redeploys: `.github/workflows/deploy.yml` installs doctl and calls
`apps create-deployment --force-rebuild`, using the repo secret
`DIGITALOCEAN_ACCESS_TOKEN`. App Platform's generic-git source does not auto-deploy on
push by itself, which is why the Actions trigger exists.

### Cache busting is not optional here

Cloudflare serves `styles.css` and `main.js` with `max-age=14400` (4 hours in the
browser) and `s-maxage=86400` (24 hours at the edge), while the HTML is only cached for
10 seconds. Deploy a CSS change without changing its URL and visitors get **new HTML with
the old stylesheet** for up to a day, which renders as an unstyled page. This happened on
4 November 2026 and was live until it was caught.

So both assets carry a content hash in the query string, and it must be regenerated
whenever either file changes:

    python scripts/fingerprint.py

That rewrites `styles.css?v=` and `main.js?v=` across every HTML file from a SHA-1 of the
asset's own bytes, so the query only changes when the asset does.

### If the site 404s or Cloudflare returns a 1016

That happened between early September and 4 November 2026. The cause was **not** a deleted
app: an account suspension left every App Platform app on the account with no active
deployment, so the ingress hostname stopped resolving and Cloudflare had nothing to proxy
to. The fix was a forced rebuild, after which the app came back on its original ingress
`kamobo-web-owcuf.ondigitalocean.app`, so no DNS change was needed.

    curl -X POST -H "Authorization: Bearer $DO_TOKEN" -H "Content-Type: application/json"       -d '{"force_build":true}'       https://api.digitalocean.com/v2/apps/266261e0-953f-4627-acd2-b47921716243/deployments

### Alternative host

GitHub Pages works as a fallback: add a `CNAME` file containing `kamobo.co.uk`, enable
Pages on `main` at the repository root, and repoint both Cloudflare CNAMEs at
`kamoboltd.github.io`, DNS-only at first so GitHub can issue its certificate.

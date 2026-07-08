# Kamobo — Public Website

Marketing site for **Kamobo Ltd** — a UK software studio building fixed-cost products
for niche markets (e.g. [GrassrootsDNA](https://grassrootsdna.co.uk)) and delivering
senior **DevOps & Azure** consultancy.

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

Any static host works — Cloudflare Pages, DigitalOcean App Platform (static site),
GitHub Pages, or Netlify. Point the build at the repo root; there is no build step,
so the "output directory" is `/`.

## Content notes / TODO

- **Contact email** is a placeholder: `hello@kamobo.co.uk` — update if different.
- **Client naming** is deliberately anonymised ("a global professional body"). Swap in
  a named reference/logo only with client permission.
- Company registration number can be added to the footer when ready.

# Lookcraft — landing page

Astro site for Lookcraft, deployed to GitHub Pages.

## Commands

Run from `web/`:

| Command           | Action                                  |
| :---------------- | :-------------------------------------- |
| `npm install`     | Install dependencies                    |
| `npm run dev`     | Dev server at `localhost:4321`          |
| `npm run build`   | Build the static site to `./dist/`      |
| `npm run preview` | Serve the build locally                 |
| `npm run favicons` | Rebuild favicons from `src/assets/icon.png` |

## Structure

```text
src/
├── assets/       app icon, logo mark, App Store badge, fonts (from the app)
│   └── screens/  screenshots for the phone frames (see its README)
├── components/   Hero, Steps, Different, PrivacyNote, Faq, PhoneFrame,
│                 AppStoreButton, Logo, PageHeader, Footer
├── layouts/      Base.astro (head, meta, share image, app banner)
├── lib/url.ts    withBase() for links under the Pages base path
├── pages/        home, support, privacy, terms, 404, og.png (share image), robots.txt
├── styles/       global.css (color tokens, light/dark, fonts)
└── consts.ts     brand name, tagline, App Store ID and release flag, contact and legal details
```

## Before and after launch

- **Rename:** change `BRAND_NAME` in `src/consts.ts`. Pages, the share image and
  the structured data follow. The domain, contact email and logo mark are separate.
- **App released:** set `APP_RELEASED = true`. The "Coming soon" label becomes
  the App Store badge, and Safari on iPhone shows the app banner.
- **Screenshots:** add them to `src/assets/screens/` with the names in its README.

The look follows the app's `Theme.swift` in `../styleFit`: charcoal on warm
off-white (the reverse in dark mode), Fraunces Medium titles, Hanken Grotesk
for everything else, rounded cards.

## Deploying

`.github/workflows/deploy-web.yml` (at the repo root) builds and deploys on
every push to `main` that touches `web/`. In the GitHub repo, set
**Settings → Pages → Source** to **GitHub Actions**.

The workflow passes the Pages origin and base path to the build as
`SITE_URL` and `BASE_PATH`, so a project page (`<user>.github.io/<repo>`)
and a custom domain both work. Link to internal pages and `public/` files with
`withBase('path')` rather than a bare `/path` so they keep working under a
sub-path.

To check a sub-path build locally:

```sh
BASE_PATH=/Lookcraft-marketing npm run build && npm run preview
```

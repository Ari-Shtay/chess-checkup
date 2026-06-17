# Deploying Chess Checkup to Vercel

The whole app is a single static `index.html` with no build step, so deploying is
just "serve the folder."

## One-time setup (recommended: GitHub import)

1. Go to https://vercel.com/new and import the `Ari-Shtay/chess-checkup` repo.
2. Framework preset: **Other**. Build command: **none**. Output directory: **leave blank / `.`** (the repo root).
3. Deploy. Vercel serves `index.html` at the root and gives you a free
   `*.vercel.app` URL (per the spec, the launch ships on the free subdomain;
   a custom domain waits for the launch gate).

After that, every push to `main` auto-deploys.

## Or deploy from the CLI

```sh
npm i -g vercel      # once
vercel               # preview deploy
vercel --prod        # production deploy
```

## What `vercel.json` does

- `cleanUrls` / `trailingSlash: false` — tidy URLs.
- `Referrer-Policy: strict-origin-when-cross-origin` — **important**: this keeps the
  deploy origin (e.g. `chess-checkup.vercel.app`) attached as the `Referer`/`Origin`
  on the Lichess API calls. Because browsers forbid setting a `User-Agent` from
  `fetch()`, that origin is how Lichess identifies this app (see the note in
  `index.html`). Do **not** change this to `no-referrer`.
- `X-Content-Type-Options` / `X-Frame-Options` — basic hardening.

A `Content-Security-Policy` is set via a `<meta>` tag in `index.html` (so it travels
with the file and is testable locally); it allows only the chess.js CDN and the
Lichess API.

## Notes

- No environment variables, no secrets, no backend in v0.
- If Lichess ever rate-limits heavy launch traffic, the upgrade path is the
  section-6 serverless proxy (a `/api/lichess` function that adds a real
  `User-Agent`); not needed for v0.

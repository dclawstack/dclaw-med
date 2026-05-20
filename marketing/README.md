# DClaw Med — Marketing Site

Standalone Next.js 14 landing page for [DClaw Med](https://github.com/dclawstack/dclaw-med).
Independent from `frontend/` (the clinician dashboard) — no backend calls, no
shared deps.

## Local

```bash
cd marketing
npm install
npm run dev     # http://localhost:3005
```

## Environment

`NEXT_PUBLIC_APP_URL` — the public URL of the clinician dashboard that the
"Launch app" / "Launch dashboard" CTAs point at. Falls back to
`http://localhost:3004` (the local Docker / dev port) if unset.

For Vercel: set `NEXT_PUBLIC_APP_URL` in the project's Environment Variables
to the public app hostname (e.g. `https://app.dclaw-med.dev`) before deploying
production.

## Deploy

Configured for Vercel. The Vercel project root must be `marketing/`.

```bash
vercel link              # one-time
vercel                   # preview
vercel --prod            # production
```

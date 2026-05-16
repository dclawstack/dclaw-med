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

## Deploy

Configured for Vercel. The Vercel project root must be `marketing/`.

```bash
vercel link              # one-time
vercel                   # preview
vercel --prod            # production
```

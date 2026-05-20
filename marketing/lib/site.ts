export const GITHUB_URL = "https://github.com/dclawstack/dclaw-med";
export const DEMO_EMAIL = "hello@dclaw.dev";

// Where the clinician dashboard lives. Override via NEXT_PUBLIC_APP_URL on
// Vercel once the app has a public hostname. Default is the local dev port
// so anyone running the stack locally gets a working "Launch dashboard" CTA
// out of the box.
export const APP_URL =
  process.env.NEXT_PUBLIC_APP_URL?.trim() || "http://localhost:3004";

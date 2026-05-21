import type { APIRequestContext } from "@playwright/test";

export const API_BASE = process.env.DCLAW_API_URL ?? "http://localhost:8092";

export const ADMIN_EMAIL = "test@dclaw.dev";
export const ADMIN_PASSWORD = "TestPass123!";
export const DEMO_EMAIL = "demo@dclaw.dev";
export const DEMO_PASSWORD = "DemoPass123!";

/**
 * Reset the demo dataset via the public endpoint. Only ever touches
 * rows tagged with the DEMO- MRN prefix and the demo@dclaw.dev user —
 * never real data. Safe to call at suite end.
 */
export async function resetDemoIfEnabled(
  request: APIRequestContext,
): Promise<void> {
  const status = await request.get(`${API_BASE}/api/v1/demo/status`);
  if (!status.ok()) return;
  const body = await status.json();
  if (!body.enabled) return;
  await request.delete(`${API_BASE}/api/v1/demo/reset`);
}

/**
 * Seed the demo dataset directly via the API (faster than going
 * through the UI when the test doesn't care about the seed click).
 */
export async function ensureDemoSeeded(
  request: APIRequestContext,
): Promise<void> {
  await request.post(`${API_BASE}/api/v1/demo/seed`);
}

/**
 * Log in as the named admin and return the bearer token. Useful when
 * a test needs to set up state via the API rather than the UI.
 */
export async function adminToken(
  request: APIRequestContext,
): Promise<string> {
  const res = await request.post(`${API_BASE}/api/v1/auth/login`, {
    form: { username: ADMIN_EMAIL, password: ADMIN_PASSWORD },
  });
  if (!res.ok()) {
    throw new Error(
      `Admin login failed (${res.status()}). Is the admin seeded? ` +
        `Expected ${ADMIN_EMAIL} / ${ADMIN_PASSWORD}.`,
    );
  }
  const body = await res.json();
  return body.access_token as string;
}

/** Unique-per-test email so suites can be re-run without collisions. */
export function uniqueEmail(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`;
}

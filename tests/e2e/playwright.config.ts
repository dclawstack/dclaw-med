import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for DClaw Med end-to-end tests.
 *
 * Targets the running Docker stack on this host:
 *   - frontend at http://localhost:3004
 *   - backend  at http://localhost:8092
 *
 * Override with PLAYWRIGHT_BASE_URL / DCLAW_API_URL env vars if needed.
 */
export default defineConfig({
  testDir: ".",
  fullyParallel: false, // they touch shared demo data — serialize to keep things sane
  workers: 1,
  retries: 0,
  timeout: 60_000,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3004",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});

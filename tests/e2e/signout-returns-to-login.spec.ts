import { expect, test } from "@playwright/test";
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  ensureDemoSeeded,
  resetDemoIfEnabled,
} from "./helpers";

test.describe("Sign out", () => {
  test.afterAll(async ({ request }) => {
    await resetDemoIfEnabled(request);
  });

  test("logged-in user → Sign out → /login", async ({ page, request }) => {
    // Use the admin login (seeded by the dev bootstrap) so this test
    // doesn't depend on demo data being in place.
    await ensureDemoSeeded(request); // no-op if already seeded; harmless
    await page.goto("/login");
    await page.getByLabel("Email").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    await page.getByRole("button", { name: /Sign out/i }).click();
    await page.waitForURL("**/login", { timeout: 10_000 });
    expect(page.url()).toMatch(/\/login$/);
  });
});

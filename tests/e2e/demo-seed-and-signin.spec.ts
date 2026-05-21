import { expect, test } from "@playwright/test";
import { resetDemoIfEnabled } from "./helpers";

test.describe("Demo seed + sign in as demo doctor", () => {
  test.beforeEach(async ({ request }) => {
    // Start each run from a clean demo state so the "Seed demo data"
    // button is the one rendered (not "Sign in as demo doctor").
    await resetDemoIfEnabled(request);
  });

  test.afterAll(async ({ request }) => {
    await resetDemoIfEnabled(request);
  });

  test("seed → sign in → /dashboard", async ({ page }) => {
    await page.goto("/");

    await page
      .getByRole("button", { name: /Seed demo data/i })
      .click();

    // After seeding the button morphs to "Sign in as demo doctor".
    const signInBtn = page.getByRole("button", {
      name: /Sign in as demo doctor/i,
    });
    await expect(signInBtn).toBeEnabled({ timeout: 15_000 });

    await signInBtn.click();

    // login() does router.replace to /dashboard for clinicians.
    await page.waitForURL("**/dashboard", { timeout: 15_000 });
    expect(page.url()).toMatch(/\/dashboard$/);
  });
});

import { expect, test } from "@playwright/test";
import { ensureDemoSeeded } from "./helpers";

test.describe("Logged-out landing page", () => {
  test.beforeAll(async ({ request }) => {
    // The demo section is gated on demo_status.enabled — seed once so
    // status.seeded is true and the section renders its "Sign in" state.
    await ensureDemoSeeded(request);
  });

  test("renders hero and demo section", async ({ page }) => {
    await page.goto("/");

    // Hero — sanity that the landing page rendered at all.
    await expect(
      page.getByRole("heading", { name: /Clinical intelligence/i }),
    ).toBeVisible();

    // Demo section — auto-hides if ENABLE_DEMO_MODE is off, so its
    // presence is also the assertion that demo mode is on in this stack.
    await expect(
      page.getByRole("heading", { name: /Spin up a demo dataset\./i }),
    ).toBeVisible();
  });
});

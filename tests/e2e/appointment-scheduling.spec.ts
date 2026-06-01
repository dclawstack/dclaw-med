import { expect, test } from "@playwright/test";
import { DEMO_EMAIL, DEMO_PASSWORD, ensureDemoSeeded } from "./helpers";

test.describe("Doctor schedules appointment", () => {
  test("clickable Schedule button validates missing fields, then schedules", async ({
    page,
    request,
  }) => {
    await ensureDemoSeeded(request);

    await page.goto("/login");
    await page.getByLabel("Email").fill(DEMO_EMAIL);
    await page.getByLabel("Password").fill(DEMO_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    await page.goto("/appointments");
    await page.getByRole("button", { name: /New Appointment/i }).first().click();

    const scheduleBtn = page.getByRole("button", { name: /^Schedule$/ });

    // The button is now always clickable (not silently disabled).
    await expect(scheduleBtn).toBeEnabled();

    // Fill patient + date/time but intentionally skip the provider.
    await page.getByText("Select patient").click();
    await page.getByRole("option").first().click();
    await page.locator('input[type="datetime-local"]').fill("2026-11-05T09:15");

    // Clicking with a missing provider gives clear feedback instead of nothing.
    await scheduleBtn.click();
    await expect(page.getByText("Select a provider.")).toBeVisible({ timeout: 5_000 });

    // Now pick the provider and schedule for real.
    await page.getByText("Select provider").click();
    await page.getByRole("option").first().click();
    await scheduleBtn.click();
    await expect(page.getByText(/Appointment scheduled/i)).toBeVisible({
      timeout: 10_000,
    });
  });
});

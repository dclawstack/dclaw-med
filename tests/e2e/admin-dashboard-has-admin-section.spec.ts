import { expect, test } from "@playwright/test";
import { ADMIN_EMAIL, ADMIN_PASSWORD } from "./helpers";

test.describe("Admin login", () => {
  test("dashboard sidebar shows Users + Audit Trail", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    // These two links are only rendered when can.viewAudit(user) is
    // true — i.e. the admin-only sidebar branch.
    await expect(
      page.getByRole("link", { name: /^Audit Trail$/ }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: /^Users$/ })).toBeVisible();
  });
});

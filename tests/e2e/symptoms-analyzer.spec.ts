import { expect, test } from "@playwright/test";
import { ADMIN_EMAIL, ADMIN_PASSWORD } from "./helpers";

// Real-LLM round-trip — runs against whatever LLM the backend is
// pointed at (local Ollama by default). Excluded from the default
// suite via @llm; opt in with RUN_LLM_TESTS=1.
test.describe("Symptom analyzer @llm", () => {
  // 3B Ollama generating 5 structured-JSON differentials can need
  // 4-7 minutes under load. Generous budget so the test isn't flaky.
  test.setTimeout(10 * 60_000);

  test("renders differentials + urgency + recommended tests", async ({ page }) => {
    // Sign in as admin (clinical-tool permission).
    await page.goto("/login");
    await page.getByLabel("Email").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    await page.goto("/symptoms");

    // Submit a chest-pain prompt — the analyzer's keyword fallback
    // would also produce ACS-style differentials for this input, so
    // the assertions below are deliberately *shape-only* (not
    // condition-name) to avoid coupling to the model's diction.
    await page
      .getByLabel("Symptoms")
      .fill("chest pain radiating to left arm, sweating, 30 minutes");
    await page.getByRole("button", { name: /Analyze/i }).click();

    // Wait for the urgency badge — it only renders after the call returns.
    const urgencyBadge = page.getByText(/URGENCY/i).first();
    await expect(urgencyBadge).toBeVisible({ timeout: 9 * 60_000 });
    await expect(urgencyBadge).toHaveText(/(LOW|MEDIUM|HIGH|CRITICAL)\s+URGENCY/i);

    // Differentials section renders. Shape-only checks — verify the
    // title (CardTitle renders as a div, not a heading), that at least
    // one confidence percentage is shown, and that the recommended-
    // tests panel is present.
    await expect(page.getByText("Differential Diagnoses")).toBeVisible();
    await expect(page.getByText(/\d+% confidence/).first()).toBeVisible();
    await expect(page.getByText("Recommended Tests")).toBeVisible();
  });
});

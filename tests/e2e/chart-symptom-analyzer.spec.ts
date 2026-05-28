import { expect, test } from "@playwright/test";
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  API_BASE,
  adminToken,
} from "./helpers";

// Real-LLM round-trip via the chart-side "Analyze" button added in
// PR #38. Same `@llm` gating as the dedicated /symptoms spec.
test.describe("Chart-side symptom analyzer @llm", () => {
  test.setTimeout(10 * 60_000);

  let patientId: string | null = null;
  let symptomId: string | null = null;

  test.beforeAll(async ({ request }) => {
    // Seed a patient + one symptom via the API so the chart has
    // something to analyze. Driving creation through the UI here
    // would add 30-60s of clicking that's already covered by the
    // existing admin-creates-doctor-and-patient.spec.ts.
    const token = await adminToken(request);
    const p = await request.post(`${API_BASE}/api/v1/med/patients`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        name: "Analyze Target",
        date_of_birth: "1970-04-04",
        gender: "other",
        medical_record_number: `MRN-LLM-${Date.now()}`,
      },
    });
    expect(p.ok()).toBeTruthy();
    patientId = (await p.json()).id;

    const s = await request.post(`${API_BASE}/api/v1/med/symptoms`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        patient_id: patientId,
        description: "chest pain radiating to left arm, sweating, 30 minutes",
        severity: 8,
      },
    });
    expect(s.ok()).toBeTruthy();
    symptomId = (await s.json()).id;
  });

  test.afterAll(async ({ request }) => {
    if (!patientId) return;
    const token = await adminToken(request);
    // CASCADE on patient delete cleans up the seeded symptom too.
    await request.delete(`${API_BASE}/api/v1/med/patients/${patientId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  });

  test("inline differential panel renders after Analyze click", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Email").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    expect(patientId).toBeTruthy();
    await page.goto(`/patients/${patientId}`);

    // Symptoms tab is the default — clicking the "Analyze" button
    // (the one with the Sparkles icon, not the dialog's "Add")
    // kicks the analyzer using the most recently captured symptom.
    await page.getByRole("button", { name: /^Analyze$/ }).click();

    // The inline differentials block appears under the symptom card.
    await expect(
      page.getByText(/Differential diagnoses/i),
    ).toBeVisible({ timeout: 9 * 60_000 });

    // Urgency badge in the inline panel.
    await expect(
      page.getByText(/(LOW|MEDIUM|HIGH|CRITICAL)\s+URGENCY/i).first(),
    ).toBeVisible();

    // At least one differential confidence percentage.
    await expect(page.getByText(/\d+%/).first()).toBeVisible();

    // Dismiss restores the original layout.
    await page.getByRole("button", { name: /^Dismiss$/ }).click();
    await expect(page.getByText(/Differential diagnoses/i)).toBeHidden();
  });
});

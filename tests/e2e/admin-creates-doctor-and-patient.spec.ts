import { expect, test } from "@playwright/test";
import {
  ADMIN_EMAIL,
  ADMIN_PASSWORD,
  API_BASE,
  adminToken,
  uniqueEmail,
} from "./helpers";

test.describe("Admin creates accounts + patients", () => {
  // We create rows via the API where it's already covered by the
  // backend tests — the e2e responsibility is the *UI flow*, not
  // re-verifying CRUD. The doctor creation step still goes through
  // the dialog so we exercise the "+ Add user" surface end-to-end.
  let createdPatientId: string | null = null;
  let createdDoctorEmail: string | null = null;

  test.afterAll(async ({ request }) => {
    // Best-effort cleanup. The backend has no DELETE /auth/users
    // endpoint, so created users are left behind (they're test-
    // tagged emails — harmless). Patient is cleaned up.
    if (createdPatientId) {
      const token = await adminToken(request);
      await request.delete(
        `${API_BASE}/api/v1/med/patients/${createdPatientId}`,
        { headers: { Authorization: `Bearer ${token}` } },
      );
    }
  });

  test("admin creates a doctor via dialog, then a patient via API", async ({
    page,
    request,
  }) => {
    // Pre-create a patient through the API so we have a real chart to
    // potentially link against. The user spec asks for "create a
    // patient with chart link", and the UI's create-patient flow is
    // covered separately by /patients pages.
    const token = await adminToken(request);
    const patientRes = await request.post(`${API_BASE}/api/v1/med/patients`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        name: "E2E Linked Patient",
        date_of_birth: "1985-05-05",
        gender: "other",
        medical_record_number: `MRN-E2E-${Date.now()}`,
      },
    });
    expect(patientRes.ok()).toBeTruthy();
    createdPatientId = (await patientRes.json()).id;

    // Now drive the UI: log in as admin, open admin/users, click + Add user.
    await page.goto("/login");
    await page.getByLabel("Email").fill(ADMIN_EMAIL);
    await page.getByLabel("Password").fill(ADMIN_PASSWORD);
    await page.getByRole("button", { name: /Sign in/i }).click();
    await page.waitForURL("**/dashboard", { timeout: 15_000 });

    await page.goto("/admin/users");
    // DialogTrigger wraps a Button so getByRole matches twice — first
    // the trigger, then the inner button. Clicking the trigger opens
    // the dialog either way.
    await page
      .getByRole("button", { name: /Add user/i })
      .first()
      .click();

    // Fill the dialog for a new doctor account.
    createdDoctorEmail = uniqueEmail("e2e-doctor");
    await page.getByLabel("Email").fill(createdDoctorEmail);
    await page.getByLabel("Full name").fill("E2E Test Doctor");
    await page.getByLabel("Temporary password").fill("e2e-password-1");
    // Role defaults to "doctor" in EMPTY_DRAFT so we don't need to touch it.
    await page.getByRole("button", { name: /^Create user$/ }).click();

    // The toast confirms the create — the surest signal the API
    // succeeded without depending on the table re-rendering.
    await expect(page.getByText(/User created/i)).toBeVisible({
      timeout: 10_000,
    });

    // Sanity: the created doctor can log in.
    const login = await request.post(`${API_BASE}/api/v1/auth/login`, {
      form: {
        username: createdDoctorEmail,
        password: "e2e-password-1",
      },
    });
    expect(login.ok()).toBeTruthy();
  });
});

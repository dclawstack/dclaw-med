import { describe, expect, it } from "vitest";

import type { CurrentUser } from "@/lib/api";
import { can, isClinicianUser, isPatientUser } from "@/lib/permissions";

const user = (role: string) => ({ role }) as Pick<CurrentUser, "role">;

describe("isPatientUser / isClinicianUser", () => {
  it("classifies a patient", () => {
    expect(isPatientUser(user("patient"))).toBe(true);
    expect(isClinicianUser(user("patient"))).toBe(false);
  });

  it("classifies each clinician role", () => {
    for (const role of ["admin", "doctor", "nurse", "receptionist"]) {
      expect(isClinicianUser(user(role))).toBe(true);
      expect(isPatientUser(user(role))).toBe(false);
    }
  });

  it("treats null/undefined as no access", () => {
    expect(isPatientUser(null)).toBe(false);
    expect(isClinicianUser(undefined)).toBe(false);
  });
});

describe("can.* role policy", () => {
  it("restricts prescriptions and diagnoses to admin/doctor", () => {
    expect(can.writePrescription(user("doctor"))).toBe(true);
    expect(can.writePrescription(user("admin"))).toBe(true);
    expect(can.writePrescription(user("nurse"))).toBe(false);
    expect(can.writeDiagnosis(user("receptionist"))).toBe(false);
  });

  it("lets nurses use clinical tools and write notes but not prescribe", () => {
    expect(can.useClinicalTool(user("nurse"))).toBe(true);
    expect(can.writeNote(user("nurse"))).toBe(true);
    expect(can.writePrescription(user("nurse"))).toBe(false);
  });

  it("scopes audit + app settings to admin only", () => {
    expect(can.viewAudit(user("admin"))).toBe(true);
    expect(can.viewAudit(user("doctor"))).toBe(false);
    expect(can.viewAppSettings(user("admin"))).toBe(true);
    expect(can.viewAppSettings(user("nurse"))).toBe(false);
  });

  it("denies everything to patients and to anonymous", () => {
    for (const check of Object.values(can)) {
      expect(check(user("patient"))).toBe(false);
      expect(check(null)).toBe(false);
    }
  });
});

/**
 * Frontend mirror of backend role policy in app.core.auth.
 * Keep in sync with the Depends constants there.
 */
import type { CurrentUser } from "./api";

type RoleHolder = Pick<CurrentUser, "role"> | null | undefined;

function hasRole(user: RoleHolder, roles: readonly string[]): boolean {
  if (!user) return false;
  return roles.includes(user.role);
}

export const can = {
  writePatient: (u: RoleHolder) =>
    hasRole(u, ["admin", "doctor", "receptionist"]),
  writeSymptom: (u: RoleHolder) => hasRole(u, ["admin", "doctor", "nurse"]),
  writeDiagnosis: (u: RoleHolder) => hasRole(u, ["admin", "doctor"]),
  writePrescription: (u: RoleHolder) => hasRole(u, ["admin", "doctor"]),
  writeNote: (u: RoleHolder) => hasRole(u, ["admin", "doctor", "nurse"]),
  writeLabResult: (u: RoleHolder) => hasRole(u, ["admin", "doctor", "nurse"]),
  writeAppointment: (u: RoleHolder) =>
    hasRole(u, ["admin", "doctor", "receptionist"]),
  useClinicalTool: (u: RoleHolder) => hasRole(u, ["admin", "doctor", "nurse"]),
  viewAudit: (u: RoleHolder) => hasRole(u, ["admin"]),
};

import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Sidebar } from "@/components/sidebar";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));
vi.mock("next/navigation", () => ({ usePathname: () => "/dashboard" }));

function asUser(role: string): CurrentUser {
  return {
    id: "1",
    email: "u@x.com",
    full_name: "U",
    role,
    is_active: true,
    patient_id: role === "patient" ? "p1" : null,
  };
}

function renderAs(role: string) {
  vi.mocked(useAuth).mockReturnValue({
    user: asUser(role),
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  });
  return render(<Sidebar />);
}

beforeEach(() => {
  vi.mocked(useAuth).mockReset();
});

describe("Sidebar navigation by role", () => {
  it("shows the full clinician nav for a doctor", () => {
    renderAs("doctor");
    for (const label of [
      "Dashboard",
      "Patients",
      "Appointments",
      "Symptoms",
      "Diagnoses",
      "Prescriptions",
      "Clinical Notes",
      "ICD-10",
    ]) {
      expect(screen.getByRole("link", { name: label })).toBeInTheDocument();
    }
  });

  it("hides admin-only links (Audit, Users, Settings) from a doctor", () => {
    renderAs("doctor");
    expect(screen.queryByRole("link", { name: "Audit Trail" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Users" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Settings" })).not.toBeInTheDocument();
  });

  it("shows admin-only links to an admin", () => {
    renderAs("admin");
    expect(screen.getByRole("link", { name: "Audit Trail" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Users" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Settings" })).toBeInTheDocument();
  });

  it("shows a patient only their portal link, not clinician nav", () => {
    renderAs("patient");
    expect(screen.getByRole("link", { name: "My Records" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Patients" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Prescriptions" })).not.toBeInTheDocument();
  });
});

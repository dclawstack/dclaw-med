import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SymptomsPage from "@/app/symptoms/page";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));
vi.mock("@/lib/api", () => ({ analyzeSymptoms: vi.fn() }));

function asUser(role: string): CurrentUser {
  return { id: "1", email: "a", full_name: "A", role, is_active: true, patient_id: null };
}

beforeEach(() => {
  vi.mocked(useAuth).mockReset();
});

describe("SymptomsPage", () => {
  it("renders the analyzer for a clinician", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser("doctor"),
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<SymptomsPage />);
    expect(
      screen.getByRole("heading", { name: /Symptom Analyzer/i }),
    ).toBeInTheDocument();
  });

  it("renders for a patient without crashing (permission-gated)", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser("patient"),
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<SymptomsPage />);
    expect(
      screen.getByRole("heading", { name: /Symptom Analyzer/i }),
    ).toBeInTheDocument();
  });
});

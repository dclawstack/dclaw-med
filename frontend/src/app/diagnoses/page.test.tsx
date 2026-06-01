import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DiagnosesPage from "@/app/diagnoses/page";
import { useAuth } from "@/components/auth-provider";
import { listDiagnoses, type CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));
vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return { ...actual, listDiagnoses: vi.fn() };
});

function asUser(role: string): CurrentUser {
  return { id: "1", email: "u@x.com", full_name: "U", role, is_active: true, patient_id: null };
}

beforeEach(() => {
  vi.mocked(useAuth).mockReturnValue({
    user: asUser("doctor"),
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  });
  vi.mocked(listDiagnoses).mockResolvedValue([]);
});

describe("DiagnosesPage", () => {
  it("renders the heading and loads diagnoses without crashing", async () => {
    render(<DiagnosesPage />);
    expect(screen.getByRole("heading", { name: /Diagnoses/i })).toBeInTheDocument();
    await waitFor(() => expect(listDiagnoses).toHaveBeenCalled());
  });
});

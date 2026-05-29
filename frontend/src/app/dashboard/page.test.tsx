import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";
import { useAuth } from "@/components/auth-provider";
import {
  listDiagnoses,
  listNotes,
  listPatients,
  listPrescriptions,
} from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));
vi.mock("@/lib/api", () => ({
  listPatients: vi.fn(),
  listPrescriptions: vi.fn(),
  listNotes: vi.fn(),
  listDiagnoses: vi.fn(),
  triage: vi.fn(),
}));

beforeEach(() => {
  vi.mocked(useAuth).mockReturnValue({
    user: { id: "1", email: "a", full_name: "A", role: "admin", is_active: true, patient_id: null },
    loading: false,
    login: vi.fn(),
    logout: vi.fn(),
  });
  vi.mocked(listPatients).mockResolvedValue([]);
  vi.mocked(listPrescriptions).mockResolvedValue([]);
  vi.mocked(listNotes).mockResolvedValue([]);
  vi.mocked(listDiagnoses).mockResolvedValue([]);
});

describe("DashboardPage", () => {
  it("renders the dashboard heading and loads summary data without crashing", async () => {
    render(<DashboardPage />);
    expect(
      screen.getByRole("heading", { name: /DClaw Med/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Clinical intelligence at your fingertips"),
    ).toBeInTheDocument();
    await waitFor(() => expect(listPatients).toHaveBeenCalled());
  });
});

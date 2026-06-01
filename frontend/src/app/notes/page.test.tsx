import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import NotesPage from "@/app/notes/page";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));
vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return { ...actual, generateNote: vi.fn() };
});

function asUser(role: string): CurrentUser {
  return { id: "1", email: "u@x.com", full_name: "U", role, is_active: true, patient_id: null };
}

beforeEach(() => {
  vi.mocked(useAuth).mockReset();
});

describe("NotesPage", () => {
  it("renders the clinical-notes heading for a clinician", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser("doctor"),
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<NotesPage />);
    expect(screen.getByRole("heading", { name: /Clinical Notes/i })).toBeInTheDocument();
  });
});

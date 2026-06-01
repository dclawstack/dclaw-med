import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Navbar } from "@/components/navbar";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));

const logout = vi.fn();

function asUser(overrides: Partial<CurrentUser> = {}): CurrentUser {
  return {
    id: "1",
    email: "doc@clinic.com",
    full_name: "Dr. Jane Stone",
    role: "doctor",
    is_active: true,
    patient_id: null,
    ...overrides,
  };
}

beforeEach(() => {
  logout.mockReset();
});

describe("Navbar", () => {
  it("shows the signed-in user's name and role", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser(),
      loading: false,
      login: vi.fn(),
      logout,
    });
    render(<Navbar />);
    expect(screen.getByText("Dr. Jane Stone")).toBeInTheDocument();
    expect(screen.getByText("doctor")).toBeInTheDocument();
  });

  it("logs out when Sign out is clicked", async () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser(),
      loading: false,
      login: vi.fn(),
      logout,
    });
    render(<Navbar />);
    await userEvent.click(screen.getByRole("button", { name: /sign out/i }));
    expect(logout).toHaveBeenCalledOnce();
  });

  it("renders nothing user-facing when logged out", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      loading: false,
      login: vi.fn(),
      logout,
    });
    render(<Navbar />);
    expect(screen.queryByRole("button", { name: /sign out/i })).not.toBeInTheDocument();
  });
});

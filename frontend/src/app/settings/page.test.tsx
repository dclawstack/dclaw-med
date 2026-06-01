import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SettingsPage from "@/app/settings/page";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));

function asUser(role: string): CurrentUser {
  return { id: "1", email: "u@x.com", full_name: "U", role, is_active: true, patient_id: null };
}

beforeEach(() => {
  vi.mocked(useAuth).mockReset();
});

describe("SettingsPage", () => {
  it("shows settings to an admin", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser("admin"),
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<SettingsPage />);
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
    expect(screen.getByText("API Configuration")).toBeInTheDocument();
  });

  it("restricts settings for non-admins", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: asUser("doctor"),
      loading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });
    render(<SettingsPage />);
    expect(
      screen.getByText(/restricted to administrators/i),
    ).toBeInTheDocument();
    expect(screen.queryByText("API Configuration")).not.toBeInTheDocument();
  });
});

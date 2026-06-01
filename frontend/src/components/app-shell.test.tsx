import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppShell } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import type { CurrentUser } from "@/lib/api";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));

const usePathname = vi.fn();
vi.mock("next/navigation", () => ({ usePathname: () => usePathname() }));

function setAuth(user: CurrentUser | null, loading = false) {
  vi.mocked(useAuth).mockReturnValue({ user, loading, login: vi.fn(), logout: vi.fn() });
}

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

beforeEach(() => {
  vi.mocked(useAuth).mockReset();
  usePathname.mockReset();
});

describe("AppShell", () => {
  it("renders children bare on a public path (no chrome)", () => {
    usePathname.mockReturnValue("/login");
    setAuth(null);
    render(<AppShell><p>public content</p></AppShell>);
    expect(screen.getByText("public content")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /sign out/i })).not.toBeInTheDocument();
  });

  it("shows a loading state while auth resolves", () => {
    usePathname.mockReturnValue("/dashboard");
    setAuth(null, true);
    render(<AppShell><p>protected</p></AppShell>);
    expect(screen.getByText("Loading…")).toBeInTheDocument();
    expect(screen.queryByText("protected")).not.toBeInTheDocument();
  });

  it("renders nothing once unauthenticated on a protected path (pending redirect)", () => {
    usePathname.mockReturnValue("/dashboard");
    setAuth(null, false);
    const { container } = render(<AppShell><p>protected</p></AppShell>);
    expect(container).toBeEmptyDOMElement();
  });

  it("holds rendering for a patient who lands on a clinician path", () => {
    usePathname.mockReturnValue("/patients");
    setAuth(asUser("patient"));
    render(<AppShell><p>clinical</p></AppShell>);
    expect(screen.getByText(/Redirecting to your portal/i)).toBeInTheDocument();
    expect(screen.queryByText("clinical")).not.toBeInTheDocument();
  });

  it("renders the chrome + children for an authenticated clinician", () => {
    usePathname.mockReturnValue("/dashboard");
    setAuth(asUser("doctor"));
    render(<AppShell><p>clinical dashboard</p></AppShell>);
    expect(screen.getByText("clinical dashboard")).toBeInTheDocument();
    // Navbar's sign-out is part of the chrome.
    expect(screen.getByRole("button", { name: /sign out/i })).toBeInTheDocument();
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthProvider, useAuth } from "@/components/auth-provider";
import { getCurrentUser, login as apiLogin } from "@/lib/api";
import { getToken, setToken } from "@/lib/auth-storage";

const replace = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/login",
}));
vi.mock("@/lib/api", () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
}));
vi.mock("@/lib/auth-storage", () => ({
  getToken: vi.fn(),
  setToken: vi.fn(),
  clearToken: vi.fn(),
}));

function Consumer() {
  const { user, loading, login } = useAuth();
  if (loading) return <p>loading</p>;
  return (
    <div>
      <span>role:{user?.role ?? "none"}</span>
      <button onClick={() => login("a@b.com", "pw")}>sign in</button>
    </div>
  );
}

beforeEach(() => {
  vi.mocked(getToken).mockReturnValue(null);
  replace.mockReset();
  vi.mocked(apiLogin).mockReset();
  vi.mocked(getCurrentUser).mockReset();
  vi.mocked(setToken).mockReset();
});

describe("useAuth", () => {
  it("throws when used outside an AuthProvider", () => {
    // Silence the expected React error boundary logging.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<Consumer />)).toThrow(/must be used inside/);
    spy.mockRestore();
  });
});

describe("AuthProvider", () => {
  it("starts unauthenticated when no token is stored", async () => {
    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    );
    expect(await screen.findByText("role:none")).toBeInTheDocument();
  });

  it("logs in: stores the token, loads the user, and redirects", async () => {
    vi.mocked(apiLogin).mockResolvedValue({ access_token: "tok", token_type: "bearer" });
    vi.mocked(getCurrentUser).mockResolvedValue({
      id: "1",
      email: "a@b.com",
      full_name: "A B",
      role: "doctor",
      is_active: true,
      patient_id: null,
    });

    render(
      <AuthProvider>
        <Consumer />
      </AuthProvider>,
    );
    await userEvent.click(await screen.findByRole("button", { name: "sign in" }));

    await waitFor(() => expect(setToken).toHaveBeenCalledWith("tok"));
    expect(apiLogin).toHaveBeenCalledWith("a@b.com", "pw");
    expect(replace).toHaveBeenCalledWith("/dashboard");
    expect(await screen.findByText("role:doctor")).toBeInTheDocument();
  });
});

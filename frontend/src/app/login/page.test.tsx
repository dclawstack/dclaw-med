import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LoginPage from "@/app/login/page";
import { useAuth } from "@/components/auth-provider";

vi.mock("@/components/auth-provider", () => ({ useAuth: vi.fn() }));

const login = vi.fn();

beforeEach(() => {
  login.mockReset();
  vi.mocked(useAuth).mockReturnValue({
    login,
    logout: vi.fn(),
    user: null,
    loading: false,
  });
});

describe("LoginPage", () => {
  it("renders the sign-in form", () => {
    render(<LoginPage />);
    expect(screen.getByText("Sign in to DClaw Med")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("submits the entered credentials", async () => {
    login.mockResolvedValue(undefined);
    render(<LoginPage />);
    await userEvent.type(screen.getByLabelText("Email"), "doc@clinic.com");
    await userEvent.type(screen.getByLabelText("Password"), "secret");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    expect(login).toHaveBeenCalledWith("doc@clinic.com", "secret");
  });

  it("shows an error message when login fails", async () => {
    login.mockRejectedValue(new Error("401 Incorrect email or password"));
    render(<LoginPage />);
    await userEvent.type(screen.getByLabelText("Email"), "doc@clinic.com");
    await userEvent.type(screen.getByLabelText("Password"), "bad");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() =>
      expect(
        screen.getByText("401 Incorrect email or password"),
      ).toBeInTheDocument(),
    );
  });
});

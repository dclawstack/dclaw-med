import { afterEach, describe, expect, it } from "vitest";

import { clearToken, getToken, setToken } from "@/lib/auth-storage";

afterEach(() => {
  window.localStorage.clear();
});

describe("auth-storage", () => {
  it("returns null when no token is stored", () => {
    expect(getToken()).toBeNull();
  });

  it("round-trips a token through localStorage", () => {
    setToken("jwt-123");
    expect(getToken()).toBe("jwt-123");
    expect(window.localStorage.getItem("dclaw_med_token")).toBe("jwt-123");
  });

  it("clears the token", () => {
    setToken("jwt-123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});

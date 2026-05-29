import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiError,
  getCurrentUser,
  listPatients,
  login,
} from "@/lib/api";
import { getToken, setToken } from "@/lib/auth-storage";

function mockFetch(value: {
  ok?: boolean;
  status: number;
  statusText?: string;
  json?: () => unknown;
}) {
  const fn = vi.fn().mockResolvedValue({
    ok: value.ok ?? (value.status >= 200 && value.status < 300),
    status: value.status,
    statusText: value.statusText ?? "",
    json: async () => (value.json ? value.json() : {}),
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

beforeEach(() => {
  window.localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("request()", () => {
  it("parses a JSON body on success", async () => {
    mockFetch({ status: 200, json: () => ({ id: "u1", role: "doctor" }) });
    await expect(getCurrentUser()).resolves.toMatchObject({ id: "u1" });
  });

  it("attaches the bearer token and JSON headers", async () => {
    setToken("tok-xyz");
    const fetchFn = mockFetch({ status: 200, json: () => ({}) });
    await getCurrentUser();
    const [, init] = fetchFn.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer tok-xyz");
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(init.cache).toBe("no-store");
  });

  it("throws ApiError with parsed detail on non-2xx", async () => {
    mockFetch({ status: 400, statusText: "Bad", json: () => ({ detail: "boom" }) });
    await expect(getCurrentUser()).rejects.toMatchObject({
      status: 400,
      message: "400 boom",
    });
  });

  it("clears the token on 401", async () => {
    setToken("stale");
    // Pretend we're already on /login so the helper doesn't navigate.
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { pathname: "/login", href: "" },
    });
    mockFetch({ status: 401, statusText: "Unauthorized", json: () => ({ detail: "nope" }) });
    await expect(getCurrentUser()).rejects.toBeInstanceOf(ApiError);
    expect(getToken()).toBeNull();
  });

  it("builds query strings and skips empty filters", async () => {
    const fetchFn = mockFetch({ status: 200, json: () => [] });
    await listPatients(2, 10, { q: "smith", diagnosis_code: "" });
    const url = fetchFn.mock.calls[0][0] as string;
    expect(url).toContain("page=2");
    expect(url).toContain("page_size=10");
    expect(url).toContain("q=smith");
    expect(url).not.toContain("diagnosis_code");
  });
});

describe("login()", () => {
  it("posts form-urlencoded credentials and returns the token", async () => {
    const fetchFn = mockFetch({
      status: 200,
      json: () => ({ access_token: "abc", token_type: "bearer" }),
    });
    await expect(login("a@b.com", "pw")).resolves.toEqual({
      access_token: "abc",
      token_type: "bearer",
    });
    const [url, init] = fetchFn.mock.calls[0];
    expect(url).toContain("/api/v1/auth/login");
    expect(init.method).toBe("POST");
    expect(init.headers["Content-Type"]).toBe("application/x-www-form-urlencoded");
    expect(init.body.toString()).toContain("username=a%40b.com");
    expect(init.body.toString()).toContain("password=pw");
  });

  it("throws ApiError when credentials are rejected", async () => {
    mockFetch({ status: 401, statusText: "Unauthorized", json: () => ({ detail: "Incorrect email or password" }) });
    await expect(login("a@b.com", "wrong")).rejects.toMatchObject({
      status: 401,
      message: "401 Incorrect email or password",
    });
  });
});

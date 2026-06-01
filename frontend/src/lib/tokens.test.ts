import { describe, expect, it } from "vitest";

import { APP_NAME, APP_TAGLINE, GITHUB_URL } from "@/lib/tokens";

describe("brand tokens", () => {
  it("exposes the product name", () => {
    expect(APP_NAME).toBe("DClaw Med");
  });

  it("has a non-empty tagline", () => {
    expect(APP_TAGLINE.length).toBeGreaterThan(0);
  });

  it("points at the canonical GitHub repo over https", () => {
    expect(GITHUB_URL).toMatch(/^https:\/\/github\.com\/.+/);
  });
});

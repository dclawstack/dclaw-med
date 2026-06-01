import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ICD10Page from "@/app/icd10/page";
import { lookupICD10 } from "@/lib/api";

vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));
vi.mock("@/lib/api", async (importActual) => {
  const actual = await importActual<typeof import("@/lib/api")>();
  return { ...actual, lookupICD10: vi.fn() };
});

beforeEach(() => {
  vi.mocked(lookupICD10).mockReset();
});

describe("ICD10Page", () => {
  it("renders the lookup heading", () => {
    render(<ICD10Page />);
    expect(screen.getByRole("heading", { name: /ICD-10 Lookup/i })).toBeInTheDocument();
  });

  it("queries the API when a search is submitted", async () => {
    vi.mocked(lookupICD10).mockResolvedValue({
      query: "diabetes",
      results: [
        { code: "E11.9", description: "Type 2 diabetes", category: "Endocrine", billable: true },
      ],
      total_found: 1,
    });
    render(<ICD10Page />);
    await userEvent.type(screen.getByRole("textbox"), "diabetes");
    await userEvent.keyboard("{Enter}");
    expect(lookupICD10).toHaveBeenCalledWith(
      expect.objectContaining({ query: "diabetes" }),
    );
  });
});

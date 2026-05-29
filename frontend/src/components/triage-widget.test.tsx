import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TriageWidget } from "@/components/triage-widget";
import { triage, type TriageResponse } from "@/lib/api";

vi.mock("@/lib/api", () => ({ triage: vi.fn() }));
vi.mock("sonner", () => ({ toast: { error: vi.fn(), success: vi.fn() } }));

const mockedTriage = vi.mocked(triage);

const RESULT: TriageResponse = {
  urgency_level: "high",
  suggested_department: "Cardiology",
  recommended_tests: ["ECG", "Troponin"],
  red_flags: ["radiating chest pain"],
  differential_diagnoses: [
    { condition: "ACS", icd10_code: "I20", confidence: 0.82, reasoning: "x" },
  ],
  summary: "Possible acute coronary syndrome.",
  disclaimer: "Not medical advice.",
};

beforeEach(() => {
  mockedTriage.mockReset();
});

describe("TriageWidget", () => {
  it("renders the form with the Triage button disabled until input is entered", () => {
    render(<TriageWidget />);
    expect(screen.getByText("Symptom triage")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /triage/i })).toBeDisabled();
  });

  it("submits the symptoms and renders the triage result", async () => {
    mockedTriage.mockResolvedValue(RESULT);
    render(<TriageWidget />);

    await userEvent.type(
      screen.getByPlaceholderText(/crushing chest pain/i),
      "chest pain",
    );
    await userEvent.click(screen.getByRole("button", { name: /triage/i }));

    expect(mockedTriage).toHaveBeenCalledWith({ symptoms: "chest pain" });
    await waitFor(() =>
      expect(
        screen.getByText("Possible acute coronary syndrome."),
      ).toBeInTheDocument(),
    );
    expect(screen.getByText("HIGH")).toBeInTheDocument();
    expect(screen.getByText("→ Cardiology")).toBeInTheDocument();
    expect(screen.getByText("radiating chest pain")).toBeInTheDocument();
  });

  it("shows an error toast when triage fails", async () => {
    const { toast } = await import("sonner");
    mockedTriage.mockRejectedValue(new Error("server down"));
    render(<TriageWidget />);

    await userEvent.type(screen.getByPlaceholderText(/crushing chest pain/i), "x");
    await userEvent.click(screen.getByRole("button", { name: /triage/i }));

    await waitFor(() =>
      expect(toast.error).toHaveBeenCalledWith("Triage failed", {
        description: "server down",
      }),
    );
  });
});

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders its label", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("applies the destructive variant classes", () => {
    render(<Badge variant="destructive">Critical</Badge>);
    expect(screen.getByText("Critical").className).toContain("text-destructive");
  });

  it("merges a custom className", () => {
    render(<Badge className="custom-x">Tag</Badge>);
    expect(screen.getByText("Tag").className).toContain("custom-x");
  });
});

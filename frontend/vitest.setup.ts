import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// React Testing Library doesn't auto-clean between tests under Vitest's
// non-global afterEach, so unmount explicitly to keep tests isolated.
afterEach(() => {
  cleanup();
});

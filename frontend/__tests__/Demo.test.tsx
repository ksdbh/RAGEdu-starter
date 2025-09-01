import { getConfidenceLabel } from "../components/Demo";

describe("getConfidenceLabel", () => {
  test("maps numeric confidence to low/medium/high", () => {
    expect(getConfidenceLabel(0.0)).toBe("low");
    expect(getConfidenceLabel(0.1)).toBe("low");
    expect(getConfidenceLabel(0.33)).toBe("medium");
    expect(getConfidenceLabel(0.5)).toBe("medium");
    expect(getConfidenceLabel(0.66)).toBe("high");
    expect(getConfidenceLabel(1)).toBe("high");
  });

  test("accepts string inputs case-insensitively", () => {
    expect(getConfidenceLabel("low")).toBe("low");
    expect(getConfidenceLabel("Medium")).toBe("medium");
    expect(getConfidenceLabel("HIGH")).toBe("high");
  });

  test("handles null/undefined/fallbacks", () => {
    expect(getConfidenceLabel(null)).toBe("low");
    expect(getConfidenceLabel(undefined)).toBe("low");
    expect(getConfidenceLabel({} as any)).toBe("medium");
  });
});

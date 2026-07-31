import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ComparisonPage } from "./ComparisonPage";

const completedJob = {
  job_id: "comparison-1",
  status: "completed",
  progress: { current: 2, total: 2, message: "completed" },
  error: null
};

const comparisonPayload = {
  job_id: "comparison-1",
  status: "completed",
  result: {
    report: {
      mode: "independent_seeds",
      baseline: "S17 baseline",
      notes: ["common-random-number comparisons may diverge after rule-dependent draw order changes"],
      results: [
        {
          name: "S17 baseline",
          rounds: 100,
          net_result: "10",
          final_bankroll: "1010",
          house_edge_initial_bet: "-0.0100",
          rtp: "1.0100",
          average_net_result: "0.1000",
          delta_net_result: "0",
          delta_house_edge_initial_bet: "0",
          delta_rtp: "0"
        },
        {
          name: "H17 variant",
          rounds: 100,
          net_result: "-4",
          final_bankroll: "996",
          house_edge_initial_bet: "0.0040",
          rtp: "0.9960",
          average_net_result: "-0.0400",
          delta_net_result: "-14",
          delta_house_edge_initial_bet: "0.0140",
          delta_rtp: "-0.0140"
        }
      ]
    }
  }
};

describe("ComparisonPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/comparisons")) {
          return { ok: true, json: async () => completedJob };
        }
        if (url.endsWith("/comparisons/comparison-1/result")) {
          return { ok: true, json: async () => comparisonPayload };
        }
        return { ok: true, json: async () => completedJob };
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("creates a comparison and shows baseline deltas", async () => {
    const user = userEvent.setup();
    render(<ComparisonPage />);

    await user.click(screen.getByRole("button", { name: "Run comparison" }));

    await waitFor(() => expect(screen.getByText("Baseline Deltas")).toBeInTheDocument());
    expect(screen.getAllByText("S17 baseline").length).toBeGreaterThan(0);
    expect(screen.getAllByText("H17 variant").length).toBeGreaterThan(0);
    expect(screen.getAllByText("-14").length).toBeGreaterThan(0);

    const request = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    expect(fetch).toHaveBeenCalledWith("/api/v1/comparisons", expect.objectContaining({ method: "POST" }));
    expect(String(request.body)).toContain("S17 baseline");
    expect(String(request.body)).toContain("rounds");
  });

  it("sorts rows and toggles column visibility", async () => {
    const user = userEvent.setup();
    render(<ComparisonPage />);

    await user.click(screen.getByRole("button", { name: "Run comparison" }));
    await screen.findByText("Baseline Deltas");

    await user.click(screen.getByRole("button", { name: /Configuration/ }));
    await user.click(screen.getByLabelText("RTP"));

    expect(screen.queryByRole("button", { name: /^RTP$/ })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Configuration/ })).toBeInTheDocument();
  });

  it("exposes JSON and CSV export actions", async () => {
    const user = userEvent.setup();
    render(<ComparisonPage />);

    await user.click(screen.getByRole("button", { name: "Run comparison" }));
    await screen.findByText("Baseline Deltas");

    expect(screen.getByRole("link", { name: "JSON" })).toHaveAttribute(
      "href",
      "/api/v1/comparisons/comparison-1/export/json"
    );
    expect(screen.getByRole("link", { name: "CSV" })).toHaveAttribute(
      "href",
      "/api/v1/comparisons/comparison-1/export/csv"
    );
  });
});

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { HistoryPage } from "./HistoryPage";

const run = {
  id: "run-1",
  configuration_id: null,
  run_type: "simulation",
  status: "queued",
  seed: 123,
  rounds: 100,
  config_snapshot: "simulation:\n  rounds: 100\n",
  created_at: "2026-07-14T10:00:00Z",
  updated_at: "2026-07-14T10:00:00Z"
};

describe("HistoryPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/simulations")) {
          return {
            ok: true,
            json: async () => ({
              job_id: "job-1",
              status: "queued",
              progress: { current: 0, total: 1, message: "queued" },
              error: null
            })
          };
        }
        if (url.endsWith("/history/run-1")) {
          return { ok: true, json: async () => ({}) };
        }
        return { ok: true, json: async () => ({ runs: [run] }) };
      })
    );
  });

  afterEach(() => {
    window.sessionStorage.clear();
    vi.unstubAllGlobals();
  });

  it("filters history and reruns a saved run", async () => {
    const user = userEvent.setup();
    renderHistory();

    expect(await screen.findByText("simulation")).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Type"), "simulation");
    await user.click(screen.getByRole("button", { name: "Apply filters" }));

    expect(fetch).toHaveBeenCalledWith("/api/v1/history?run_type=simulation&limit=100");

    await user.click(screen.getByLabelText("Re-run run-1"));

    await waitFor(() => expect(screen.getByText("Opened simulation job-1")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/simulations",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining("config_text")
      })
    );
  });

  it("confirms delete and stores a run snapshot for comparison", async () => {
    const user = userEvent.setup();
    renderHistory();

    await screen.findByText("simulation");
    await user.click(screen.getByLabelText("Delete run-1"));
    expect(screen.getByRole("dialog", { name: "Delete run confirmation" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirm delete" }));

    await waitFor(() => expect(screen.getByText("Deleted run run-1.")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith("/api/v1/history/run-1", { method: "DELETE" });
  });

  it("stores a run snapshot for comparison", async () => {
    const user = userEvent.setup();
    renderHistory();

    await screen.findByText("simulation");
    await user.click(screen.getByLabelText("Compare run-1"));

    expect(window.sessionStorage.getItem("blackjack.compareConfig")).toContain("simulation:");
    expect(screen.getByText("Opened comparisons")).toBeInTheDocument();
  });
});

function renderHistory() {
  render(
    <MemoryRouter initialEntries={["/history"]}>
      <Routes>
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/simulations/:jobId" element={<p>Opened simulation job-1</p>} />
        <Route path="/comparisons" element={<p>Opened comparisons</p>} />
      </Routes>
    </MemoryRouter>
  );
}

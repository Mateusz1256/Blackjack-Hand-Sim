import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BatchPage } from "./BatchPage";

const runningJob = {
  job_id: "batch-1",
  status: "running",
  progress: { current: 1, total: 2, message: "running_batch" },
  error: null
};

const completedJob = {
  job_id: "batch-1",
  status: "completed",
  progress: { current: 2, total: 2, message: "completed" },
  error: null
};

const cancelledJob = {
  job_id: "batch-1",
  status: "cancelled",
  progress: { current: 1, total: 2, message: "cancelled" },
  error: null
};

const batchPayload = {
  job_id: "batch-1",
  status: "completed",
  result: {
    report: {
      config: { sessions: 3, rounds_per_session: 10, base_seed: 42 },
      sessions_completed: 3,
      ruin_count: 1,
      risk_of_ruin: "0.3333",
      profitable_sessions: 1,
      losing_sessions: 1,
      breakeven_sessions: 1,
      profit_rate: "0.3333",
      loss_rate: "0.3333",
      breakeven_rate: "0.3333",
      average_final_bankroll: "1003.3333",
      median_final_bankroll: "1000",
      min_final_bankroll: "900",
      max_final_bankroll: "1110",
      percentile_final_bankrolls: { "5": "900", "50": "1000", "95": "1110" },
      average_max_drawdown: "60",
      median_max_drawdown: "40",
      percentile_max_drawdowns: { "5": "20", "50": "40", "95": "120" },
      session_results: [
        {
          session_index: 0,
          seed: 42,
          rounds_completed: 10,
          initial_bankroll: "1000",
          final_bankroll: "1110",
          net_result: "110",
          max_drawdown: "20",
          ruined: false
        },
        {
          session_index: 1,
          seed: 43,
          rounds_completed: 10,
          initial_bankroll: "1000",
          final_bankroll: "1000",
          net_result: "0",
          max_drawdown: "40",
          ruined: false
        },
        {
          session_index: 2,
          seed: 44,
          rounds_completed: 10,
          initial_bankroll: "1000",
          final_bankroll: "900",
          net_result: "-100",
          max_drawdown: "120",
          ruined: true
        }
      ]
    }
  }
};

describe("BatchPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/batches") && !url.includes("batch-1")) {
          return { ok: true, json: async () => runningJob };
        }
        if (url.endsWith("/batches/batch-1/cancel")) {
          return { ok: true, json: async () => cancelledJob };
        }
        if (url.endsWith("/batches/batch-1/result")) {
          return { ok: true, json: async () => batchPayload };
        }
        return { ok: true, json: async () => completedJob };
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("validates the batch form before submission", async () => {
    const user = userEvent.setup();
    render(<BatchPage />);

    await user.clear(screen.getByLabelText("Sessions"));
    await user.type(screen.getByLabelText("Sessions"), "0");

    expect(screen.getByText("Sessions must be positive.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run batch" })).toBeDisabled();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("shows progress and cancels an active batch", async () => {
    const user = userEvent.setup();
    render(<BatchPage />);

    await user.click(screen.getByRole("button", { name: "Run batch" }));

    expect(await screen.findByLabelText("Batch progress")).toHaveTextContent("running");

    await user.click(screen.getByRole("button", { name: "Cancel batch" }));

    await waitFor(() => expect(screen.getByLabelText("Batch progress")).toHaveTextContent("cancelled"));
    expect(fetch).toHaveBeenCalledWith("/api/v1/batches/batch-1/cancel", { method: "POST" });
  });

  it("renders distribution charts and session tables after completion", async () => {
    const user = userEvent.setup();
    render(<BatchPage />);

    await user.click(screen.getByRole("button", { name: "Run batch" }));

    expect(await screen.findByText("Distribution Metrics")).toBeInTheDocument();
    expect(screen.getByLabelText("Final bankroll histogram")).toBeInTheDocument();
    expect(screen.getByLabelText("Percentile chart")).toBeInTheDocument();
    expect(screen.getByText("Risk of Ruin")).toBeInTheDocument();
    expect(screen.getByText("Best Sessions")).toBeInTheDocument();
    expect(screen.getByText("Worst Sessions")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "JSON" })).toHaveAttribute(
      "href",
      "/api/v1/batches/batch-1/export/json"
    );
  });
});

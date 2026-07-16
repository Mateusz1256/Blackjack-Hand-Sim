import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ResultsDashboard } from "./ResultsDashboard";

const reportPayload = {
  report: {
    rounds: 25,
    hands: 26,
    initial_bankroll: "1000",
    final_bankroll: "980",
    net_result: "-20",
    total_initial_bet: "250",
    total_action: "270",
    average_net_result: "-0.8",
    sample_variance: "4.2",
    population_variance: "4.0",
    house_edge_initial_bet: "0.08",
    house_edge_total_action: "0.0741",
    rtp: "0.92",
    max_drawdown: "50",
    longest_win_streak: 3,
    longest_loss_streak: 4,
    longest_push_streak: 1
  },
  stop_reason: "completed",
  trace_events: [{ event_type: "round_started", round_index: 0 }]
};

describe("ResultsDashboard", () => {
  it("renders overview metric cards and chart", () => {
    render(<ResultsDashboard result={reportPayload} jobId="job-1" />);

    expect(screen.getByText("Results Dashboard")).toBeInTheDocument();
    expect(screen.getAllByText("Final bankroll").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Downsampled bankroll chart")).toBeInTheDocument();
  });

  it("supports tab navigation", async () => {
    const user = userEvent.setup();
    render(<ResultsDashboard result={reportPayload} />);

    await user.click(screen.getByRole("tab", { name: "Trace" }));

    expect(screen.getByRole("tabpanel")).toHaveTextContent("round_started");
  });

  it("renders an empty state when report data is missing", () => {
    render(<ResultsDashboard result={{ stop_reason: "completed" }} />);

    expect(screen.getByText("No report data")).toBeInTheDocument();
  });
});

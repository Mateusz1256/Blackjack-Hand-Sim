import { describe, expect, it } from "vitest";

import { buildDashboardData, downsamplePoints } from "./resultsModel";

describe("resultsModel", () => {
  it("builds dashboard metrics from a simulation report payload", () => {
    const dashboard = buildDashboardData({
      report: {
        rounds: 100,
        hands: 102,
        initial_bankroll: "1000",
        final_bankroll: "1040",
        net_result: "40",
        total_initial_bet: "1000",
        total_action: "1060",
        average_net_result: "0.4",
        sample_variance: "12.5",
        population_variance: "12.3",
        house_edge_initial_bet: "-0.04",
        house_edge_total_action: "-0.0377",
        rtp: "1.04",
        max_drawdown: "80",
        longest_win_streak: 4,
        longest_loss_streak: 3,
        longest_push_streak: 2
      },
      stop_reason: null,
      trace_events: [{ event_type: "round_started", round_index: 0 }]
    });

    expect(dashboard?.cards).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ label: "Rounds", value: "100" }),
        expect.objectContaining({ label: "Final bankroll", detail: "+40.00 from start" })
      ])
    );
    expect(dashboard?.traceEvents).toHaveLength(1);
  });

  it("returns null for payloads without a report object", () => {
    expect(buildDashboardData({ status: "completed" })).toBeNull();
  });

  it("downsamples large chart datasets to a stable maximum", () => {
    const points = Array.from({ length: 200 }, (_, index) => ({
      label: String(index),
      value: index
    }));

    expect(downsamplePoints(points, 20)).toHaveLength(20);
  });
});

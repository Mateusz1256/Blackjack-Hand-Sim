import { expect, Page } from "@playwright/test";

export const importedConfig = `schema_version: 1
simulation:
  rounds: 7
  seed: 321
  workers: 1
bankroll:
  initial: 100
player:
  betting_strategy:
    type: flat
    amount: 10
  playing_strategy:
    type: basic_strategy
  insurance_strategy:
    type: never
rules:
  decks: 1
  penetration: 0.75
  blackjack_payout: 1.5
  dealer:
    hits_soft_17: false
    peeks_for_blackjack: true
output:
  console: true
`;

export async function mockApi(page: Page) {
  await page.route("**/api/v1/health", async (route) => {
    await route.fulfill({
      json: {
        status: "ok",
        api_version: "v1",
        engine_version: "1.0.0"
      }
    });
  });

  await page.route("**/api/v1/simulations/validate", async (route) => {
    await route.fulfill({
      json: {
        valid: true,
        rounds: 7,
        seed: 321,
        workers: 1
      }
    });
  });

  await page.route("**/api/v1/simulations", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 202,
      json: completedJob("sim-e2e")
    });
  });

  await page.route("**/api/v1/simulations/sim-e2e/result", async (route) => {
    await route.fulfill({
      json: {
        job_id: "sim-e2e",
        status: "completed",
        result: simulationResult()
      }
    });
  });

  await page.route("**/api/v1/simulations/sim-e2e/export/json", async (route) => {
    await route.fulfill({
      body: JSON.stringify({
        schema_version: 1,
        metadata: {
          report_type: "simulation",
          job_id: "sim-e2e"
        },
        report: simulationResult().report
      }),
      contentType: "application/json",
      headers: {
        "content-disposition": 'attachment; filename="simulation-sim-e2e.json"'
      }
    });
  });

  await page.route("**/api/v1/comparisons", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 202,
      json: completedJob("comparison-e2e")
    });
  });

  await page.route("**/api/v1/comparisons/comparison-e2e/result", async (route) => {
    await route.fulfill({
      json: {
        job_id: "comparison-e2e",
        status: "completed",
        result: comparisonResult()
      }
    });
  });

  await page.route("**/api/v1/batches", async (route) => {
    if (route.request().method() !== "POST") {
      await route.continue();
      return;
    }
    await route.fulfill({
      status: 202,
      json: completedJob("batch-e2e")
    });
  });

  await page.route("**/api/v1/batches/batch-e2e/result", async (route) => {
    await route.fulfill({
      json: {
        job_id: "batch-e2e",
        status: "completed",
        result: batchResult()
      }
    });
  });
}

export async function expectBasicAccessibility(page: Page) {
  await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
  await expect(page.locator("main")).toBeVisible();

  const violations = await page.evaluate(() => {
    const issues: string[] = [];
    const namedInteractive = Array.from(
      document.querySelectorAll("button, a[href]")
    ).filter((element) => {
      const label =
        element.getAttribute("aria-label") ??
        element.getAttribute("title") ??
        element.textContent;
      return !label || label.trim().length === 0;
    });
    if (namedInteractive.length > 0) {
      issues.push(`${namedInteractive.length} interactive elements lack names`);
    }

    const unlabeledControls = Array.from(
      document.querySelectorAll("input:not([type='hidden']), select, textarea")
    ).filter((element) => {
      const control = element as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement;
      return control.labels?.length === 0 && !control.getAttribute("aria-label");
    });
    if (unlabeledControls.length > 0) {
      issues.push(`${unlabeledControls.length} form controls lack labels`);
    }

    const ids = Array.from(document.querySelectorAll("[id]")).map((element) => element.id);
    const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
    if (duplicateIds.length > 0) {
      issues.push(`duplicate ids: ${[...new Set(duplicateIds)].join(", ")}`);
    }
    return issues;
  });

  expect(violations).toEqual([]);
}

function completedJob(jobId: string) {
  return {
    job_id: jobId,
    status: "completed",
    progress: {
      current: 2,
      total: 2,
      message: "completed"
    },
    error: null
  };
}

function simulationResult() {
  return {
    report: {
      rounds: 7,
      hands: 7,
      initial_bankroll: "100",
      final_bankroll: "115",
      net_result: "15",
      total_initial_bet: "70",
      total_action: "80",
      average_net_result: "2.1429",
      sample_variance: "4",
      population_variance: "3.5",
      house_edge_initial_bet: "-0.2143",
      house_edge_total_action: "-0.1875",
      rtp: "1.1875",
      max_drawdown: "10",
      longest_win_streak: 2,
      longest_loss_streak: 1,
      longest_push_streak: 1
    },
    report_json: "{}",
    stop_reason: "completed",
    trace_events: [{ event_type: "round_started", round_index: 0 }]
  };
}

function comparisonResult() {
  return {
    report: {
      mode: "independent_seeds",
      baseline: "S17 baseline",
      notes: [],
      results: [
        {
          name: "S17 baseline",
          rounds: 7,
          hands: 7,
          net_result: "15",
          final_bankroll: "115",
          house_edge_initial_bet: "-0.2143",
          house_edge_total_action: "-0.1875",
          rtp: "1.1875",
          average_net_result: "2.1429",
          delta_net_result: "0",
          delta_house_edge_initial_bet: "0",
          delta_house_edge_total_action: "0",
          delta_rtp: "0",
          delta_average_net_result: "0",
          max_drawdown: "10"
        },
        {
          name: "H17 variant",
          rounds: 7,
          hands: 7,
          net_result: "5",
          final_bankroll: "105",
          house_edge_initial_bet: "-0.0714",
          house_edge_total_action: "-0.0625",
          rtp: "1.0625",
          average_net_result: "0.7143",
          delta_net_result: "-10",
          delta_house_edge_initial_bet: "0.1429",
          delta_house_edge_total_action: "0.125",
          delta_rtp: "-0.125",
          delta_average_net_result: "-1.4286",
          max_drawdown: "10"
        }
      ]
    }
  };
}

function batchResult() {
  return {
    report: {
      config: { sessions: 2, rounds_per_session: 3, base_seed: 44 },
      sessions_completed: 2,
      ruin_count: 0,
      risk_of_ruin: "0",
      profitable_sessions: 1,
      losing_sessions: 1,
      breakeven_sessions: 0,
      profit_rate: "0.5",
      loss_rate: "0.5",
      breakeven_rate: "0",
      average_final_bankroll: "102",
      median_final_bankroll: "102",
      min_final_bankroll: "99",
      max_final_bankroll: "105",
      percentile_final_bankrolls: { "5": "99", "50": "102", "95": "105" },
      average_max_drawdown: "8",
      median_max_drawdown: "8",
      percentile_max_drawdowns: { "5": "5", "50": "8", "95": "11" },
      session_results: [
        {
          session_index: 0,
          seed: 44,
          rounds_completed: 3,
          initial_bankroll: "100",
          final_bankroll: "105",
          net_result: "5",
          max_drawdown: "5",
          ruined: false
        },
        {
          session_index: 1,
          seed: 45,
          rounds_completed: 3,
          initial_bankroll: "100",
          final_bankroll: "99",
          net_result: "-1",
          max_drawdown: "11",
          ruined: false
        }
      ]
    }
  };
}

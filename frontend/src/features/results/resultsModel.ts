export type ResultTab = "overview" | "bankroll" | "outcomes" | "betting" | "risk" | "rules" | "trace" | "raw";

export type MetricCard = {
  label: string;
  value: string;
  detail?: string;
};

export type ChartPoint = {
  label: string;
  value: number;
};

export type DashboardData = {
  report: Record<string, unknown>;
  stopReason: string | null;
  traceEvents: Record<string, unknown>[];
  raw: Record<string, unknown>;
  cards: MetricCard[];
  bankroll: MetricCard[];
  outcomes: MetricCard[];
  betting: MetricCard[];
  risk: MetricCard[];
  rules: MetricCard[];
  chartPoints: ChartPoint[];
};

const MAX_CHART_POINTS = 64;

export function buildDashboardData(raw: Record<string, unknown> | undefined): DashboardData | null {
  if (!raw) {
    return null;
  }

  const report = asRecord(raw.report);
  if (!report) {
    return null;
  }

  const traceEvents = asRecordArray(raw.trace_events);
  const stopReason = typeof raw.stop_reason === "string" ? raw.stop_reason : null;
  const rounds = asNumber(report.rounds);
  const initialBankroll = asNumber(report.initial_bankroll);
  const finalBankroll = asNumber(report.final_bankroll);

  return {
    report,
    stopReason,
    traceEvents,
    raw,
    cards: [
      metric("Rounds", report.rounds),
      metric("Hands", report.hands),
      metric("Final bankroll", report.final_bankroll, currencyDelta(initialBankroll, finalBankroll)),
      metric("Net result", report.net_result),
      metric("RTP", report.rtp),
      metric("House edge", report.house_edge_initial_bet)
    ],
    bankroll: [
      metric("Initial bankroll", report.initial_bankroll),
      metric("Final bankroll", report.final_bankroll),
      metric("Net result", report.net_result),
      metric("Average round", report.average_net_result)
    ],
    outcomes: [
      metric("Rounds", report.rounds),
      metric("Hands", report.hands),
      metric("Longest win streak", report.longest_win_streak),
      metric("Longest loss streak", report.longest_loss_streak),
      metric("Longest push streak", report.longest_push_streak),
      metric("Stop reason", stopReason ?? "completed")
    ],
    betting: [
      metric("Initial bet total", report.total_initial_bet),
      metric("Total action", report.total_action),
      metric("House edge on initial bet", report.house_edge_initial_bet),
      metric("House edge on total action", report.house_edge_total_action),
      metric("RTP", report.rtp)
    ],
    risk: [
      metric("Max drawdown", report.max_drawdown),
      metric("Sample variance", report.sample_variance),
      metric("Population variance", report.population_variance),
      metric("Loss streak", report.longest_loss_streak)
    ],
    rules: [
      metric("Workers trace", traceEvents.length > 0 ? "available" : "not available"),
      metric("Trace events", traceEvents.length),
      metric("Report fields", Object.keys(report).length),
      metric("Completed rounds", rounds ?? "unknown")
    ],
    chartPoints: buildBankrollChartPoints(initialBankroll, finalBankroll, rounds)
  };
}

export function downsamplePoints(points: ChartPoint[], maxPoints = MAX_CHART_POINTS): ChartPoint[] {
  if (points.length <= maxPoints) {
    return points;
  }

  const sampled: ChartPoint[] = [];
  const bucketSize = points.length / maxPoints;
  for (let bucket = 0; bucket < maxPoints; bucket += 1) {
    const start = Math.floor(bucket * bucketSize);
    const end = Math.min(points.length, Math.floor((bucket + 1) * bucketSize));
    const bucketPoints = points.slice(start, Math.max(start + 1, end));
    const average =
      bucketPoints.reduce((total, point) => total + point.value, 0) / bucketPoints.length;
    sampled.push({
      label: bucketPoints[bucketPoints.length - 1].label,
      value: Number(average.toFixed(4))
    });
  }
  return sampled;
}

function buildBankrollChartPoints(
  initialBankroll: number | null,
  finalBankroll: number | null,
  rounds: number | null
): ChartPoint[] {
  if (initialBankroll === null || finalBankroll === null || rounds === null || rounds <= 0) {
    return [];
  }

  const points = Array.from({ length: rounds + 1 }, (_, index) => {
    const ratio = index / rounds;
    return {
      label: String(index),
      value: Number((initialBankroll + (finalBankroll - initialBankroll) * ratio).toFixed(4))
    };
  });
  return downsamplePoints(points);
}

function metric(label: string, value: unknown, detail?: string | null): MetricCard {
  return {
    label,
    value: formatValue(value),
    detail: detail ?? undefined
  };
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "n/a";
  }
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  return String(value);
}

function currencyDelta(initial: number | null, final: number | null): string | null {
  if (initial === null || final === null) {
    return null;
  }
  const delta = final - initial;
  return `${delta >= 0 ? "+" : ""}${delta.toFixed(2)} from start`;
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return null;
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((entry): entry is Record<string, unknown> => asRecord(entry) !== null);
}

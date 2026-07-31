export interface BatchSessionRow {
  sessionIndex: number;
  seed: number | null;
  roundsCompleted: number | null;
  initialBankroll: number | null;
  finalBankroll: number | null;
  netResult: number | null;
  maxDrawdown: number | null;
  ruined: boolean;
}

export interface HistogramBin {
  label: string;
  count: number;
}

export interface PercentilePoint {
  percentile: number;
  finalBankroll: number | null;
  maxDrawdown: number | null;
}

export interface BatchData {
  sessionsCompleted: number | null;
  roundsPerSession: number | null;
  baseSeed: number | null;
  ruinCount: number | null;
  riskOfRuin: number | null;
  profitRate: number | null;
  lossRate: number | null;
  breakevenRate: number | null;
  averageFinalBankroll: number | null;
  medianFinalBankroll: number | null;
  minFinalBankroll: number | null;
  maxFinalBankroll: number | null;
  averageMaxDrawdown: number | null;
  medianMaxDrawdown: number | null;
  sampledSessions: BatchSessionRow[];
  bestSessions: BatchSessionRow[];
  worstSessions: BatchSessionRow[];
  histogram: HistogramBin[];
  percentiles: PercentilePoint[];
}

const MAX_SAMPLED_SESSIONS = 160;
const HISTOGRAM_BINS = 12;
const TABLE_ROWS = 5;

export function buildBatchData(raw: Record<string, unknown> | undefined): BatchData | null {
  const report = asRecord(raw?.report);
  if (!report) {
    return null;
  }
  const config = asRecord(report.config);
  const sessions = asRecordArray(report.session_results).map(toSessionRow);
  const sampledSessions = sampleSessions(sessions);
  const byFinalBankroll = [...sessions].sort(
    (left, right) => (right.finalBankroll ?? Number.NEGATIVE_INFINITY) - (left.finalBankroll ?? Number.NEGATIVE_INFINITY)
  );

  return {
    sessionsCompleted: asNumber(report.sessions_completed),
    roundsPerSession: asNumber(config?.rounds_per_session),
    baseSeed: asNumber(config?.base_seed),
    ruinCount: asNumber(report.ruin_count),
    riskOfRuin: asNumber(report.risk_of_ruin),
    profitRate: asNumber(report.profit_rate),
    lossRate: asNumber(report.loss_rate),
    breakevenRate: asNumber(report.breakeven_rate),
    averageFinalBankroll: asNumber(report.average_final_bankroll),
    medianFinalBankroll: asNumber(report.median_final_bankroll),
    minFinalBankroll: asNumber(report.min_final_bankroll),
    maxFinalBankroll: asNumber(report.max_final_bankroll),
    averageMaxDrawdown: asNumber(report.average_max_drawdown),
    medianMaxDrawdown: asNumber(report.median_max_drawdown),
    sampledSessions,
    bestSessions: byFinalBankroll.slice(0, TABLE_ROWS),
    worstSessions: byFinalBankroll.slice(-TABLE_ROWS).reverse(),
    histogram: buildHistogram(sampledSessions),
    percentiles: buildPercentiles(
      asRecord(report.percentile_final_bankrolls),
      asRecord(report.percentile_max_drawdowns)
    )
  };
}

export function formatBatchMetric(value: number | null, digits = 4): string {
  if (value === null) {
    return "n/a";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(digits);
}

export function formatRate(value: number | null): string {
  if (value === null) {
    return "n/a";
  }
  return `${(value * 100).toFixed(2)}%`;
}

function toSessionRow(raw: Record<string, unknown>): BatchSessionRow {
  return {
    sessionIndex: asNumber(raw.session_index) ?? 0,
    seed: asNumber(raw.seed),
    roundsCompleted: asNumber(raw.rounds_completed),
    initialBankroll: asNumber(raw.initial_bankroll),
    finalBankroll: asNumber(raw.final_bankroll),
    netResult: asNumber(raw.net_result),
    maxDrawdown: asNumber(raw.max_drawdown),
    ruined: raw.ruined === true || raw.ruined === "true"
  };
}

function sampleSessions(sessions: BatchSessionRow[]): BatchSessionRow[] {
  if (sessions.length <= MAX_SAMPLED_SESSIONS) {
    return sessions;
  }
  const step = sessions.length / MAX_SAMPLED_SESSIONS;
  return Array.from({ length: MAX_SAMPLED_SESSIONS }, (_, index) => sessions[Math.floor(index * step)]);
}

function buildHistogram(sessions: BatchSessionRow[]): HistogramBin[] {
  const values = sessions
    .map((session) => session.finalBankroll)
    .filter((value): value is number => value !== null);
  if (values.length === 0) {
    return [];
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const counts = Array.from({ length: HISTOGRAM_BINS }, () => 0);
  values.forEach((value) => {
    const index = Math.min(HISTOGRAM_BINS - 1, Math.floor(((value - min) / range) * HISTOGRAM_BINS));
    counts[index] += 1;
  });
  return counts.map((count, index) => {
    const start = min + (range / HISTOGRAM_BINS) * index;
    const end = min + (range / HISTOGRAM_BINS) * (index + 1);
    return {
      label: `${start.toFixed(0)}-${end.toFixed(0)}`,
      count
    };
  });
}

function buildPercentiles(
  finalBankrolls: Record<string, unknown> | null,
  maxDrawdowns: Record<string, unknown> | null
): PercentilePoint[] {
  const keys = new Set([
    ...Object.keys(finalBankrolls ?? {}),
    ...Object.keys(maxDrawdowns ?? {})
  ]);
  return [...keys]
    .map((key) => Number(key))
    .filter((percentile) => Number.isFinite(percentile))
    .sort((left, right) => left - right)
    .map((percentile) => ({
      percentile,
      finalBankroll: asNumber(finalBankrolls?.[String(percentile)]),
      maxDrawdown: asNumber(maxDrawdowns?.[String(percentile)])
    }));
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
  return Array.isArray(value) ? value.filter((entry): entry is Record<string, unknown> => asRecord(entry) !== null) : [];
}

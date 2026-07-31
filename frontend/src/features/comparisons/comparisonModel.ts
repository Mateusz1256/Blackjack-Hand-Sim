export type ComparisonColumnKey =
  | "name"
  | "rounds"
  | "netResult"
  | "finalBankroll"
  | "houseEdge"
  | "rtp"
  | "deltaNetResult"
  | "deltaHouseEdge"
  | "deltaRtp";

export interface ComparisonRow {
  name: string;
  rounds: number | null;
  netResult: number | null;
  finalBankroll: number | null;
  houseEdge: number | null;
  rtp: number | null;
  averageNetResult: number | null;
  deltaNetResult: number | null;
  deltaHouseEdge: number | null;
  deltaRtp: number | null;
  raw: Record<string, unknown>;
}

export interface ComparisonData {
  mode: string;
  baseline: string;
  notes: string[];
  rows: ComparisonRow[];
}

export const COMPARISON_COLUMNS: { key: ComparisonColumnKey; label: string }[] = [
  { key: "name", label: "Configuration" },
  { key: "rounds", label: "Rounds" },
  { key: "netResult", label: "Net result" },
  { key: "finalBankroll", label: "Final bankroll" },
  { key: "houseEdge", label: "House edge" },
  { key: "rtp", label: "RTP" },
  { key: "deltaNetResult", label: "Delta net" },
  { key: "deltaHouseEdge", label: "Delta edge" },
  { key: "deltaRtp", label: "Delta RTP" }
];

export function buildComparisonData(raw: Record<string, unknown> | undefined): ComparisonData | null {
  const report = asRecord(raw?.report);
  if (!report) {
    return null;
  }

  const results = asRecordArray(report.results);
  if (results.length === 0) {
    return null;
  }

  return {
    mode: String(report.mode ?? "unknown"),
    baseline: String(report.baseline ?? results[0]?.name ?? "baseline"),
    notes: asStringArray(report.notes),
    rows: results.map((result, index) => ({
      name: String(result.name ?? `Config ${index + 1}`),
      rounds: asNumber(result.rounds),
      netResult: asNumber(result.net_result),
      finalBankroll: asNumber(result.final_bankroll),
      houseEdge: asNumber(result.house_edge_initial_bet),
      rtp: asNumber(result.rtp),
      averageNetResult: asNumber(result.average_net_result),
      deltaNetResult: asNumber(result.delta_net_result),
      deltaHouseEdge: asNumber(result.delta_house_edge_initial_bet),
      deltaRtp: asNumber(result.delta_rtp),
      raw: result
    }))
  };
}

export function sortedRows(
  rows: ComparisonRow[],
  sortKey: ComparisonColumnKey,
  direction: "asc" | "desc"
): ComparisonRow[] {
  const multiplier = direction === "asc" ? 1 : -1;
  return [...rows].sort((left, right) => {
    const leftValue = valueForSort(left, sortKey);
    const rightValue = valueForSort(right, sortKey);
    if (typeof leftValue === "string" || typeof rightValue === "string") {
      return String(leftValue).localeCompare(String(rightValue)) * multiplier;
    }
    return ((leftValue ?? Number.NEGATIVE_INFINITY) - (rightValue ?? Number.NEGATIVE_INFINITY)) * multiplier;
  });
}

export function formatMetric(value: number | null, digits = 4): string {
  if (value === null) {
    return "n/a";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(digits);
}

export function formatDelta(value: number | null, digits = 4): string {
  if (value === null) {
    return "n/a";
  }
  return `${value >= 0 ? "+" : ""}${formatMetric(value, digits)}`;
}

function valueForSort(row: ComparisonRow, key: ComparisonColumnKey): string | number | null {
  switch (key) {
    case "name":
      return row.name;
    case "rounds":
      return row.rounds;
    case "netResult":
      return row.netResult;
    case "finalBankroll":
      return row.finalBankroll;
    case "houseEdge":
      return row.houseEdge;
    case "rtp":
      return row.rtp;
    case "deltaNetResult":
      return row.deltaNetResult;
    case "deltaHouseEdge":
      return row.deltaHouseEdge;
    case "deltaRtp":
      return row.deltaRtp;
  }
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

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((entry) => String(entry)) : [];
}

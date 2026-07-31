import { ArrowDownUp, BarChart3, CircleAlert, Download, EyeOff, Play, RefreshCw, Table2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  changedConfigurationToYaml,
  configurationToYaml,
  defaultConfigurationState
} from "../configuration/configurationModel";
import {
  comparisonExportUrl,
  ComparisonJobResponse,
  ComparisonMode,
  getComparisonJob,
  getComparisonResult,
  ReportExportFormat,
  startComparison
} from "../../services/apiClient";
import {
  buildComparisonData,
  COMPARISON_COLUMNS,
  ComparisonColumnKey,
  ComparisonRow,
  formatDelta,
  formatMetric,
  sortedRows
} from "./comparisonModel";

type ConfigDraft = {
  name: string;
  text: string;
};

type SortDirection = "asc" | "desc";

const defaultYaml = configurationToYaml(defaultConfigurationState);
const h17Yaml = configurationToYaml({
  ...defaultConfigurationState,
  simulation: {
    ...defaultConfigurationState.simulation,
    seed: 123457
  },
  rules: {
    ...defaultConfigurationState.rules,
    dealerHitsSoft17: true
  }
});

const INITIAL_CONFIGS: ConfigDraft[] = [
  { name: "S17 baseline", text: defaultYaml },
  { name: "H17 variant", text: h17Yaml }
];

const EXPORT_FORMATS: { label: string; format: ReportExportFormat }[] = [
  { label: "JSON", format: "json" },
  { label: "CSV", format: "csv" },
  { label: "ZIP", format: "zip" },
  { label: "PDF", format: "pdf" },
  { label: "SVG", format: "chart.svg" }
];

function initialConfigs(): ConfigDraft[] {
  const stored = window.sessionStorage.getItem("blackjack.compareConfig");
  if (!stored) {
    return INITIAL_CONFIGS;
  }
  window.sessionStorage.removeItem("blackjack.compareConfig");
  return [
    INITIAL_CONFIGS[0],
    {
      name: "History snapshot",
      text: stored
    }
  ];
}

export function ComparisonPage() {
  const [configs, setConfigs] = useState<ConfigDraft[]>(initialConfigs);
  const [baselineIndex, setBaselineIndex] = useState(0);
  const [rounds, setRounds] = useState(10000);
  const [seed, setSeed] = useState(123456);
  const [workers, setWorkers] = useState(1);
  const [mode, setMode] = useState<ComparisonMode>("independent_seeds");
  const [job, setJob] = useState<ComparisonJobResponse | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<ComparisonColumnKey>("deltaNetResult");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");
  const [visibleColumns, setVisibleColumns] = useState<Set<ComparisonColumnKey>>(
    () => new Set(COMPARISON_COLUMNS.map((column) => column.key))
  );

  const comparison = useMemo(() => buildComparisonData(result ?? undefined), [result]);
  const rows = useMemo(
    () => (comparison ? sortedRows(comparison.rows, sortKey, sortDirection) : []),
    [comparison, sortDirection, sortKey]
  );
  const visibleColumnList = COMPARISON_COLUMNS.filter((column) => visibleColumns.has(column.key));

  useEffect(() => {
    if (!job || job.status === "completed" || job.status === "failed" || job.status === "cancelled") {
      return;
    }

    let cancelled = false;
    const timer = window.setInterval(() => {
      void getComparisonJob(job.job_id)
        .then((updatedJob) => {
          if (!cancelled) {
            setJob(updatedJob);
          }
          if (!cancelled && updatedJob.status === "completed") {
            return getComparisonResult(updatedJob.job_id).then((payload) => {
              if (!cancelled) {
                setResult(payload.result);
              }
            });
          }
          return undefined;
        })
        .catch((pollError) => {
          if (!cancelled) {
            setError(pollError instanceof Error ? pollError.message : "Comparison status request failed");
          }
        });
    }, 250);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [job]);

  const updateConfig = (index: number, patch: Partial<ConfigDraft>) => {
    setConfigs((current) => current.map((config, configIndex) => (configIndex === index ? { ...config, ...patch } : config)));
  };

  const runComparison = async () => {
    setError(null);
    setResult(null);
    const orderedConfigs = [...configs];
    const [baseline] = orderedConfigs.splice(baselineIndex, 1);
    const requestConfigs = [baseline, ...orderedConfigs];
    try {
      const started = await startComparison({
        configs: requestConfigs.map((config) => config.text),
        names: requestConfigs.map((config) => config.name),
        mode,
        rounds,
        seed,
        workers
      });
      setJob(started);
      if (started.status === "completed") {
        const payload = await getComparisonResult(started.job_id);
        setResult(payload.result);
      }
    } catch (startError) {
      setError(startError instanceof Error ? startError.message : "Comparison start failed");
    }
  };

  const applyCurrentDefaults = (index: number) => {
    updateConfig(index, {
      text: configurationToYaml(defaultConfigurationState)
    });
  };

  const applyChangedOnly = (index: number) => {
    updateConfig(index, {
      text: changedConfigurationToYaml({
        ...defaultConfigurationState,
        simulation: {
          ...defaultConfigurationState.simulation,
          seed: 123456 + index
        },
        rules: {
          ...defaultConfigurationState.rules,
          dealerHitsSoft17: index === 1
        }
      })
    });
  };

  const toggleSort = (column: ComparisonColumnKey) => {
    if (sortKey === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortKey(column);
      setSortDirection("desc");
    }
  };

  const toggleColumn = (column: ComparisonColumnKey) => {
    setVisibleColumns((current) => {
      const next = new Set(current);
      if (next.has(column) && next.size > 1) {
        next.delete(column);
      } else {
        next.add(column);
      }
      return next;
    });
  };

  return (
    <div className="comparison-layout">
      <section className="panel comparison-setup">
        <div className="panel-heading">
          <h2>Comparison Setup</h2>
          <BarChart3 size={18} aria-hidden="true" />
        </div>
        <div className="field-grid comparison-controls">
          <label className="field">
            Baseline
            <select value={baselineIndex} onChange={(event) => setBaselineIndex(Number(event.target.value))}>
              {configs.map((config, index) => (
                <option key={config.name} value={index}>
                  {config.name || `Config ${index + 1}`}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            Mode
            <select value={mode} onChange={(event) => setMode(event.target.value as ComparisonMode)}>
              <option value="independent_seeds">Independent seeds</option>
              <option value="common_random_numbers">Common random numbers</option>
            </select>
          </label>
          <label className="field">
            Rounds
            <input min={1} type="number" value={rounds} onChange={(event) => setRounds(Number(event.target.value))} />
          </label>
          <label className="field">
            Seed
            <input min={0} type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} />
          </label>
          <label className="field">
            Workers
            <input min={1} type="number" value={workers} onChange={(event) => setWorkers(Number(event.target.value))} />
          </label>
        </div>
        <p className="muted comparison-note">
          Common random numbers reduce seed noise only when configuration differences keep comparable draw order; rule changes such as ENHC, splits, or insurance can still diverge.
        </p>
        <button className="primary-button" type="button" onClick={runComparison} disabled={configs.some((config) => config.text.trim() === "") || rounds < 1 || workers < 1}>
          <Play size={16} aria-hidden="true" />
          Run comparison
        </button>
        {job && <JobProgressView job={job} />}
        {error && (
          <p className="status-error">
            <CircleAlert size={15} aria-hidden="true" />
            {error}
          </p>
        )}
      </section>

      <section className="comparison-config-grid" aria-label="Comparison configurations">
        {configs.map((config, index) => (
          <div className="panel form-section" key={index === 0 ? "baseline" : "variant"}>
            <div className="panel-heading">
              <h2>{index === baselineIndex ? "Baseline config" : `Config ${index + 1}`}</h2>
              <button className="icon-button" type="button" aria-label={`Use current defaults for config ${index + 1}`} title="Use current defaults" onClick={() => applyCurrentDefaults(index)}>
                <RefreshCw size={16} aria-hidden="true" />
              </button>
            </div>
            <label className="field">
              Name
              <input value={config.name} onChange={(event) => updateConfig(index, { name: event.target.value })} />
            </label>
            <label className="field file-field">
              Config text
              <textarea rows={16} value={config.text} onChange={(event) => updateConfig(index, { text: event.target.value })} />
            </label>
            <button className="secondary-button full-width-button" type="button" onClick={() => applyChangedOnly(index)}>
              Load changed-only sample
            </button>
          </div>
        ))}
      </section>

      {comparison && (
        <section className="comparison-results">
          <div className="results-hero">
            <div>
              <p className="eyebrow">Completed comparison</p>
              <h2>Baseline Deltas</h2>
              <p className="muted">Baseline {comparison.baseline} in {comparison.mode}</p>
            </div>
            {job && (
              <div className="export-actions" aria-label="Comparison export actions">
                {EXPORT_FORMATS.map((entry) => (
                  <a className="result-link" href={comparisonExportUrl(job.job_id, entry.format)} key={entry.format}>
                    <Download size={16} aria-hidden="true" />
                    {entry.label}
                  </a>
                ))}
              </div>
            )}
          </div>

          {comparison.notes.length > 0 && (
            <ul className="issue-list">
              {comparison.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          )}

          <section className="panel">
            <div className="panel-heading">
              <h2>Columns</h2>
              <EyeOff size={18} aria-hidden="true" />
            </div>
            <div className="column-toggle-grid">
              {COMPARISON_COLUMNS.map((column) => (
                <label className="toggle-field" key={column.key}>
                  <input checked={visibleColumns.has(column.key)} type="checkbox" onChange={() => toggleColumn(column.key)} />
                  {column.label}
                </label>
              ))}
            </div>
          </section>

          <section className="panel tab-panel">
            <div className="panel-heading">
              <h2>Comparison Table</h2>
              <Table2 size={18} aria-hidden="true" />
            </div>
            <div className="table-scroll">
              <table className="data-table comparison-table">
                <thead>
                  <tr>
                    {visibleColumnList.map((column) => (
                      <th scope="col" key={column.key}>
                        <button type="button" onClick={() => toggleSort(column.key)}>
                          {column.label}
                          <ArrowDownUp size={14} aria-hidden="true" />
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => (
                    <tr key={row.name}>
                      {visibleColumnList.map((column) => (
                        <td key={column.key}>{renderCell(row, column.key)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading">
              <h2>Delta Chart</h2>
              <BarChart3 size={18} aria-hidden="true" />
            </div>
            <DeltaChart rows={comparison.rows} />
          </section>
        </section>
      )}
    </div>
  );
}

function JobProgressView({ job }: { job: ComparisonJobResponse }) {
  const percent = job.progress.total > 0 ? Math.round((job.progress.current / job.progress.total) * 100) : 0;
  return (
    <div className="job-status" aria-label="Comparison progress">
      <div className="metric-list compact">
        <div>
          <dt>Status</dt>
          <dd>{job.status}</dd>
        </div>
        <div>
          <dt>Step</dt>
          <dd>{job.progress.message}</dd>
        </div>
      </div>
      <div className="progress-track" aria-label="Progress">
        <span style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

function renderCell(row: ComparisonRow, column: ComparisonColumnKey) {
  switch (column) {
    case "name":
      return row.name;
    case "rounds":
      return formatMetric(row.rounds, 0);
    case "netResult":
      return formatMetric(row.netResult);
    case "finalBankroll":
      return formatMetric(row.finalBankroll);
    case "houseEdge":
      return formatMetric(row.houseEdge);
    case "rtp":
      return formatMetric(row.rtp);
    case "deltaNetResult":
      return formatDelta(row.deltaNetResult);
    case "deltaHouseEdge":
      return formatDelta(row.deltaHouseEdge);
    case "deltaRtp":
      return formatDelta(row.deltaRtp);
  }
}

function DeltaChart({ rows }: { rows: ComparisonRow[] }) {
  const max = Math.max(1, ...rows.map((row) => Math.abs(row.deltaNetResult ?? 0)));
  return (
    <div className="delta-chart" aria-label="Net result delta chart">
      {rows.map((row) => {
        const delta = row.deltaNetResult ?? 0;
        return (
          <div className="delta-row" key={row.name}>
            <span>{row.name}</span>
            <div className="delta-track">
              <i className={delta >= 0 ? "positive" : "negative"} style={{ width: `${Math.max(4, (Math.abs(delta) / max) * 100)}%` }} />
            </div>
            <strong>{formatDelta(row.deltaNetResult)}</strong>
          </div>
        );
      })}
    </div>
  );
}

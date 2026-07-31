import { BarChart3, CircleAlert, Download, Play, RefreshCw, ShieldAlert, Square, Table2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { configurationToYaml, defaultConfigurationState } from "../configuration/configurationModel";
import {
  batchExportUrl,
  BatchJobResponse,
  cancelBatch,
  getBatchJob,
  getBatchResult,
  startBatch
} from "../../services/apiClient";
import { BatchData, BatchSessionRow, buildBatchData, formatBatchMetric, formatRate } from "./batchModel";

const DEFAULT_CONFIG_TEXT = configurationToYaml({
  ...defaultConfigurationState,
  simulation: {
    ...defaultConfigurationState.simulation,
    rounds: 1000
  }
});

export function BatchPage() {
  const [configText, setConfigText] = useState(DEFAULT_CONFIG_TEXT);
  const [sessions, setSessions] = useState(25);
  const [roundsPerSession, setRoundsPerSession] = useState(1000);
  const [baseSeed, setBaseSeed] = useState(123456);
  const [job, setJob] = useState<BatchJobResponse | null>(null);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  const batch = useMemo(() => buildBatchData(result ?? undefined), [result]);
  const formErrors = buildFormErrors(configText, sessions, roundsPerSession);
  const isActiveJob = job?.status === "queued" || job?.status === "running";

  useEffect(() => {
    if (!job || !isPolling || !isActiveJob) {
      return;
    }

    let cancelled = false;
    const timer = window.setInterval(() => {
      void getBatchJob(job.job_id)
        .then((updatedJob) => {
          if (cancelled) {
            return undefined;
          }
          if (updatedJob.status === "completed") {
            return getBatchResult(updatedJob.job_id).then((payload) => {
              if (!cancelled) {
                setJob(updatedJob);
                setResult(payload.result);
                setIsPolling(false);
              }
            });
          }
          setJob(updatedJob);
          if (updatedJob.status === "failed" || updatedJob.status === "cancelled") {
            setIsPolling(false);
          }
          return undefined;
        })
        .catch((pollError) => {
          if (!cancelled) {
            setError(pollError instanceof Error ? pollError.message : "Batch status request failed");
            setIsPolling(false);
          }
        });
    }, 250);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [isActiveJob, isPolling, job]);

  const runBatch = async () => {
    if (formErrors.length > 0) {
      return;
    }
    setError(null);
    setResult(null);
    try {
      const started = await startBatch({
        config_text: configText,
        sessions,
        rounds_per_session: roundsPerSession,
        base_seed: baseSeed
      });
      setJob(started);
      if (started.status === "completed") {
        const payload = await getBatchResult(started.job_id);
        setResult(payload.result);
      } else {
        setIsPolling(true);
      }
    } catch (startError) {
      setError(startError instanceof Error ? startError.message : "Batch start failed");
    }
  };

  const cancelActiveBatch = async () => {
    if (!job) {
      return;
    }
    setError(null);
    try {
      const cancelledJob = await cancelBatch(job.job_id);
      setJob(cancelledJob);
      setIsPolling(false);
    } catch (cancelError) {
      setError(cancelError instanceof Error ? cancelError.message : "Batch cancel failed");
    }
  };

  return (
    <div className="batch-layout">
      <section className="panel batch-setup">
        <div className="panel-heading">
          <h2>Batch Setup</h2>
          <BarChart3 size={18} aria-hidden="true" />
        </div>
        <div className="field-grid batch-controls">
          <label className="field">
            Sessions
            <input min={1} type="number" value={sessions} onChange={(event) => setSessions(Number(event.target.value))} />
          </label>
          <label className="field">
            Rounds per session
            <input min={1} type="number" value={roundsPerSession} onChange={(event) => setRoundsPerSession(Number(event.target.value))} />
          </label>
          <label className="field">
            Base seed
            <input min={0} type="number" value={baseSeed} onChange={(event) => setBaseSeed(Number(event.target.value))} />
          </label>
        </div>
        <label className="field">
          Config text
          <textarea rows={18} value={configText} onChange={(event) => setConfigText(event.target.value)} />
        </label>
        {formErrors.length > 0 && (
          <ul className="issue-list" aria-label="Batch form errors">
            {formErrors.map((formError) => (
              <li key={formError}>{formError}</li>
            ))}
          </ul>
        )}
        <div className="button-row">
          <button className="primary-button" type="button" onClick={runBatch} disabled={formErrors.length > 0 || isActiveJob}>
            <Play size={16} aria-hidden="true" />
            Run batch
          </button>
          <button className="secondary-button full-width-button" type="button" onClick={cancelActiveBatch} disabled={!isActiveJob}>
            <Square size={16} aria-hidden="true" />
            Cancel batch
          </button>
        </div>
        {job && <BatchProgress job={job} />}
        {error && (
          <p className="status-error">
            <CircleAlert size={15} aria-hidden="true" />
            {error}
          </p>
        )}
      </section>

      {batch && job && <BatchResults batch={batch} jobId={job.job_id} />}
    </div>
  );
}

function BatchResults({ batch, jobId }: { batch: BatchData; jobId: string }) {
  return (
    <section className="batch-results">
      <div className="results-hero">
        <div>
          <p className="eyebrow">Completed batch</p>
          <h2>Distribution Metrics</h2>
          <p className="muted">
            {formatBatchMetric(batch.sessionsCompleted, 0)} sessions, {formatBatchMetric(batch.roundsPerSession, 0)} rounds each
          </p>
        </div>
        <div className="export-actions" aria-label="Batch export actions">
          <a className="result-link" href={batchExportUrl(jobId, "json")}>
            <Download size={16} aria-hidden="true" />
            JSON
          </a>
          <a className="result-link" href={batchExportUrl(jobId, "csv")}>
            <Download size={16} aria-hidden="true" />
            CSV
          </a>
        </div>
      </div>

      <dl className="metric-card-grid">
        <MetricCard label="Risk of ruin" value={formatRate(batch.riskOfRuin)} detail={`${formatBatchMetric(batch.ruinCount, 0)} ruined sessions`} />
        <MetricCard label="Profit rate" value={formatRate(batch.profitRate)} detail={`Loss ${formatRate(batch.lossRate)}`} />
        <MetricCard label="Median bankroll" value={formatBatchMetric(batch.medianFinalBankroll)} detail={`Average ${formatBatchMetric(batch.averageFinalBankroll)}`} />
        <MetricCard label="Bankroll range" value={formatBatchMetric(batch.minFinalBankroll)} detail={`Max ${formatBatchMetric(batch.maxFinalBankroll)}`} />
        <MetricCard label="Median drawdown" value={formatBatchMetric(batch.medianMaxDrawdown)} detail={`Average ${formatBatchMetric(batch.averageMaxDrawdown)}`} />
        <MetricCard label="Base seed" value={formatBatchMetric(batch.baseSeed, 0)} detail={`Breakeven ${formatRate(batch.breakevenRate)}`} />
      </dl>

      <section className="panel">
        <div className="panel-heading">
          <h2>Final Bankroll Histogram</h2>
          <BarChart3 size={18} aria-hidden="true" />
        </div>
        <Histogram bins={batch.histogram} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Percentiles</h2>
          <RefreshCw size={18} aria-hidden="true" />
        </div>
        <PercentileChart batch={batch} />
      </section>

      <section className="panel risk-panel">
        <div className="panel-heading">
          <h2>Risk of Ruin</h2>
          <ShieldAlert size={18} aria-hidden="true" />
        </div>
        <div className="risk-meter" aria-label="Risk of ruin meter">
          <span style={{ width: `${Math.min(100, Math.max(0, (batch.riskOfRuin ?? 0) * 100))}%` }} />
        </div>
        <p className="muted">
          Ruin is reported by the engine per independent session. This view summarizes completed sessions only.
        </p>
      </section>

      <section className="batch-table-grid">
        <SessionTable title="Best Sessions" rows={batch.bestSessions} />
        <SessionTable title="Worst Sessions" rows={batch.worstSessions} />
      </section>
    </section>
  );
}

function BatchProgress({ job }: { job: BatchJobResponse }) {
  const percent = job.progress.total > 0 ? Math.round((job.progress.current / job.progress.total) * 100) : 0;
  return (
    <div className="job-status" aria-label="Batch progress">
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

function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="metric-card">
      <dt>{label}</dt>
      <dd>{value}</dd>
      <span>{detail}</span>
    </div>
  );
}

function Histogram({ bins }: { bins: { label: string; count: number }[] }) {
  if (bins.length === 0) {
    return <p className="muted">No session data is available.</p>;
  }
  const max = Math.max(1, ...bins.map((bin) => bin.count));
  return (
    <div className="histogram-chart" aria-label="Final bankroll histogram">
      {bins.map((bin) => (
        <div key={bin.label}>
          <span title={`${bin.label}: ${bin.count}`} style={{ height: `${Math.max(6, (bin.count / max) * 100)}%` }} />
          <small>{bin.label}</small>
        </div>
      ))}
    </div>
  );
}

function PercentileChart({ batch }: { batch: BatchData }) {
  if (batch.percentiles.length === 0) {
    return <p className="muted">No percentile data is available.</p>;
  }
  return (
    <div className="percentile-chart" aria-label="Percentile chart">
      {batch.percentiles.map((point) => (
        <div key={point.percentile}>
          <span>p{point.percentile}</span>
          <strong>{formatBatchMetric(point.finalBankroll)}</strong>
          <em>{formatBatchMetric(point.maxDrawdown)}</em>
        </div>
      ))}
    </div>
  );
}

function SessionTable({ title, rows }: { title: string; rows: BatchSessionRow[] }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>{title}</h2>
        <Table2 size={18} aria-hidden="true" />
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th scope="col">Session</th>
            <th scope="col">Seed</th>
            <th scope="col">Final bankroll</th>
            <th scope="col">Net</th>
            <th scope="col">Drawdown</th>
            <th scope="col">Ruin</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${title}-${row.sessionIndex}`}>
              <td>{row.sessionIndex}</td>
              <td>{formatBatchMetric(row.seed, 0)}</td>
              <td>{formatBatchMetric(row.finalBankroll)}</td>
              <td>{formatBatchMetric(row.netResult)}</td>
              <td>{formatBatchMetric(row.maxDrawdown)}</td>
              <td>{row.ruined ? "yes" : "no"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function buildFormErrors(configText: string, sessions: number, roundsPerSession: number): string[] {
  const errors: string[] = [];
  if (configText.trim() === "") {
    errors.push("Config text is required.");
  }
  if (!Number.isFinite(sessions) || sessions <= 0) {
    errors.push("Sessions must be positive.");
  }
  if (!Number.isFinite(roundsPerSession) || roundsPerSession <= 0) {
    errors.push("Rounds per session must be positive.");
  }
  return errors;
}

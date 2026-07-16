import { CircleAlert, Loader2, Play, Square, ExternalLink } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  cancelSimulation,
  getSimulationJob,
  SimulationJobResponse,
  startSimulation
} from "../../services/apiClient";

const TERMINAL_STATUSES = new Set(["completed", "failed", "cancelled"]);

type SimulationRunPanelProps = {
  configText: string;
  disabledReason?: string;
  pollIntervalMs?: number;
};

export function SimulationRunPanel({
  configText,
  disabledReason,
  pollIntervalMs = 1000
}: SimulationRunPanelProps) {
  const [job, setJob] = useState<SimulationJobResponse | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const progressPercent = useMemo(() => {
    if (!job) {
      return 0;
    }
    return Math.round((job.progress.current / job.progress.total) * 100);
  }, [job]);

  const isActive = job ? !TERMINAL_STATUSES.has(job.status) : false;

  useEffect(() => {
    if (!job || !isActive) {
      return undefined;
    }

    const poll = async () => {
      try {
        const nextJob = await getSimulationJob(job.job_id);
        setJob(nextJob);
      } catch (pollError) {
        setError(pollError instanceof Error ? pollError.message : "Simulation status request failed");
      }
    };

    const intervalId = window.setInterval(poll, pollIntervalMs);
    return () => window.clearInterval(intervalId);
  }, [job, isActive, pollIntervalMs]);

  const runSimulation = async () => {
    setError(null);
    setIsStarting(true);
    try {
      const startedJob = await startSimulation(configText);
      setJob(startedJob);
    } catch (startError) {
      setError(startError instanceof Error ? startError.message : "Simulation start failed");
    } finally {
      setIsStarting(false);
    }
  };

  const cancelCurrentSimulation = async () => {
    if (!job) {
      return;
    }
    setError(null);
    setIsCancelling(true);
    try {
      const cancelledJob = await cancelSimulation(job.job_id);
      setJob(cancelledJob);
    } catch (cancelError) {
      setError(cancelError instanceof Error ? cancelError.message : "Simulation cancel failed");
    } finally {
      setIsCancelling(false);
    }
  };

  return (
    <section className="panel simulation-panel">
      <div className="panel-heading">
        <h2>Run Simulation</h2>
        {isActive ? <Loader2 className="spin-icon" size={18} aria-hidden="true" /> : <Play size={18} aria-hidden="true" />}
      </div>
      <button
        className="primary-button"
        type="button"
        disabled={Boolean(disabledReason) || isStarting || isActive}
        onClick={runSimulation}
      >
        <Play size={16} aria-hidden="true" />
        {isStarting ? "Starting" : "Start run"}
      </button>
      {disabledReason && <p className="muted">{disabledReason}</p>}
      {job && (
        <div className="job-status" aria-label="Simulation status">
          <dl className="metric-list compact">
            <div>
              <dt>Status</dt>
              <dd>{job.status}</dd>
            </div>
            <div>
              <dt>Progress</dt>
              <dd>{progressPercent}%</dd>
            </div>
            <div>
              <dt>Message</dt>
              <dd>{job.progress.message}</dd>
            </div>
          </dl>
          <div className="progress-track" aria-label="Simulation progress">
            <span style={{ width: `${progressPercent}%` }} />
          </div>
          {isActive && (
            <button
              className="secondary-button full-width-button"
              type="button"
              disabled={isCancelling}
              onClick={cancelCurrentSimulation}
            >
              <Square size={15} aria-hidden="true" />
              {isCancelling ? "Cancelling" : "Cancel run"}
            </button>
          )}
          {job.status === "completed" && (
            <Link className="result-link" to={`/simulations/${job.job_id}`}>
              <ExternalLink size={15} aria-hidden="true" />
              Open result
            </Link>
          )}
          {job.error && <p className="status-error">{job.error}</p>}
        </div>
      )}
      {error && (
        <p className="status-error">
          <CircleAlert size={15} aria-hidden="true" />
          {error}
        </p>
      )}
    </section>
  );
}

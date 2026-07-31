import { Download, GitCompare, Play, RefreshCw, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  deleteHistoryRun,
  listRunHistory,
  RunHistoryRecord,
  startSimulation
} from "../../services/apiClient";

export function HistoryPage() {
  const navigate = useNavigate();
  const [runs, setRuns] = useState<RunHistoryRecord[]>([]);
  const [runType, setRunType] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<RunHistoryRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const loadRuns = async () => {
    setError(null);
    try {
      const payload = await listRunHistory({
        runType: runType || undefined,
        status: statusFilter || undefined,
        limit: 100
      });
      setRuns(payload.runs);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "History list failed");
    }
  };

  useEffect(() => {
    void loadRuns();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rerun = async (run: RunHistoryRecord) => {
    setError(null);
    try {
      const job = await startSimulation(run.config_snapshot);
      navigate(`/simulations/${job.job_id}`);
    } catch (rerunError) {
      setError(rerunError instanceof Error ? rerunError.message : "Run restart failed");
    }
  };

  const compare = (run: RunHistoryRecord) => {
    window.sessionStorage.setItem("blackjack.compareConfig", run.config_snapshot);
    navigate("/comparisons");
  };

  const exportSnapshot = (run: RunHistoryRecord) => {
    const blob = new Blob([run.config_snapshot], { type: "application/x-yaml" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${run.run_type}-${run.id}.yaml`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const confirmDelete = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await deleteHistoryRun(deleteTarget.id);
      setMessage(`Deleted run ${deleteTarget.id}.`);
      setDeleteTarget(null);
      await loadRuns();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "History delete failed");
    }
  };

  return (
    <div className="history-layout">
      <section className="panel">
        <div className="panel-heading">
          <h2>Run History</h2>
          <button className="icon-button" type="button" aria-label="Refresh history" title="Refresh history" onClick={() => void loadRuns()}>
            <RefreshCw size={16} aria-hidden="true" />
          </button>
        </div>
        <div className="field-grid history-filters">
          <label className="field">
            Type
            <select value={runType} onChange={(event) => setRunType(event.target.value)}>
              <option value="">All</option>
              <option value="simulation">Simulation</option>
              <option value="comparison">Comparison</option>
              <option value="batch">Batch</option>
            </select>
          </label>
          <label className="field">
            Status
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="">All</option>
              <option value="queued">Queued</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </label>
          <button className="secondary-button" type="button" onClick={() => void loadRuns()}>
            Apply filters
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">Created</th>
                <th scope="col">Type</th>
                <th scope="col">Status</th>
                <th scope="col">Seed</th>
                <th scope="col">Rounds</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td>{new Date(run.created_at).toLocaleString()}</td>
                  <td>{run.run_type}</td>
                  <td>{run.status}</td>
                  <td>{run.seed ?? "n/a"}</td>
                  <td>{run.rounds ?? "n/a"}</td>
                  <td>
                    <div className="row-actions">
                      <button type="button" aria-label={`Re-run ${run.id}`} onClick={() => void rerun(run)}>
                        <Play size={15} aria-hidden="true" />
                      </button>
                      <button type="button" aria-label={`Compare ${run.id}`} onClick={() => compare(run)}>
                        <GitCompare size={15} aria-hidden="true" />
                      </button>
                      <button type="button" aria-label={`Export ${run.id}`} onClick={() => exportSnapshot(run)}>
                        <Download size={15} aria-hidden="true" />
                      </button>
                      <button type="button" aria-label={`Delete ${run.id}`} onClick={() => setDeleteTarget(run)}>
                        <Trash2 size={15} aria-hidden="true" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {runs.length === 0 && <p className="muted">No history entries match the current filters.</p>}
      </section>

      {deleteTarget && (
        <section className="confirm-panel" role="dialog" aria-label="Delete run confirmation">
          <div className="panel">
            <h2>Delete run?</h2>
            <p className="muted">{deleteTarget.id}</p>
            <div className="button-row">
              <button className="secondary-button" type="button" onClick={() => setDeleteTarget(null)}>
                Cancel
              </button>
              <button className="primary-button" type="button" onClick={confirmDelete}>
                Confirm delete
              </button>
            </div>
          </div>
        </section>
      )}

      {message && <p className="status-success">{message}</p>}
      {error && <p className="status-error">{error}</p>}
    </div>
  );
}

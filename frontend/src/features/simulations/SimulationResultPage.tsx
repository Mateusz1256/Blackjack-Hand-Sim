import { CircleAlert, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getSimulationResult, SimulationResultResponse } from "../../services/apiClient";

export function SimulationResultPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [result, setResult] = useState<SimulationResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const loadResult = async () => {
      if (!jobId) {
        setError("Missing simulation job id");
        setIsLoading(false);
        return;
      }
      setIsLoading(true);
      setError(null);
      try {
        const payload = await getSimulationResult(jobId);
        if (!cancelled) {
          setResult(payload);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(loadError instanceof Error ? loadError.message : "Simulation result request failed");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadResult();
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  const summary = useMemo(() => buildResultSummary(result?.result), [result]);

  return (
    <div className="result-layout">
      <section className="panel">
        <div className="panel-heading">
          <h2>Simulation Result</h2>
          {isLoading && <RefreshCw className="spin-icon" size={18} aria-hidden="true" />}
        </div>
        {jobId && <p className="muted">Job {jobId}</p>}
        {isLoading && <p className="muted">Loading result.</p>}
        {error && (
          <p className="status-error">
            <CircleAlert size={15} aria-hidden="true" />
            {error}
          </p>
        )}
        {result && (
          <>
            <dl className="metric-list result-summary">
              {summary.map((entry) => (
                <div key={entry.label}>
                  <dt>{entry.label}</dt>
                  <dd>{entry.value}</dd>
                </div>
              ))}
            </dl>
            <pre className="result-json">{JSON.stringify(result.result, null, 2)}</pre>
          </>
        )}
        <Link className="text-link" to="/configuration">
          Back to configuration
        </Link>
      </section>
    </div>
  );
}

function buildResultSummary(result: Record<string, unknown> | undefined) {
  if (!result) {
    return [];
  }

  return [
    ["Rounds", result.rounds],
    ["Final bankroll", result.final_bankroll],
    ["Net result", result.net_result],
    ["House edge", result.house_edge],
    ["RTP", result.rtp]
  ]
    .filter(([, value]) => value !== undefined && value !== null)
    .map(([label, value]) => ({
      label: String(label),
      value: String(value)
    }));
}

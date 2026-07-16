import { CircleAlert, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ResultsDashboard } from "../results/ResultsDashboard";
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
        <Link className="text-link" to="/configuration">
          Back to configuration
        </Link>
      </section>
      {result && <ResultsDashboard result={result.result} jobId={jobId} />}
    </div>
  );
}

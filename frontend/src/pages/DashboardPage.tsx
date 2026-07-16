import { useEffect, useState } from "react";

import { getHealth, HealthResponse } from "../services/apiClient";

export function DashboardPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getHealth()
      .then((response) => {
        if (mounted) {
          setHealth(response);
          setError(null);
        }
      })
      .catch(() => {
        if (mounted) {
          setHealth(null);
          setError("Backend unavailable");
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="dashboard-grid">
      <section className="panel">
        <h2>Backend Health</h2>
        <dl className="metric-list">
          <div>
            <dt>Status</dt>
            <dd>{health?.status ?? (error ? "offline" : "checking")}</dd>
          </div>
          <div>
            <dt>API</dt>
            <dd>{health?.api_version ?? "-"}</dd>
          </div>
          <div>
            <dt>Engine</dt>
            <dd>{health?.engine_version ?? "-"}</dd>
          </div>
        </dl>
      </section>
      <section className="panel">
        <h2>Workflows</h2>
        <div className="workflow-list">
          <span>Simulations</span>
          <span>Comparisons</span>
          <span>Batches</span>
          <span>Audits</span>
        </div>
      </section>
    </div>
  );
}

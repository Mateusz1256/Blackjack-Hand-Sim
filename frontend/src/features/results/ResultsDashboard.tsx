import { Activity, BarChart3, CircleAlert, Database, Download, FileJson, ScrollText, Shield, Table2, Wallet } from "lucide-react";
import { useMemo, useState } from "react";

import { ReportExportFormat, simulationExportUrl } from "../../services/apiClient";
import { buildDashboardData, DashboardData, MetricCard, ResultTab } from "./resultsModel";

type ResultsDashboardProps = {
  result: Record<string, unknown> | undefined;
  jobId?: string;
};

const TABS: { id: ResultTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "bankroll", label: "Bankroll" },
  { id: "outcomes", label: "Outcomes" },
  { id: "betting", label: "Betting" },
  { id: "risk", label: "Risk" },
  { id: "rules", label: "Rules" },
  { id: "trace", label: "Trace" },
  { id: "raw", label: "Raw" }
];

export function ResultsDashboard({ result, jobId }: ResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState<ResultTab>("overview");
  const dashboard = useMemo(() => buildDashboardData(result), [result]);

  if (!dashboard) {
    return (
      <section className="panel empty-dashboard">
        <CircleAlert size={20} aria-hidden="true" />
        <h2>No report data</h2>
        <p className="muted">The simulation completed without a readable report payload.</p>
      </section>
    );
  }

  return (
    <div className="results-dashboard">
      <section className="results-hero">
        <div>
          <p className="eyebrow">Completed simulation</p>
          <h2>Results Dashboard</h2>
          {jobId && <p className="muted">Job {jobId}</p>}
        </div>
        <div className="hero-stat">
          <span>Stop reason</span>
          <strong>{dashboard.stopReason ?? "completed"}</strong>
        </div>
        {jobId && <ReportExportActions jobId={jobId} />}
      </section>

      <MetricGrid metrics={dashboard.cards} />

      <div className="tab-list" role="tablist" aria-label="Result sections">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            className={activeTab === tab.id ? "active" : undefined}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <section className="panel tab-panel" role="tabpanel">
        <TabContent dashboard={dashboard} activeTab={activeTab} />
      </section>
    </div>
  );
}

function ReportExportActions({ jobId }: { jobId: string }) {
  const formats: { label: string; format: ReportExportFormat }[] = [
    { label: "JSON", format: "json" },
    { label: "CSV", format: "csv" },
    { label: "ZIP", format: "zip" },
    { label: "PDF", format: "pdf" },
    { label: "SVG", format: "chart.svg" }
  ];
  return (
    <div className="export-actions" aria-label="Simulation export actions">
      {formats.map((entry) => (
        <a className="result-link" href={simulationExportUrl(jobId, entry.format)} key={entry.format}>
          <Download size={16} aria-hidden="true" />
          {entry.label}
        </a>
      ))}
    </div>
  );
}

function TabContent({ dashboard, activeTab }: { dashboard: DashboardData; activeTab: ResultTab }) {
  switch (activeTab) {
    case "overview":
      return (
        <>
          <PanelTitle icon={<Activity size={18} aria-hidden="true" />} title="Overview" />
          <MetricGrid metrics={dashboard.cards} compact />
          <BankrollChart points={dashboard.chartPoints} />
        </>
      );
    case "bankroll":
      return (
        <>
          <PanelTitle icon={<Wallet size={18} aria-hidden="true" />} title="Bankroll" />
          <MetricGrid metrics={dashboard.bankroll} compact />
          <BankrollChart points={dashboard.chartPoints} />
        </>
      );
    case "outcomes":
      return (
        <>
          <PanelTitle icon={<Table2 size={18} aria-hidden="true" />} title="Outcomes" />
          <MetricTable metrics={dashboard.outcomes} />
        </>
      );
    case "betting":
      return (
        <>
          <PanelTitle icon={<BarChart3 size={18} aria-hidden="true" />} title="Betting" />
          <MetricTable metrics={dashboard.betting} />
        </>
      );
    case "risk":
      return (
        <>
          <PanelTitle icon={<Shield size={18} aria-hidden="true" />} title="Risk" />
          <MetricTable metrics={dashboard.risk} />
        </>
      );
    case "rules":
      return (
        <>
          <PanelTitle icon={<ScrollText size={18} aria-hidden="true" />} title="Rules and Metadata" />
          <MetricTable metrics={dashboard.rules} />
        </>
      );
    case "trace":
      return (
        <>
          <PanelTitle icon={<Database size={18} aria-hidden="true" />} title="Trace" />
          {dashboard.traceEvents.length === 0 ? (
            <p className="muted">No trace events are available for this report.</p>
          ) : (
            <TraceTable events={dashboard.traceEvents} />
          )}
        </>
      );
    case "raw":
      return (
        <>
          <PanelTitle icon={<FileJson size={18} aria-hidden="true" />} title="Raw Data" />
          <pre className="result-json">{JSON.stringify(dashboard.raw, null, 2)}</pre>
        </>
      );
  }
}

function MetricGrid({ metrics, compact = false }: { metrics: MetricCard[]; compact?: boolean }) {
  return (
    <dl className={compact ? "metric-card-grid compact-cards" : "metric-card-grid"}>
      {metrics.map((metric) => (
        <div key={metric.label} className="metric-card">
          <dt>{metric.label}</dt>
          <dd>{metric.value}</dd>
          {metric.detail && <span>{metric.detail}</span>}
        </div>
      ))}
    </dl>
  );
}

function MetricTable({ metrics }: { metrics: MetricCard[] }) {
  return (
    <table className="data-table">
      <tbody>
        {metrics.map((metric) => (
          <tr key={metric.label}>
            <th scope="row">{metric.label}</th>
            <td>{metric.value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function BankrollChart({ points }: { points: { label: string; value: number }[] }) {
  if (points.length === 0) {
    return <p className="muted">No bankroll chart data is available.</p>;
  }

  const min = Math.min(...points.map((point) => point.value));
  const max = Math.max(...points.map((point) => point.value));
  const range = max - min || 1;

  return (
    <div className="chart-panel" aria-label="Downsampled bankroll chart">
      {points.map((point, index) => (
        <span
          key={`${point.label}-${index}`}
          title={`Round ${point.label}: ${point.value}`}
          style={{ height: `${18 + ((point.value - min) / range) * 82}%` }}
        />
      ))}
    </div>
  );
}

function TraceTable({ events }: { events: Record<string, unknown>[] }) {
  return (
    <table className="data-table trace-table">
      <thead>
        <tr>
          <th scope="col">#</th>
          <th scope="col">Type</th>
          <th scope="col">Round</th>
          <th scope="col">Payload</th>
        </tr>
      </thead>
      <tbody>
        {events.slice(0, 50).map((event, index) => (
          <tr key={`${String(event.event_type ?? event.type ?? "event")}-${index}`}>
            <td>{index + 1}</td>
            <td>{String(event.event_type ?? event.type ?? "event")}</td>
            <td>{String(event.round_index ?? event.round ?? "n/a")}</td>
            <td>{JSON.stringify(event)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function PanelTitle({ icon, title }: { icon: JSX.Element; title: string }) {
  return (
    <div className="panel-heading">
      <h2>{title}</h2>
      {icon}
    </div>
  );
}

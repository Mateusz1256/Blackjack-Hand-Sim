export interface HealthResponse {
  status: string;
  app_name: string;
  api_version: string;
  engine_version: string;
}

export interface ValidationResponse {
  valid: boolean;
  rounds: number;
  seed: number;
  workers: number;
}

export type JobStatus = "queued" | "running" | "completed" | "failed" | "cancelled";

export interface JobProgress {
  current: number;
  total: number;
  message: string;
}

export interface SimulationJobResponse {
  job_id: string;
  status: JobStatus;
  progress: JobProgress;
  error: string | null;
}

export interface SimulationResultResponse {
  job_id: string;
  status: JobStatus;
  result: Record<string, unknown>;
}

export type ComparisonMode = "independent_seeds" | "common_random_numbers";

export interface ComparisonStartRequest {
  configs: string[];
  names?: string[];
  mode: ComparisonMode;
  rounds?: number;
  seed?: number;
  workers?: number;
}

export type ComparisonJobResponse = SimulationJobResponse;

export interface ComparisonResultResponse {
  job_id: string;
  status: JobStatus;
  result: Record<string, unknown>;
}

export interface BatchStartRequest {
  config_text: string;
  sessions: number;
  rounds_per_session: number;
  base_seed?: number;
  configuration_id?: string;
}

export type BatchJobResponse = SimulationJobResponse;

export interface BatchResultResponse {
  job_id: string;
  status: JobStatus;
  result: Record<string, unknown>;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function readError(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ?? fallback;
  } catch {
    return fallback;
  }
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

export async function validateSimulationConfig(
  configText: string
): Promise<ValidationResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations/validate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ config_text: configText })
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Validation request failed with status ${response.status}`));
  }
  return (await response.json()) as ValidationResponse;
}

export async function startSimulation(configText: string): Promise<SimulationJobResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ config_text: configText })
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Simulation start failed with status ${response.status}`));
  }
  return (await response.json()) as SimulationJobResponse;
}

export async function getSimulationJob(jobId: string): Promise<SimulationJobResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations/${jobId}`);
  if (!response.ok) {
    throw new Error(await readError(response, `Simulation status failed with status ${response.status}`));
  }
  return (await response.json()) as SimulationJobResponse;
}

export async function cancelSimulation(jobId: string): Promise<SimulationJobResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations/${jobId}/cancel`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Simulation cancel failed with status ${response.status}`));
  }
  return (await response.json()) as SimulationJobResponse;
}

export async function getSimulationResult(jobId: string): Promise<SimulationResultResponse> {
  const response = await fetch(`${API_BASE_URL}/simulations/${jobId}/result`);
  if (!response.ok) {
    throw new Error(await readError(response, `Simulation result failed with status ${response.status}`));
  }
  return (await response.json()) as SimulationResultResponse;
}


export async function startComparison(
  request: ComparisonStartRequest
): Promise<ComparisonJobResponse> {
  const response = await fetch(`${API_BASE_URL}/comparisons`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Comparison start failed with status ${response.status}`));
  }
  return (await response.json()) as ComparisonJobResponse;
}

export async function getComparisonJob(jobId: string): Promise<ComparisonJobResponse> {
  const response = await fetch(`${API_BASE_URL}/comparisons/${jobId}`);
  if (!response.ok) {
    throw new Error(await readError(response, `Comparison status failed with status ${response.status}`));
  }
  return (await response.json()) as ComparisonJobResponse;
}

export async function getComparisonResult(jobId: string): Promise<ComparisonResultResponse> {
  const response = await fetch(`${API_BASE_URL}/comparisons/${jobId}/result`);
  if (!response.ok) {
    throw new Error(await readError(response, `Comparison result failed with status ${response.status}`));
  }
  return (await response.json()) as ComparisonResultResponse;
}

export function comparisonExportUrl(jobId: string, exportFormat: "json" | "csv"): string {
  return `${API_BASE_URL}/comparisons/${jobId}/export/${exportFormat}`;
}

export async function startBatch(request: BatchStartRequest): Promise<BatchJobResponse> {
  const response = await fetch(`${API_BASE_URL}/batches`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Batch start failed with status ${response.status}`));
  }
  return (await response.json()) as BatchJobResponse;
}

export async function getBatchJob(jobId: string): Promise<BatchJobResponse> {
  const response = await fetch(`${API_BASE_URL}/batches/${jobId}`);
  if (!response.ok) {
    throw new Error(await readError(response, `Batch status failed with status ${response.status}`));
  }
  return (await response.json()) as BatchJobResponse;
}

export async function cancelBatch(jobId: string): Promise<BatchJobResponse> {
  const response = await fetch(`${API_BASE_URL}/batches/${jobId}/cancel`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(await readError(response, `Batch cancel failed with status ${response.status}`));
  }
  return (await response.json()) as BatchJobResponse;
}

export async function getBatchResult(jobId: string): Promise<BatchResultResponse> {
  const response = await fetch(`${API_BASE_URL}/batches/${jobId}/result`);
  if (!response.ok) {
    throw new Error(await readError(response, `Batch result failed with status ${response.status}`));
  }
  return (await response.json()) as BatchResultResponse;
}

export function batchExportUrl(jobId: string, exportFormat: "json" | "csv"): string {
  return `${API_BASE_URL}/batches/${jobId}/export/${exportFormat}`;
}

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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

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
    let detail = `Validation request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail ?? detail;
    } catch {
      // Keep the status-based fallback when the backend returns a non-JSON error.
    }
    throw new Error(detail);
  }
  return (await response.json()) as ValidationResponse;
}

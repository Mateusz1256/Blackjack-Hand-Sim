export interface HealthResponse {
  status: string;
  app_name: string;
  api_version: string;
  engine_version: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}

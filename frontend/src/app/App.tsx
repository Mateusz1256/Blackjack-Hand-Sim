import { Route, Routes } from "react-router-dom";

import { AppShell } from "../components/AppShell";
import { ConfigurationBuilderPage } from "../features/configuration/ConfigurationBuilderPage";
import { SimulationResultPage } from "../features/simulations/SimulationResultPage";
import { DashboardPage } from "../pages/DashboardPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { SettingsPage } from "../pages/SettingsPage";

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/configuration" element={<ConfigurationBuilderPage />} />
        <Route path="/simulations/:jobId" element={<SimulationResultPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  );
}

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../app/App";

const healthPayload = {
  status: "ok",
  app_name: "Blackjack Simulator API",
  api_version: "0.1.0",
  engine_version: "1.0.0"
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => healthPayload
      }))
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the application shell and health summary", async () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Simulation Console")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("1.0.0")).toBeInTheDocument());
  });

  it("routes to settings", async () => {
    render(
      <MemoryRouter initialEntries={["/settings"]}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText("Workspace Settings")).toBeInTheDocument();
  });

  it("toggles color theme", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );

    await user.click(screen.getByRole("button", { name: "Toggle color theme" }));

    expect(document.documentElement.dataset.theme).toBe("dark");
  });
});

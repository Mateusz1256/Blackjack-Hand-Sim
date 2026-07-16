import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SimulationRunPanel } from "./SimulationRunPanel";

const runningJob = {
  job_id: "job-1",
  status: "running",
  progress: {
    current: 2,
    total: 10,
    message: "running"
  },
  error: null
};

const completedJob = {
  job_id: "job-1",
  status: "completed",
  progress: {
    current: 10,
    total: 10,
    message: "completed"
  },
  error: null
};

describe("SimulationRunPanel", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("starts a simulation, polls progress, and links to the result", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => runningJob
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => completedJob
      });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <SimulationRunPanel configText="simulation: { rounds: 10 }" pollIntervalMs={1} />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole("button", { name: /start run/i }));

    await waitFor(() => expect(screen.getAllByText("completed").length).toBeGreaterThan(0));
    expect(screen.getByRole("link", { name: /open result/i })).toHaveAttribute(
      "href",
      "/simulations/job-1"
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/simulations", expect.objectContaining({ method: "POST" }));
    expect(fetchMock).toHaveBeenCalledWith("/api/v1/simulations/job-1");
  });

  it("cancels an active simulation", async () => {
    const cancelledJob = {
      ...runningJob,
      status: "cancelled",
      progress: {
        ...runningJob.progress,
        message: "cancelled"
      }
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => runningJob
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => cancelledJob
      });
    vi.stubGlobal("fetch", fetchMock);

    render(
      <MemoryRouter>
        <SimulationRunPanel configText="simulation: { rounds: 10 }" />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole("button", { name: /start run/i }));
    await waitFor(() => expect(screen.getByRole("button", { name: /cancel run/i })).toBeInTheDocument());
    expect(screen.getByText("20%")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /cancel run/i }));

    await waitFor(() => expect(screen.getAllByText("cancelled").length).toBeGreaterThan(0));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/v1/simulations/job-1/cancel",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("shows backend start errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 422,
        json: async () => ({ detail: "invalid configuration" })
      }))
    );

    render(
      <MemoryRouter>
        <SimulationRunPanel configText="bad config" />
      </MemoryRouter>
    );

    fireEvent.click(screen.getByRole("button", { name: /start run/i }));

    await waitFor(() => expect(screen.getByText("invalid configuration")).toBeInTheDocument());
  });
});

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ConfigurationBuilderPage } from "./ConfigurationBuilderPage";

describe("ConfigurationBuilderPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          valid: true,
          rounds: 10000,
          seed: 123,
          workers: 1
        })
      }))
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows dynamic betting fields and preview sequence", async () => {
    const user = userEvent.setup();
    render(<ConfigurationBuilderPage />);

    await user.selectOptions(screen.getByLabelText("Betting strategy"), "martingale");

    const preview = screen.getByLabelText("Betting preview sequence");
    expect(preview).toHaveTextContent("10");
    expect(preview).toHaveTextContent("160");
    expect(screen.queryByLabelText("Spread")).not.toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Betting strategy"), "true_count_spread");

    expect(screen.getByLabelText("Spread")).toBeInTheDocument();
    expect(screen.getByText("True-count spread betting requires counting to be enabled.")).toBeInTheDocument();
  });

  it("blocks backend validation while local validation has errors", async () => {
    const user = userEvent.setup();
    render(<ConfigurationBuilderPage />);

    await user.clear(screen.getByLabelText("Rounds"));
    await user.type(screen.getByLabelText("Rounds"), "0");
    await user.click(screen.getByRole("button", { name: "Validate config" }));

    expect(screen.getByText("Rounds must be positive.")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("validates generated YAML with the backend", async () => {
    const user = userEvent.setup();
    render(<ConfigurationBuilderPage />);

    await user.click(screen.getByRole("button", { name: "Validate config" }));

    await waitFor(() => expect(screen.getByText("valid")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/simulations/validate",
      expect.objectContaining({
        method: "POST",
        body: expect.stringContaining("config_text")
      })
    );
    const request = vi.mocked(fetch).mock.calls[0][1] as RequestInit;
    expect(String(request.body)).toContain("simulation:");
    expect(String(request.body)).toContain("blackjack_payout: 1.5");
  });

  it("previews, applies, and exports imported configuration", async () => {
    const user = userEvent.setup();
    render(<ConfigurationBuilderPage />);

    fireEvent.change(screen.getByLabelText("Pasted config"), {
      target: {
        value: `schema_version: 1
simulation:
  rounds: 42
`
      }
    });
    await user.click(screen.getByRole("button", { name: "Preview" }));

    expect(screen.getByText("Import preview is valid. 1 changes detected.")).toBeInTheDocument();
    expect(screen.getByLabelText("Import diff")).toHaveTextContent("simulation.rounds");

    await user.click(screen.getByRole("button", { name: "Apply import" }));

    expect(screen.getByLabelText("Rounds")).toHaveValue(42);

    await user.selectOptions(screen.getByLabelText("Format"), "json");
    await user.selectOptions(screen.getByLabelText("Scope"), "changed");

    expect(screen.getByText(/"rounds": 42/)).toBeInTheDocument();
  });
});

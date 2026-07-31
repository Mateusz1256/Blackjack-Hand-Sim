import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { PresetsPage } from "./PresetsPage";

const builtinPreset = {
  id: "standard-6d-s17",
  name: "Standard 6D S17",
  metadata: {
    id: "standard-6d-s17",
    name: "Standard 6D S17",
    category: "standard",
    source: "builtin"
  },
  config_text: "metadata:\n  id: standard-6d-s17\nconfiguration:\n  simulation:\n    rounds: 100\n",
  read_only: true,
  created_at: "2026-07-14T10:00:00Z",
  updated_at: "2026-07-14T10:00:00Z"
};

const customPreset = {
  ...builtinPreset,
  id: "custom-copy",
  name: "Custom Copy",
  read_only: false
};

describe("PresetsPage", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/presets/standard-6d-s17/duplicate")) {
          return { ok: true, json: async () => customPreset };
        }
        if (url.endsWith("/presets/custom-copy")) {
          return { ok: true, json: async () => ({}) };
        }
        if (url.includes("/presets")) {
          return { ok: true, json: async () => ({ presets: [builtinPreset, customPreset] }) };
        }
        return { ok: true, json: async () => ({}) };
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads presets and duplicates a built-in preset", async () => {
    const user = userEvent.setup();
    render(<PresetsPage />);

    await screen.findByText("read-only");
    expect(screen.getAllByText("Standard 6D S17").length).toBeGreaterThan(0);
    expect(screen.getByText("read-only")).toBeInTheDocument();

    await user.type(screen.getByLabelText("New preset name"), "Custom Copy");
    await user.click(screen.getByRole("button", { name: "Duplicate preset" }));

    await waitFor(() => expect(screen.getByText("Duplicated Custom Copy.")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/presets/standard-6d-s17/duplicate",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("requires confirmation before deleting a custom preset", async () => {
    const user = userEvent.setup();
    render(<PresetsPage />);

    await screen.findByText("Custom Copy");
    await user.click(screen.getByRole("button", { name: /Custom Copy/ }));
    await user.click(screen.getByRole("button", { name: "Delete" }));

    expect(screen.getByRole("dialog", { name: "Delete preset confirmation" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirm delete" }));

    await waitFor(() => expect(screen.getByText("Deleted Custom Copy.")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith("/api/v1/presets/custom-copy", { method: "DELETE" });
  });
});

import { afterEach, describe, expect, it, vi } from "vitest";

import { getHealth } from "../services/apiClient";

describe("apiClient", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches backend health", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          status: "ok",
          app_name: "Blackjack Simulator API",
          api_version: "0.1.0",
          engine_version: "1.0.0"
        })
      }))
    );

    await expect(getHealth()).resolves.toMatchObject({
      status: "ok",
      engine_version: "1.0.0"
    });
  });
});

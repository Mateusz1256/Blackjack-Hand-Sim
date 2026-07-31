import { expect, test } from "@playwright/test";

import { expectBasicAccessibility, importedConfig, mockApi } from "./fixtures";

test.beforeEach(async ({ page }) => {
  await mockApi(page);
});

test("creates a config, runs a simulation, opens results, and exports JSON", async ({
  page
}) => {
  await page.goto("/configuration");

  await page.getByRole("spinbutton", { name: "Rounds", exact: true }).fill("7");
  await page.getByRole("spinbutton", { name: "Seed", exact: true }).fill("321");
  await page.getByRole("button", { name: "Validate config" }).click();
  await expect(page.locator("dd").filter({ hasText: /^valid$/ })).toBeVisible();

  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page.getByLabel("Simulation status")).toContainText("completed");
  await page.getByRole("link", { name: "Open result" }).click();

  await expect(page.getByRole("heading", { name: "Results Dashboard" })).toBeVisible();
  await expect(page.getByLabel("Downsampled bankroll chart")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "JSON" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("simulation-sim-e2e.json");

  await expectBasicAccessibility(page);
});

test("imports a config and compares two deterministic short configs", async ({ page }) => {
  await page.goto("/configuration");

  await page.getByRole("textbox", { name: "Pasted config" }).fill(importedConfig);
  await page.getByRole("button", { name: "Preview" }).click();
  await expect(page.getByText(/Import preview is valid/)).toBeVisible();
  await page.getByRole("button", { name: "Apply import" }).click();
  await expect(page.getByRole("spinbutton", { name: "Rounds", exact: true })).toHaveValue("7");

  await page.getByRole("link", { name: "Comparisons" }).click();
  await page.getByRole("spinbutton", { name: "Rounds", exact: true }).fill("7");
  await page.getByRole("spinbutton", { name: "Seed", exact: true }).fill("321");
  await page.getByRole("button", { name: "Run comparison" }).click();

  await expect(page.getByRole("heading", { name: "Baseline Deltas" })).toBeVisible();
  await expect(page.getByRole("link", { name: "JSON" })).toHaveAttribute(
    "href",
    "/api/v1/comparisons/comparison-e2e/export/json"
  );
  await expect(page.getByLabel("Net result delta chart")).toBeVisible();

  await expectBasicAccessibility(page);
});

test("runs a short deterministic batch and shows loading and empty/error states", async ({
  page
}) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Backend Health" })).toBeVisible();

  await page.getByRole("link", { name: "Batches" }).click();
  await page.getByRole("spinbutton", { name: "Sessions", exact: true }).fill("0");
  await expect(page.getByText("Sessions must be positive.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Run batch" })).toBeDisabled();

  await page.getByRole("spinbutton", { name: "Sessions", exact: true }).fill("2");
  await page.getByRole("spinbutton", { name: "Rounds per session" }).fill("3");
  await page.getByRole("spinbutton", { name: "Base seed" }).fill("44");
  await page.getByRole("button", { name: "Run batch" }).click();

  await expect(page.getByRole("heading", { name: "Distribution Metrics" })).toBeVisible();
  await expect(page.getByLabel("Final bankroll histogram")).toBeVisible();
  await expect(page.getByRole("link", { name: "ZIP" })).toHaveAttribute(
    "href",
    "/api/v1/batches/batch-e2e/export/zip"
  );

  await expectBasicAccessibility(page);
});

import fs from "node:fs";
import path from "node:path";
import { test, expect } from "./fixtures";
import {
  capture,
  login,
  seedPlatformData,
  TEST_RESULTS_DIR,
  uniqueSuffix,
} from "./helpers";

test("administrator dashboard shows live metrics, growth and activity", async ({
  page,
}) => {
  await login(page);
  await seedPlatformData(page);
  await page.reload();

  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Active Users", { exact: true })).toBeVisible();
  await expect(page.getByText("Active Models", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Compliance Score", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("System Health", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Compliance Score", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("100%", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("Platform Growth (last 24 hours)")).toBeVisible();
  await expect(page.getByText("Recent Activity")).toBeVisible();

  await capture(page, "dashboard-desktop.png");
});

test("administrator can create, edit, deactivate and delete a user", async ({
  page,
}) => {
  await login(page);
  await page.goto("/users");
  await expect(
    page.getByRole("heading", { name: "User Management" }),
  ).toBeVisible();
  await expect(page.getByText("admin@example.com")).toBeVisible();

  const suffix = uniqueSuffix();
  const username = `e2e${suffix}`.slice(0, 16);
  const email = `managed-${suffix}@example.com`;
  const password = "ManagedUser123!";

  await page.getByRole("button", { name: "Add User" }).click();
  const createDialog = page.getByRole("dialog");
  await expect(
    createDialog.getByRole("heading", { name: "Add New User" }),
  ).toBeVisible();
  await createDialog.getByLabel("Username").fill(username);
  await createDialog.getByLabel("Email").fill(email);
  await createDialog.getByLabel("Full Name").fill("Managed Test User");
  await createDialog.locator('input[type="password"]').fill(password);
  await createDialog.getByRole("button", { name: "Add User" }).click();

  await expect(createDialog).toBeHidden();
  const row = page.getByRole("row", { name: new RegExp(username) });
  await expect(row).toBeVisible();
  await expect(row.getByText(email)).toBeVisible();
  await capture(page, "users-admin.png");

  await page.getByRole("button", { name: `Edit ${username}` }).click();
  const editDialog = page.getByRole("dialog");
  await editDialog.getByLabel("Full Name").fill("Renamed E2E User");
  await editDialog.getByRole("button", { name: "Save Changes" }).click();
  await expect(editDialog).toBeHidden();
  await expect(page.getByText("Renamed E2E User")).toBeVisible();

  await page.getByRole("button", { name: `Deactivate ${username}` }).click();
  await expect(row.getByText("Inactive")).toBeVisible();

  await page.getByRole("button", { name: `Delete ${username}` }).click();
  const deleteDialog = page.getByRole("dialog");
  await expect(
    deleteDialog.getByRole("heading", { name: "Delete user?" }),
  ).toBeVisible();
  await deleteDialog.getByRole("button", { name: "Delete" }).click();
  await expect(
    page.getByRole("row", { name: new RegExp(username) }),
  ).toHaveCount(0);
});

test("administrator can run compliance checks and export a report", async ({
  page,
}) => {
  await login(page);
  await page.goto("/compliance");
  await expect(
    page.getByRole("heading", { name: "Compliance Dashboard" }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Run Checks", exact: true }).click();
  await expect(page.getByText(/Compliance checks complete/)).toBeVisible();

  await expect(page.getByText("Overall Compliance Score")).toBeVisible();
  await expect(page.getByText("100%", { exact: true }).first()).toBeVisible();
  await expect(
    page.getByText("General Data Protection Regulation", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Health Insurance Portability and Accountability Act", {
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.getByText("California Consumer Privacy Act", { exact: true }),
  ).toBeVisible();
  await expect(page.getByText("Recent Compliance Activity")).toBeVisible();

  await capture(page, "compliance-checks.png");

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export Report" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(
    /^compliance-report-\d{4}-\d{2}-\d{2}\.json$/,
  );
  const exportPath = path.join(TEST_RESULTS_DIR, "compliance-report.json");
  await download.saveAs(exportPath);

  const exported = JSON.parse(fs.readFileSync(exportPath, "utf-8")) as {
    records: unknown[];
    summary: { score: number };
  };
  expect(exported.records.length).toBeGreaterThanOrEqual(3);
  expect(exported.summary.score).toBe(100);
});

test("monitoring page displays live host and model metrics", async ({
  page,
}) => {
  await login(page);
  await seedPlatformData(page);
  await page.goto("/monitoring");

  await expect(
    page.getByRole("heading", { name: "System Monitoring" }),
  ).toBeVisible();
  await expect(page.getByText("Resource Utilization")).toBeVisible();
  await expect(page.getByText("CPU Usage", { exact: true })).toBeVisible();
  await expect(page.getByText("Model Performance")).toBeVisible();
  await expect(page.getByText(/e2e-risk-model v1\.0\.0/).first()).toBeVisible();
  await expect(page.getByText("Accuracy")).toBeVisible();

  await capture(page, "monitoring-desktop.png");
});

test("security page displays observable control checks", async ({ page }) => {
  await login(page);
  await page.goto("/security");

  await expect(
    page.getByRole("heading", { name: "Security Overview" }),
  ).toBeVisible();
  await expect(page.getByText("Control Checks")).toBeVisible();
  await expect(page.getByText("secret key", { exact: true })).toBeVisible();
  await expect(page.getByText("Recommendations")).toBeVisible();
  await expect(page.getByText("Recent Security Events")).toBeVisible();

  await capture(page, "security-desktop.png");
});

test("administrator settings persist after a reload", async ({ page }) => {
  await login(page);
  await page.goto("/config");

  await expect(
    page.getByRole("heading", { name: "Configuration Management" }),
  ).toBeVisible();
  const retention = page.getByLabel("Data Retention (days)");
  await expect(retention).toHaveValue("30");

  await retention.fill("45");
  const debugMode = page.getByLabel("Debug Mode");
  if (!(await debugMode.isChecked())) {
    await debugMode.click();
  }
  await page.getByRole("button", { name: "Save Changes" }).click();
  await expect(
    page.getByText("Configuration saved successfully."),
  ).toBeVisible();

  await page.reload();
  await expect(page.getByLabel("Data Retention (days)")).toHaveValue("45");
  await expect(page.getByLabel("Debug Mode")).toBeChecked();
  await capture(page, "configuration-settings.png");
});

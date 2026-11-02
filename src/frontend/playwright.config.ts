import { defineConfig, devices } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const frontendRoot = process.cwd();
const projectRoot = path.resolve(frontendRoot, "../..");
const evidenceRoot = path.join(projectRoot, "docs", "evidence");
const screenshots = path.join(evidenceRoot, "screenshots");
const testResults = path.join(evidenceRoot, "test-results");

fs.mkdirSync(screenshots, { recursive: true });
fs.mkdirSync(testResults, { recursive: true });

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [
    ["list"],
    [
      "html",
      {
        outputFolder: path.join(testResults, "playwright-report"),
        open: "never",
      },
    ],
    ["json", { outputFile: path.join(testResults, "playwright-results.json") }],
  ],
  outputDir: path.join(testResults, "playwright-artifacts"),
  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
    viewport: { width: 1440, height: 900 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        channel: "chrome",
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
  webServer: [
    {
      command: "bash ../../scripts/start-e2e-backend.sh",
      url: "http://127.0.0.1:5001/ready",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5173",
      url: "http://127.0.0.1:5173",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        VITE_API_PROXY_TARGET: "http://127.0.0.1:5001",
        VITE_API_URL: "",
      },
    },
  ],
});

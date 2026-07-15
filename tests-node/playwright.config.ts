import { defineConfig, devices } from "@playwright/test";
import { defineBddConfig } from "playwright-bdd";

// Compile les .feature Gherkin en specs Playwright natives (steps/, features/)
const bddTestDir = defineBddConfig({
  features: "features/**/*.feature",
  steps: "steps/**/*.ts",
});

const BASE_URL = process.env.BASE_URL ?? "http://localhost:3000";
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: ".",
  // tests/** (unit, integration, e2e, api, smoke) + specs générées BDD
  testMatch: ["tests/**/*.spec.ts", `${bddTestDir}/**/*.spec.js`],

  fullyParallel: true,
  forbidOnly: isCI,
  // Retries uniquement en CI, jamais sur @smoke (gate) - géré aussi côté workflow via --grep
  retries: isCI ? 2 : 0,
  workers: isCI ? undefined : undefined,

  reporter: isCI
    ? [
        ["blob"], // fusion multi-shards
        ["junit", { outputFile: "test-results/junit.xml" }],
        ["github"],
      ]
    : [["list"], ["html", { open: "never" }], ["mochawesome", { reportDir: "mochawesome-report" }]],

  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },

  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],

  // Décommenter si l'app cible (RWA) doit être démarrée par Playwright lui-même
  // webServer: {
  //   command: "cd ../infra && docker compose up",
  //   url: BASE_URL,
  //   reuseExistingServer: !isCI,
  // },
});

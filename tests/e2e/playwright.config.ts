import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 3 : 0,
  workers: 1,
  reporter: [
    ["junit", { outputFile: "test-results/results.xml" }],
    ["html"],
    ["list"],
  ],
  timeout: 600_000,
  expect: { timeout: 10_000 },
  use: {
    actionTimeout: process.env.CI ? 20_000 : 10_000,
    navigationTimeout: process.env.CI ? 60_000 : 30_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: {
      slowMo: process.env.CI ? 2000 : 200,
    },
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});

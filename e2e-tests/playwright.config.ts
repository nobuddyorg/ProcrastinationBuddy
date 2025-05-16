import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
    testDir: "./tests",
    fullyParallel: false,
    forbidOnly: !!process.env.CI,
    retries: 1,
    workers: 1,
    reporter: [["junit", { outputFile: "test-results/results.xml" }], ["html"]],
    timeout: 600_000,
    expect: { timeout: 10_000 }, 
    use: {
        trace: "retain-on-failure",
        screenshot: "only-on-failure",
    },

    projects: [
        {
            name: "chromium",
            use: { ...devices["Desktop Chrome"] },
        },
    ],
});
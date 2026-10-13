import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";
import { join } from "node:path";

const venvPython = join(
  process.cwd(),
  ".venv",
  process.platform === "win32" ? "Scripts" : "bin",
  process.platform === "win32" ? "python.exe" : "python",
);
const python = process.env.PYTHON ?? (existsSync(venvPython) ? venvPython : "python");

export default defineConfig({
  testDir: "./web/e2e",
  use: {
    baseURL: "http://127.0.0.1:5000",
    browserName: "chromium",
    headless: true,
    video: "retain-on-failure",
  },
  webServer: {
    command: `"${python}" -m web.app`,
    url: "http://127.0.0.1:5000/health",
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});

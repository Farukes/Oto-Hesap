import { defineConfig, devices } from "@playwright/test";

// OtoHesap E2E — gerçek API + gerçek Postgres'e karşı çalışır (mock yok).
// Yerelde sistemdeki Google Chrome kullanılır (tarayıcı indirmesi yok);
// CI'da `npx playwright install --with-deps chromium` ile gelen paketli Chromium.

export const WEB_URL = (process.env.E2E_WEB_URL ?? "http://localhost:3000").replace(/\/+$/, "");
export const API_URL = (process.env.E2E_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

// CI'da paketli Chromium; yerelde sistem Chrome'u ("chrome" kanalı).
// Gerekirse PW_CHANNEL ile ezilir (örn. PW_CHANNEL=chrome-beta), PW_CHANNEL="" → paketli Chromium.
const channel = process.env.PW_CHANNEL ?? (process.env.CI ? "" : "chrome");

export default defineConfig({
  testDir: "./e2e",
  // Tek veritabanı paylaşıldığı için testler sırayla koşar (kayıt ekleme/silme çakışmasın).
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  // Not: makine yükü altındayken API yanıtları yavaşlayabiliyor; süreler cömert tutuldu.
  timeout: 120_000,
  expect: { timeout: 25_000 },
  reporter: process.env.CI
    ? [["list"], ["html", { open: "never" }]]
    : [["list"]],
  use: {
    baseURL: WEB_URL,
    locale: "tr-TR",
    timezoneId: "Europe/Istanbul",
    actionTimeout: 30_000,
    navigationTimeout: 90_000,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"], channel: channel || undefined },
    },
  ],
  webServer: {
    command: "bun run dev",
    url: WEB_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    stdout: "pipe",
    stderr: "pipe",
    env: { NEXT_PUBLIC_API_URL: API_URL },
  },
});

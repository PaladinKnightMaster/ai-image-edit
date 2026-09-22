import { expect, test, type Page } from "@playwright/test";

import { installChatApiMocks, MOCK_HARDWARE, type EditScenario } from "./fixtures/mock-api";

async function openChat(page: Page, scenario: EditScenario = "success") {
  await installChatApiMocks(page, scenario);
  await page.goto("/chat");
}

async function stageLibraryBase(page: Page) {
  await page.getByTestId("input-slot-base").getByRole("button", { name: "Pick from library" }).click();
  await expect(page.getByTestId("history-picker-modal")).toBeVisible();
  await page.getByTestId("history-output-use-run-hist-1").click();
}

async function runNaturalRetouch(page: Page) {
  await page.getByRole("button", { name: /Edit preset Natural Skin Retouch/i }).click();
  await page.getByRole("button", { name: "Run edit" }).click();
}

test.describe("chat edit flow (mocked backend)", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear();
    });
  });

  test("loads edit mode with hardware recommendation", async ({ page }) => {
    await openChat(page);

    await expect(page.getByRole("heading", { name: "Edit Photo" }).first()).toBeVisible();
    await page.getByRole("button", { name: "Setup" }).click();
    await expect(page.getByTestId("hardware-advisor-panel")).toBeVisible();
    await expect(page.getByText(/Best local pick for this machine/i)).toBeVisible();
    await expect(page.getByTestId("hardware-ready")).toBeVisible();
    await expect(page.getByTestId("hardware-ready").getByText("Ready", { exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Run edit" })).toBeVisible();
  });

  test("offers one download when the recommended model is missing", async ({ page }) => {
    await installChatApiMocks(page);
    await page.route("http://127.0.0.1:8000/api/hardware", async (route) => {
      const missing = structuredClone(MOCK_HARDWARE);
      const best = missing.models.find((model) => model.id === "sdxl-openvino");
      if (best) {
        best.present = false;
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(missing)
      });
    });
    let confirmed = false;
    await page.route("http://127.0.0.1:8000/api/settings/model-location", async (route) => {
      let postedPath = "";
      if (route.request().method() === "POST") {
        confirmed = true;
        const body = route.request().postDataJSON() as { path?: string } | null;
        postedPath = body?.path || "";
      }
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          model_id: "sdxl-openvino",
          path: postedPath || "D:/models/openvino/sdxl_base",
          default_path: "D:/models/openvino/sdxl_base",
          confirmed,
          locked_by_env: false,
          source: confirmed ? "settings" : "default",
          exists: true
        })
      });
    });
    await page.goto("/chat");
    await page.getByRole("button", { name: "Setup" }).click();

    await expect(page.getByTestId("hardware-setup")).toBeVisible();
    await expect(page.getByTestId("model-folder-picker")).toBeVisible();
    await expect(page.getByTestId("confirm-model-folder")).toBeVisible();
    await expect(page.getByTestId("download-recommended-model")).toHaveCount(0);
    await page.getByTestId("confirm-model-folder").click();
    await expect(page.getByTestId("download-recommended-model")).toBeVisible();
    await expect(page.getByTestId("other-models")).toHaveCount(0);
    await page.getByTestId("other-models-toggle").click();
    await expect(page.getByTestId("other-models")).toBeVisible();
    await expect(page.getByTestId("other-models").getByRole("button", { name: /Download/i })).toHaveCount(0);
  });

  test("requires a base image before edit can run", async ({ page }) => {
    await openChat(page);

    await page.getByRole("button", { name: /Edit preset Natural Skin Retouch/i }).click();
    await expect(page.getByPlaceholder("Describe the portrait edit you want...")).not.toHaveValue("");

    await page.getByRole("button", { name: "Run edit" }).click();
    await expect(page.getByTestId("composer-error")).toHaveText(
      "Add a base image before running the edit."
    );
  });

  test("keeps reference guidance off for a one-image model and on for a two-image model", async ({
    page
  }) => {
    await openChat(page);

    const reference = page.getByTestId("input-slot-reference");
    await expect(reference.getByText("This model currently supports only one input image.")).toBeVisible();
    await expect(reference.getByRole("button", { name: "Pick from library" })).toBeDisabled();

    await page.getByRole("button", { name: "Open advanced controls" }).click();
    await page.getByRole("combobox").selectOption("qwen-image-edit-2511");

    await expect(
      reference.getByText("Optional. Guides lighting, style, framing, or angle without replacing the base identity.")
    ).toBeVisible();
    await reference.getByRole("button", { name: "Pick from library" }).click();
    await expect(page.getByTestId("history-picker-modal")).toBeVisible();
    await expect(page.getByRole("button", { name: "Use as visual guide" })).toBeVisible();
  });

  test("library base + run edit reaches compare, download, and reuse", async ({ page }) => {
    await openChat(page, "progress");
    await stageLibraryBase(page);
    await runNaturalRetouch(page);

    const jobCard = page.getByTestId("assistant-job-job-edit-1");
    await expect(jobCard).toBeVisible({ timeout: 20_000 });
    await expect(jobCard.getByText(/Step: \d+\/4/)).toBeVisible();
    await expect(page.getByTestId("assistant-job-status-job-edit-1")).toHaveText(/Status:\s*Complete/i);
    await expect(page.getByTestId("before-after-compare")).toBeVisible();
    await expect(jobCard.getByRole("link", { name: "Download" })).toHaveAttribute(
      "href",
      /\/api\/images\/img-out-1/
    );
    await expect(jobCard.getByRole("button", { name: "Edit this" })).toBeVisible();
  });

  test("pending review stays hidden until reveal", async ({ page }) => {
    await openChat(page, "review");
    await stageLibraryBase(page);
    await runNaturalRetouch(page);

    const jobCard = page.getByTestId("assistant-job-job-edit-1");
    await expect(jobCard.getByRole("button", { name: "Reveal result" })).toBeVisible({
      timeout: 20_000
    });
    await expect(jobCard.getByRole("link", { name: "Download" })).toHaveCount(0);

    await jobCard.getByRole("button", { name: "Reveal result" }).click();
    await expect(page.getByTestId("assistant-job-status-job-edit-1")).toHaveText(/Status:\s*Complete/i);
    await expect(jobCard.getByRole("link", { name: "Download" })).toBeVisible();
  });

  test("failed edit can be retried on the same job", async ({ page }) => {
    await openChat(page, "failed");
    await stageLibraryBase(page);
    await runNaturalRetouch(page);

    const jobCard = page.getByTestId("assistant-job-job-edit-1");
    await expect(page.getByTestId("assistant-job-status-job-edit-1")).toHaveText(/Status:\s*Failed/i, {
      timeout: 20_000
    });
    await jobCard.getByRole("button", { name: "Retry" }).click();
    await expect(page.getByTestId("assistant-job-status-job-edit-1")).toHaveText(/Status:\s*Complete/i, {
      timeout: 20_000
    });
  });

  test("stream disconnect reconciles instead of marking the job failed", async ({ page }) => {
    await openChat(page, "disconnect");
    await stageLibraryBase(page);
    await runNaturalRetouch(page);

    const status = page.getByTestId("assistant-job-status-job-edit-1");
    await expect(status).toBeVisible({ timeout: 20_000 });
    await expect(status).not.toHaveText(/Failed/i);
    await expect(status).toHaveText(/Status:\s*Complete/i, { timeout: 20_000 });
  });
});

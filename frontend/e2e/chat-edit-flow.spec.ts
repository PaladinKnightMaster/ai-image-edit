import { expect, test } from "@playwright/test";

import { installChatApiMocks } from "./fixtures/mock-api";

test.describe("chat edit flow (mocked backend)", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear();
    });
    await installChatApiMocks(page);
  });

  test("loads edit mode with hardware recommendation", async ({ page }) => {
    await page.goto("/chat");

    await expect(page.getByRole("heading", { name: "Edit Photo" }).first()).toBeVisible();
    await expect(page.getByTestId("hardware-advisor-panel")).toBeVisible();
    await expect(page.getByText(/Best local pick for this machine/i)).toBeVisible();
    await expect(
      page.getByTestId("hardware-advisor-panel").getByText("Best pick")
    ).toBeVisible();
    await expect(page.getByRole("button", { name: "Run edit" })).toBeVisible();
  });

  test("requires a base image before edit can run", async ({ page }) => {
    await page.goto("/chat");

    await page
      .getByRole("button", {
        name: /Edit preset Natural Skin Retouch/i
      })
      .click();
    await expect(page.getByPlaceholder("Describe the portrait edit you want...")).not.toHaveValue(
      ""
    );

    await page.getByRole("button", { name: "Run edit" }).click();
    await expect(page.getByTestId("composer-error")).toHaveText(
      "Add a base image before running the edit."
    );
  });

  test("library base + run edit reaches a terminal success state", async ({ page }) => {
    await page.goto("/chat");

    await page.getByRole("button", { name: "Pick from library" }).first().click();
    await expect(page.getByTestId("history-picker-modal")).toBeVisible();
    await page.getByTestId("history-output-use-run-hist-1").click();

    await page
      .getByRole("button", {
        name: /Edit preset Natural Skin Retouch/i
      })
      .click();
    await page.getByRole("button", { name: "Run edit" }).click();

    const jobCard = page.getByTestId("assistant-job-job-edit-1");
    await expect(jobCard).toBeVisible({ timeout: 20_000 });
    await expect(page.getByTestId("assistant-job-status-job-edit-1")).toHaveText(
      /Status:\s*Complete/i
    );
    await expect(page.getByTestId("before-after-compare")).toBeVisible();
  });
});

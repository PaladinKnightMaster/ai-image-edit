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
    await expect(page.getByText(/base image/i).first()).toBeVisible();
  });

  test("library base + run edit reaches a terminal success state", async ({ page }) => {
    await page.goto("/chat");

    await page.getByRole("button", { name: "Pick from library" }).first().click();
    await expect(page.getByTestId("history-picker-modal")).toBeVisible();
    await page.getByRole("button", { name: "Use as base image" }).click();

    await page
      .getByRole("button", {
        name: /Edit preset Natural Skin Retouch/i
      })
      .click();
    await page.getByRole("button", { name: "Run edit" }).click();

    await expect(page.getByText(/Complete|succeeded|Compare/i).first()).toBeVisible({
      timeout: 20_000
    });
  });
});

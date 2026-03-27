import { test, expect } from "@playwright/test";

test.describe("Dashboard", () => {
  test("should load the dashboard page", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Executions" })).toBeVisible();
    await expect(page.getByText("Automated development pipeline runs")).toBeVisible();
  });

  test("should show New Execution button", async ({ page }) => {
    await page.goto("/");

    const newExecutionButton = page.getByRole("button", { name: /New execution/i });
    await expect(newExecutionButton).toBeVisible();
  });

  test("should show search bar and filter dropdown", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByPlaceholder("Search executions...")).toBeVisible();
    await expect(page.locator("select").first()).toBeVisible();
  });

  test("should open new execution form when clicking New Execution button", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();

    await expect(page.getByRole("heading", { name: "New execution" })).toBeVisible();
    await expect(page.getByPlaceholder("e.g. Add JWT authentication with refresh tokens")).toBeVisible();
    await expect(page.getByPlaceholder("e.g. owner/repo")).toBeVisible();
  });

  test("should show Start workflow button in form", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();

    const startButton = page.getByRole("button", { name: /Start workflow/i });
    await expect(startButton).toBeVisible();
  });

  test("should disable Start workflow button when feature request is empty", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();

    const startButton = page.getByRole("button", { name: /Start workflow/i });
    await expect(startButton).toBeDisabled();
  });

  test("should enable Start workflow button when feature request is filled", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();

    await page.getByPlaceholder("e.g. Add JWT authentication with refresh tokens").fill("Build a calculator feature");

    const startButton = page.getByRole("button", { name: /Start workflow/i });
    await expect(startButton).toBeEnabled();
  });

  test("should close form when Cancel is clicked", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();
    await page.getByRole("button", { name: "Cancel" }).nth(1).click();

    await expect(page.getByRole("heading", { name: "New execution" })).not.toBeVisible();
  });

  test("should close form when X button is clicked", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: /New execution/i }).click();
    await page.getByRole("button", { name: "Cancel" }).first().click();

    await expect(page.getByRole("heading", { name: "New execution" })).not.toBeVisible();
  });

  test("should show executions list when executions exist", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator('[href^="/executions/"]').first()).toBeVisible();
  });

  test("should show skeleton loaders while loading", async ({ page }) => {
    await page.goto("/");

    await expect(page.locator(".skeleton").first()).toBeVisible();
  });
});

test.describe("New Execution Form", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: /New execution/i }).click();
  });

  test("should have workspace mode options", async ({ page }) => {
    const workspaceSelect = page.locator("select").nth(1);
    await expect(workspaceSelect).toBeVisible();

    await expect(workspaceSelect).toHaveValue("sandbox");
    await expect(workspaceSelect.locator("option")).toHaveCount(2);
  });

  test("should switch workspace mode to git", async ({ page }) => {
    const workspaceSelect = page.locator("select").nth(1);
    await workspaceSelect.selectOption("git");

    await expect(workspaceSelect).toHaveValue("git");
  });

  test("should fill GitHub repository field", async ({ page }) => {
    const repoInput = page.getByPlaceholder("e.g. owner/repo");
    await repoInput.fill("owner/repo");

    await expect(repoInput).toHaveValue("owner/repo");
  });
});

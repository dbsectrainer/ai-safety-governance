import { test, expect } from "./fixtures";
import { capture, expectNoHorizontalOverflow } from "./helpers";

test("landing page renders and remains usable on desktop and mobile", async ({
  page,
}) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", {
      name: "AI Safety Governance Platform",
      level: 1,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Key Features" }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Get Started" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Sign In" })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Compliance Management" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Real-time Monitoring" }),
  ).toBeVisible();

  await capture(page, "homepage-desktop.png");
  await expectNoHorizontalOverflow(page);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await expect(
    page.getByRole("heading", {
      name: "AI Safety Governance Platform",
      level: 1,
    }),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Get Started" })).toBeVisible();
  await capture(page, "homepage-mobile.png");
  await expectNoHorizontalOverflow(page);
});

test("login page is reachable from the landing page", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(
    page.getByRole("heading", { name: "Sign In", exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("Email Address")).toBeVisible();
  await expect(page.locator("#password")).toBeVisible();
  await capture(page, "login-desktop.png");
});

test("unauthenticated dashboard access redirects to login", async ({
  page,
}) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login$/);
});

import { test, expect } from "./fixtures";
import { capture, expectNoHorizontalOverflow, login } from "./helpers";

test("mobile navigation opens, routes, and stays within the viewport", async ({
  page,
}) => {
  await login(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await capture(page, "dashboard-mobile.png");

  await page.getByRole("button", { name: "Toggle navigation" }).click();
  await expect(
    page.getByRole("navigation", { name: "Main navigation" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Users", exact: true }).click();

  await expect(page).toHaveURL(/\/users$/);
  await expect(
    page.getByRole("heading", { name: "User Management" }),
  ).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await capture(page, "users-mobile.png");
});

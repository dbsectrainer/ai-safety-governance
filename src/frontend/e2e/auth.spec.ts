import { test, expect } from "./fixtures";
import {
  capture,
  expectNoHorizontalOverflow,
  login,
  logout,
  uniqueSuffix,
} from "./helpers";

test("a new user can register, sign in, and view the dashboard", async ({
  page,
}) => {
  const suffix = uniqueSuffix();
  const username = `e2e${suffix}`.slice(0, 16);
  const email = `e2e${suffix}@example.com`;
  const password = "E2eUser123!";

  await page.goto("/register");
  await expect(
    page.getByRole("heading", { name: "Create Account" }),
  ).toBeVisible();
  await capture(page, "register-desktop.png");

  await page.getByLabel("Email Address").fill(email);
  await page.getByLabel("Username").fill(username);
  await page.getByLabel(/Full Name/).fill("Registered Test User");
  await page.locator("#password").fill(password);
  await page.getByLabel("Confirm Password").fill(password);
  await page.getByRole("button", { name: "Create Account" }).click();

  await expect(page).toHaveURL(/\/login$/);
  await expect(
    page.getByText("Registration successful! Please sign in."),
  ).toBeVisible();

  await page.getByLabel("Email Address").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: "Sign In", exact: true }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByText("Active Users")).toBeVisible();
  await expect(page.getByText("Platform Growth (last 24 hours)")).toBeVisible();
  await capture(page, "dashboard-new-user.png");
  await expectNoHorizontalOverflow(page);
});

test("an administrator can sign out", async ({ page }) => {
  await login(page);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await logout(page);
  await expect(
    page.getByRole("heading", { name: "Sign In", exact: true }),
  ).toBeVisible();
  const token = await page.evaluate(() => localStorage.getItem("token"));
  expect(token).toBeNull();
});

test("a regular user is denied admin pages but can use the dashboard", async ({
  page,
}) => {
  const suffix = uniqueSuffix();
  const username = `usr${suffix}`.slice(0, 16);
  const email = `usr${suffix}@example.com`;
  const password = "RegularPass123!";

  const registration = await page.request.post("/api/v1/auth/register", {
    data: {
      username,
      email,
      password,
      full_name: "Regular Test User",
    },
  });
  expect(registration.status()).toBe(200);

  await login(page, email, password);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await capture(page, "dashboard-regular-user.png");

  await page.goto("/users");
  await expect(page).toHaveURL(/\/unauthorized$/);
  await expect(
    page.getByRole("heading", { name: "Access Denied" }),
  ).toBeVisible();
  await capture(page, "unauthorized.png");

  await page.goto("/dashboard");
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});

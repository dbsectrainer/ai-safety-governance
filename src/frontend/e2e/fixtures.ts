import { test as base, expect } from "@playwright/test";

/**
 * Shared test fixture that fails a test if the browser reports an uncaught
 * JavaScript error, a console error, or an API request returning >= 400.
 *
 * The fixtures are automatic so every test inherits the checks.
 */
export const test = base.extend<{
  consoleErrors: string[];
  apiFailures: string[];
}>({
  consoleErrors: [
    async ({ page }, use) => {
      const errors: string[] = [];
      page.on("console", (message) => {
        if (message.type() === "error") {
          errors.push(message.text());
        }
      });
      page.on("pageerror", (error) => {
        errors.push(`pageerror: ${error.message}`);
      });

      await use(errors);

      expect(errors, "Unexpected browser console/page errors").toEqual([]);
    },
    { auto: true },
  ],

  apiFailures: [
    async ({ page }, use) => {
      const failures: string[] = [];
      page.on("response", (response) => {
        const url = response.url();
        if (url.includes("/api/") && response.status() >= 400) {
          failures.push(`${response.status()} ${url}`);
        }
      });
      page.on("requestfailed", (request) => {
        const url = request.url();
        if (url.includes("/api/")) {
          failures.push(
            `${request.failure()?.errorText ?? "request failed"} ${url}`,
          );
        }
      });

      await use(failures);

      expect(failures, "Unexpected failed API requests").toEqual([]);
    },
    { auto: true },
  ],
});

export { expect };

import { test as base } from "@playwright/test";
import { LoginPage } from "@pages/LoginPage";

type AuthFixtures = {
  loginPage: LoginPage;
  authenticatedPage: LoginPage;
};

/**
 * Fixture d'authentification.
 * TEST_USER / TEST_PASSWORD viennent des secrets CI (jamais en dur).
 */
export const test = base.extend<AuthFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage);
  },

  authenticatedPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(
      process.env.TEST_USER ?? "test.user",
      process.env.TEST_PASSWORD ?? "s3cret",
    );
    await use(loginPage);
  },
});

export { expect } from "@playwright/test";

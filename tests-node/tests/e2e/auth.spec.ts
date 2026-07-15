import { test, expect } from "@fixtures/auth.fixture";

test.describe("Auth & onboarding @auth @regression", () => {
  test("login avec identifiants invalides affiche une erreur", async ({ page, loginPage }) => {
    await loginPage.goto();
    await loginPage.login("invalid.user", "wrong-password");
    await expect(loginPage.errorMessage).toBeVisible();
  });

  test("logout renvoie vers la page de login", async ({ authenticatedPage, page }) => {
    await page.getByTestId("sidenav-signout").click();
    await expect(page).toHaveURL(/signin/);
  });
});

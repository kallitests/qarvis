import { test, expect } from "@fixtures/auth.fixture";
import { NewTransactionPage } from "@pages/NewTransactionPage";

test.describe("Négatifs @negative @regression", () => {
  test("montant négatif est rejeté", async ({ authenticatedPage, page }) => {
    const newTx = new NewTransactionPage(page);
    await page.getByRole("button", { name: /new/i }).click();
    await newTx.amountInput.fill("-10");
    await newTx.payButton.click();
    await expect(page.getByText(/invalid amount/i)).toBeVisible();
  });
});

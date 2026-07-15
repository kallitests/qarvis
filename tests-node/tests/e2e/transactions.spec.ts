import { test, expect } from "@fixtures/auth.fixture";
import { NewTransactionPage } from "@pages/NewTransactionPage";
import { demoUsers } from "@fixtures/seed-data";
import { buildTransactionNote } from "@utils/builders";

test.describe("Transactions @regression", () => {
  test("envoyer de l'argent à un contact met à jour le feed", async ({ authenticatedPage, page }) => {
    const newTx = new NewTransactionPage(page);
    const note = buildTransactionNote();

    await page.getByRole("button", { name: /new/i }).click();
    await newTx.payContact(demoUsers.contact.username, "5.00", note);

    await expect(page.getByText(note)).toBeVisible();
  });
});

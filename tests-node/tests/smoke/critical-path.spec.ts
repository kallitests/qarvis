import { test, expect } from "@fixtures/auth.fixture";
import { FeedPage } from "@pages/FeedPage";
import { NewTransactionPage } from "@pages/NewTransactionPage";
import { demoUsers } from "@fixtures/seed-data";
import { buildTransactionNote } from "@utils/builders";

/**
 * Smoke - chemin critique (gate du pipeline, cible < 90s).
 * Login -> paiement -> transaction visible -> notification -> logout.
 */
test.describe("Smoke @smoke", () => {
  test("chemin critique paiement de bout en bout", async ({ authenticatedPage, page }) => {
    const feed = new FeedPage(page);
    const newTx = new NewTransactionPage(page);
    const note = buildTransactionNote();

    await page.getByRole("button", { name: /new/i }).click();
    await newTx.payContact(demoUsers.contact.username, "10.00", note);

    await feed.gotoTab("personal");
    const latest = await feed.latestTransaction();
    await expect(latest).toContainText(note);

    await page.getByTestId("nav-notifications").click();
    await expect(page.getByTestId("notification-list").locator("li").first()).toBeVisible();

    await page.getByTestId("sidenav-signout").click();
    await expect(page).toHaveURL(/signin/);
  });
});

import { type Page, type Locator } from "@playwright/test";

/** Page Object - Feed de transactions (public / contacts / perso) */
export class FeedPage {
  readonly page: Page;
  readonly transactionList: Locator;
  readonly newTransactionButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.transactionList = page.getByTestId("transaction-list");
    this.newTransactionButton = page.getByRole("button", { name: /new/i });
  }

  async gotoTab(tab: "public" | "contacts" | "personal") {
    await this.page.getByRole("tab", { name: new RegExp(tab, "i") }).click();
  }

  async latestTransaction(): Promise<Locator> {
    return this.transactionList.locator("li").first();
  }
}

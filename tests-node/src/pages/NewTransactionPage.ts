import { type Page, type Locator } from "@playwright/test";

/** Page Object - Envoi/Demande d'argent */
export class NewTransactionPage {
  readonly page: Page;
  readonly userSearchInput: Locator;
  readonly amountInput: Locator;
  readonly noteInput: Locator;
  readonly payButton: Locator;
  readonly requestButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.userSearchInput = page.getByPlaceholder(/search/i);
    this.amountInput = page.getByLabel("Amount");
    this.noteInput = page.getByLabel("Add a note");
    this.payButton = page.getByRole("button", { name: "Pay" });
    this.requestButton = page.getByRole("button", { name: "Request" });
  }

  async payContact(contactName: string, amount: string, note: string) {
    await this.userSearchInput.fill(contactName);
    await this.page.getByText(contactName, { exact: false }).first().click();
    await this.amountInput.fill(amount);
    await this.noteInput.fill(note);
    await this.payButton.click();
  }
}

import { createBdd } from "playwright-bdd";
import { test } from "@fixtures/auth.fixture";
import { expect } from "@playwright/test";
import { NewTransactionPage } from "@pages/NewTransactionPage";
import { FeedPage } from "@pages/FeedPage";
import { demoUsers } from "@fixtures/seed-data";
import { buildTransactionNote } from "@utils/builders";

const { Given, When, Then } = createBdd(test);

let note: string;

Given("je suis connecté avec un utilisateur de démo", async ({ authenticatedPage }) => {
  // authenticatedPage fixture gère déjà le login
});

When("j'envoie 10.00 à un contact avec une note", async ({ page }) => {
  const newTx = new NewTransactionPage(page);
  note = buildTransactionNote();
  await page.getByRole("button", { name: /new/i }).click();
  await newTx.payContact(demoUsers.contact.username, "10.00", note);
});

Then("la transaction apparaît dans mon feed personnel", async ({ page }) => {
  const feed = new FeedPage(page);
  await feed.gotoTab("personal");
  const latest = await feed.latestTransaction();
  await expect(latest).toContainText(note);
});

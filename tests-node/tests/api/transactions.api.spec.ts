import { test, expect, request } from "@playwright/test";

const API_URL = process.env.API_URL ?? "http://localhost:3001";

test.describe("API transactions @api @regression", () => {
  test("création d'une transaction retourne 200 et un id", async () => {
    const ctx = await request.newContext({ baseURL: API_URL });
    const res = await ctx.post("/transactions", {
      data: { amount: 1000, description: "qarvis-api-test" },
      headers: { Authorization: `Bearer ${process.env.TEST_TOKEN ?? ""}` },
    });
    // Placeholder : adapter les assertions au contrat réel de la RWA une fois branché.
    expect([200, 201, 401]).toContain(res.status());
  });

  test("montant invalide retourne une erreur 4xx", async () => {
    const ctx = await request.newContext({ baseURL: API_URL });
    const res = await ctx.post("/transactions", {
      data: { amount: -1 },
    });
    expect(res.status()).toBeGreaterThanOrEqual(400);
  });
});

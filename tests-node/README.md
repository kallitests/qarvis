# tests-node — Univers Test (Playwright + TypeScript)

Suite de tests UI + API contre la [Cypress Real World App](https://github.com/cypress-io/cypress-realworld-app) (front `:3000`, API `:3001`).

## Installation

```bash
npm install
npx playwright install --with-deps
cp ../.env.example ../.env   # puis renseigner les valeurs
```

## Lancer les tests

```bash
npm run test:smoke   # gate, < 90s
npm run test          # suite complète
npm run test:api      # API uniquement
npm run test -- --ui  # mode debug interactif
```

## Conventions

- **POM strict** : aucun sélecteur en dehors de `src/pages/`.
- Sélecteurs par rôle/label/`data-testid`, jamais de `waitForTimeout` (assertions web-first).
- Tags : `@smoke`, `@regression`, `@negative`, + domaine (`@auth`, `@transactions`...).
- `.feature` Gherkin dans `features/`, step definitions dans `steps/` (compilés via `playwright-bdd`).

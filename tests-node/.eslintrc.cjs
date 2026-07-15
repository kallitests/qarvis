module.exports = {
  root: true,
  parser: "@typescript-eslint/parser",
  parserOptions: {
    project: "./tsconfig.json",
    sourceType: "module",
  },
  plugins: ["@typescript-eslint"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
  ],
  env: {
    node: true,
    es2022: true,
  },
  rules: {
    "@typescript-eslint/no-explicit-any": "warn",
    "no-restricted-syntax": [
      "error",
      {
        "selector": "CallExpression[callee.property.name='waitForTimeout']",
        "message": "Pas de waitForTimeout : utiliser des assertions web-first (expect(...).toBeVisible(), etc.)."
      }
    ]
  },
  ignorePatterns: ["node_modules", "playwright-report", "test-results", "blob-report", ".playwright-mcp"],
};

# QARVIS — Spécification technique

> Document dérivé de la **spec fonctionnelle QARVIS**. Il décrit la stack, l'outillage et le setup du poste de développement.
> **Note de version :** l'écosystème (Playwright, LangChain, MCP) bouge vite. Les versions ci-dessous sont des **planchers recommandés** — vérifie la dernière version stable au moment du setup. Principe non négociable rappelé : **MCP au *build* des tests, jamais en dépendance de *run* en CI.**

---

## 1. Objet & périmètre technique

Fournir un pipeline de test automatisé **clé en main** : tests UI + API (Playwright/TypeScript), génération/maintenance assistées par IA (MCP + agents Python), orchestration conteneurisée, CI/CD multi-plateforme, alerting, reporting et chatbot RAG. Deux « univers » techniques cohabitent :
- **Univers Test (Node/TypeScript)** : Playwright CLI, BDD, reporting.
- **Univers IA (Python)** : agents LangGraph, triage, RAG, evals.

Ils communiquent par **artefacts** (résultats de tests, logs, traces) et par une **API interne**, jamais par couplage direct en runtime CI.

---

## 2. Vue d'architecture technique

| Couche | Rôle | Technologies |
|---|---|---|
| **Test** | Exécuter UI + API, produire résultats | Playwright + TypeScript, playwright-bdd |
| **Génération IA** | Scaffolder tests & Page Objects | Playwright MCP + agent Python |
| **Cerveau IA** | Triage échecs, self-healing, evals | Python, LangChain, LangGraph, LangSmith |
| **RAG / Chatbot** | Répondre en langage naturel sur l'état qualité | LangChain + vector store + LLM |
| **Orchestration** | Environnements reproductibles | Docker, docker-compose (→ Kubernetes) |
| **CI/CD** | Exécuter le pipeline sur événement | GitHub Actions **et** GitLab CI |
| **Alerting** | Notifier selon canal | Webhooks Slack/Discord/Teams, email (SMTP/SES) |
| **Reporting** | Rapports dev + tendances décideurs | Mochawesome/Allure, JUnit XML, Power BI/QuickSight |
| **Cloud (différé)** | Control plane multi-tenant | AWS (App Runner/Fargate, Lambda, Aurora+pgvector, S3, DynamoDB, Cognito, SES, Bedrock) |

---

## 3. Stack technique détaillée

### 3.1 Univers Test (Node / TypeScript)
- **Node.js** ≥ 20 LTS (recommandé 22 LTS).
- **TypeScript** en mode `strict`.
- **Playwright Test** (`@playwright/test`) — runner, navigateurs Chromium/Firefox/WebKit.
- **playwright-bdd** — compile les `.feature` Gherkin en specs Playwright natives (parallélisme, traces, retries conservés).
- **Gestionnaire de paquets** : `pnpm` (rapide, disque efficace) ou `npm`.

### 3.2 MCP
- **`@playwright/mcp`** (Microsoft, Apache-2.0) — serveur d'automatisation navigateur piloté par agent, basé sur snapshots d'accessibilité. Usage : génération de sélecteurs/Page Objects. **Jamais en run CI.**

### 3.3 Univers IA (Python)
- **Python** ≥ 3.12.
- **LangChain** ≥ 1.0 — construction (tools, retrieval, `create_agent`). *Ne pas utiliser le legacy `AgentExecutor`.*
- **LangGraph** — runtime agentique (état, boucles, branches, checkpointing, human-in-the-loop). Couche recommandée pour les agents.
- **LangSmith** — observabilité/traçage des agents + evals.
- **LLM** : API Anthropic (Claude) en direct, ou **Amazon Bedrock** (Claude) pour rester dans AWS.
- **Gestionnaire d'environnement/paquets** : **`uv`** (Astral) — venv + install ultra-rapides.

### 3.4 RAG / Chatbot
- **Vector store** : `pgvector` sur PostgreSQL (local via Docker ; Aurora Serverless en cloud) — ou **Chroma** en local pour prototyper.
- **Embeddings** : modèle d'embeddings du fournisseur LLM (ou open-source local).
- **Orchestration RAG** : LangChain (loaders, splitters, retrievers).
- **Sources ingérées** : résultats de runs, rapports, logs, traces LangSmith, code de test, (option) tickets Jira/Linear.

### 3.5 Orchestration & Cloud
- **Docker** + **docker-compose** (POC). **Kubernetes** différé (scale multi-tenant).
- **AWS** (control plane, différé) : App Runner/ECS Fargate, Lambda, Aurora PostgreSQL Serverless v2 + pgvector, S3, DynamoDB, SQS/EventBridge, Cognito, Secrets Manager, SES, Bedrock. **IaC** : Terraform ou AWS CDK.

### 3.6 Reporting
- **Mochawesome** ou **Allure** (rapport HTML lisible dev).
- **JUnit XML** (intégration native CI).
- **Reporter `blob`** Playwright (fusion multi-shards).
- **Power BI** (embed) ou **QuickSight** (natif AWS) pour les tendances décideur.

---

## 4. Environnement de développement (IDE, plugins, outils)

### 4.1 IDE
- **VS Code** (référence) ou **Cursor** (fork de VS Code orienté IA, pertinent pour le dev assisté).
- **Extensions VS Code recommandées :**
  - `ms-playwright.playwright` — Playwright Test for VS Code (exécuter/débugger, codegen, picker de sélecteurs).
  - `dbaeumer.vscode-eslint` — ESLint.
  - `esbenp.prettier-vscode` — Prettier.
  - `ms-python.python` + `ms-python.vscode-pylance` — Python & typage.
  - `charliermarsh.ruff` — linter/formatter Python (Ruff).
  - `ms-azuretools.vscode-docker` — Docker.
  - `redhat.vscode-yaml` — YAML (CI, compose).
  - `github.vscode-github-actions` — GitHub Actions.
  - `cucumberopen.cucumber-official` — coloration/navigation Gherkin.
  - `eamodio.gitlens` — Git.

### 4.2 Runtimes & gestionnaires de version
- **nvm** (ou `fnm`) pour Node ; **`uv`** gère Python (peut installer les versions).
- **Docker Desktop** (ou Docker Engine + Compose).
- **Git** + compte GitHub/GitLab.

### 4.3 Qualité de code (outils)
- **Node/TS** : ESLint + `@typescript-eslint`, Prettier.
- **Python** : **Ruff** (lint + format, remplace Black/Flake8/isort), + `mypy` (typage) optionnel.
- **Pre-commit** : hooks Git (`pre-commit`) pour lint/format automatiques avant chaque commit.
- **EditorConfig** pour l'uniformité inter-éditeurs.

### 4.4 Outils annexes
- **`.env` + dotenv** (secrets locaux ; jamais commités).
- Client HTTP (Postman/Bruno/`httpie`) pour explorer l'API cible.
- Un compte **LangSmith** (traçage) et un accès **LLM** (clé API Anthropic ou AWS/Bedrock).

---

## 5. Setup du projet pas à pas

```bash
# 1) Node (via nvm)
nvm install 22 && nvm use 22

# 2) Univers Test — init Playwright + BDD
pnpm init
pnpm create playwright@latest          # ou: npm init playwright@latest
pnpm add -D playwright-bdd
npx playwright install --with-deps      # navigateurs + dépendances système

# 3) Qualité de code Node
pnpm add -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin prettier

# 4) Reporting
pnpm add -D mochawesome            # ou allure-playwright

# 5) MCP (pour la génération de tests, en local)
claude mcp add playwright npx @playwright/mcp@latest
claude mcp list                     # vérifier l'enregistrement

# 6) Univers IA — Python via uv
uv venv && source .venv/bin/activate
uv pip install langchain langgraph langsmith
uv pip install "psycopg[binary]" pgvector       # RAG (pgvector)
uv pip install ruff mypy pre-commit             # qualité

# 7) Hooks Git
pre-commit install

# 8) Conteneurs (app cible + services)
docker compose up -d                # RWA (démo) + Postgres/pgvector, etc.
```

> **Config MCP (client type Cursor/Desktop) — `mcp.json` :**
> ```json
> { "mcpServers": { "playwright": { "command": "npx", "args": ["@playwright/mcp@latest"] } } }
> ```

---

## 6. Structure du dépôt (monorepo)

```
qarvis/
├── tests-node/                  # UNIVERS TEST (TypeScript)
│   ├── src/
│   │   ├── pages/               # Page Objects
│   │   ├── fixtures/            # fixtures Playwright (auth, données)
│   │   └── utils/               # helpers (prix, tri, builders)
│   ├── tests/
│   │   ├── unit/                # base pyramide
│   │   ├── integration/         # UI ciblée
│   │   ├── e2e/                 # parcours complets
│   │   ├── api/                 # tests API
│   │   └── smoke/               # @smoke (gate)
│   ├── features/                # .feature Gherkin
│   ├── steps/                   # step definitions BDD
│   ├── playwright.config.ts
│   ├── tsconfig.json
│   ├── .eslintrc.cjs
│   └── package.json
├── ai-brain/                    # UNIVERS IA (Python)
│   ├── agents/                  # triage, self-healing (LangGraph)
│   ├── rag/                     # ingestion, retrievers, chatbot
│   ├── evals/                   # jeux d'évaluation + LangSmith
│   ├── pyproject.toml
│   └── .python-version
├── infra/
│   ├── docker/                  # Dockerfiles
│   ├── docker-compose.yml
│   └── iac/                     # Terraform/CDK (cloud, différé)
├── .github/workflows/ci.yml     # GitHub Actions
├── .gitlab-ci.yml               # GitLab CI
├── .pre-commit-config.yaml
├── .editorconfig
├── .env.example                 # variables attendues (sans valeurs)
└── README.md
```

---

## 7. Configuration & variables d'environnement

Fichier `.env.example` (valeurs jamais commitées) :

| Variable | Rôle |
|---|---|
| `BASE_URL` | URL de l'app cible (front) |
| `API_URL` | URL de l'API cible |
| `TEST_USER` / `TEST_PASSWORD` | identifiants de test (via secrets, pas en dur) |
| `ANTHROPIC_API_KEY` *(ou creds AWS/Bedrock)* | accès LLM |
| `LANGSMITH_API_KEY` / `LANGSMITH_PROJECT` | traçage/observabilité |
| `DATABASE_URL` | Postgres/pgvector (RAG) |
| `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL` / `TEAMS_WEBHOOK_URL` | alerting |
| `SMTP_*` *(ou creds SES)* | alerting email |

**Config Playwright (`playwright.config.ts`) — points clés :** projets par navigateur (chromium/firefox/webkit) + projet BDD ; reporters `html` + `blob` + `junit` + `mochawesome` ; `retries` en CI uniquement (jamais sur `@smoke`) ; `trace`/`screenshot`/`video` on-failure ; `webServer` si l'app est lancée localement.

---

## 8. CI/CD

**Pipeline commun (GitHub Actions & GitLab CI), même logique :**
1. `quality` : ESLint + Prettier check + `tsc --noEmit` ; côté Python : Ruff + mypy.
2. `smoke` (dépend de quality) : `bddgen && playwright test --grep @smoke`, chromium headless — **gate**.
3. `e2e` (dépend de smoke) : matrice navigateurs × **sharding** (`--shard=i/n`), reporter `blob`.
4. `report` (`if: always()`) : `merge-reports` → HTML + JUnit + Mochawesome ; upload artefacts ; job summary.
- Cache paquets + navigateurs Playwright ; `fail-fast: false` ; secrets via le coffre du CI.
- Déclencheurs : `push` (main), `pull_request`/merge request, `workflow_dispatch` + `schedule` (nightly) optionnel.

---

## 9. Couche IA / MCP (technique)

- **Génération** : un agent lit un snapshot d'accessibilité via MCP → propose Page Objects + scénarios ; l'humain valide et fige en code.
- **Triage** : agent LangGraph classe les échecs d'un run (régression / flaky / UI attendue / env) → résumé priorisé.
- **Self-healing** : détection de sélecteurs cassés + suggestion de correctif.
- **Evals** : jeu d'évaluation (précision du triage, pertinence des sélecteurs) tracé dans **LangSmith**.
- **Entrées** : artefacts JUnit/JSON des runs, logs, historique. **Sorties** : rapports lisibles + suggestions.

---

## 10. Couche RAG / Chatbot (technique)

- **Ingestion** : loaders sur résultats de runs, rapports, logs, code de test, traces ; **splitting** ; **embeddings** ; stockage dans `pgvector`.
- **Retrieval** : recherche vectorielle + (option) filtres métadonnées (par client/tenant, par date).
- **Interface** : widget web + (option) bot Slack/Discord.
- **Isolation** : cloisonnement des données par client (préparation multi-tenant).

---

## 11. Qualité, conventions & workflow Git

- **TypeScript strict**, pas de `any` injustifié ; **POM** systématique (aucun sélecteur hors Page Objects) ; sélecteurs par rôle/label/`data-testid` ; assertions web-first (pas de `waitForTimeout`).
- **Python** : typé, Ruff-clean.
- **Git** : branches `feat/…`, `fix/…` ; PR/MR obligatoire ; CI verte requise pour merge ; commits conventionnels (`feat:`, `fix:`, `chore:`).
- **Pre-commit** : lint/format bloquants avant commit.
- **Tags de test** cohérents : `@smoke`, `@regression`, `@negative`, + domaine (`@auth`, `@cart`…).

---

## 12. Sécurité & secrets

- **Aucun secret en clair** : `.env` local (git-ignored), coffre du CI en pipeline, **AWS Secrets Manager** en cloud.
- Accès **moindre privilège** aux CI/repos des clients (tokens dédiés, scoping minimal).
- Isolation des données par tenant dès le RAG.
- `browser_run_code_unsafe` du MCP : **local uniquement**, jamais en pipeline.

---

## 13. Observabilité

- **LangSmith** : traçage de chaque décision d'agent (triage, chatbot) + dashboards evals.
- **Artefacts CI** : traces Playwright, screenshots, vidéos on-failure.
- **Métriques produit** : taux de flakiness, durée des runs, couverture dans le temps (alimentent Power BI/QuickSight).

---

## 14. Checklist de mise en route (onboarding dev)

- [ ] Node 22 LTS installé (nvm) ; `uv` installé.
- [ ] Repo cloné ; `.env` créé depuis `.env.example`.
- [ ] `pnpm install` + `npx playwright install --with-deps`.
- [ ] `uv venv` + `uv pip install` (deps IA).
- [ ] `pre-commit install`.
- [ ] MCP enregistré (`claude mcp list` OK).
- [ ] `docker compose up -d` (app cible + pgvector).
- [ ] Extensions VS Code installées.
- [ ] Comptes/API : LLM (Anthropic/Bedrock) + LangSmith configurés.
- [ ] `pnpm test --grep @smoke` passe en local.
- [ ] Pipeline CI vert sur une PR de test.

> Vérifie les **dernières versions stables** (Playwright, `@playwright/mcp`, LangChain/LangGraph, Node/Python) au moment du setup : l'écosystème évolue vite et certaines APIs (ex. LangChain pré-1.0) sont obsolètes.

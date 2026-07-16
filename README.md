# 🤖 QARVIS

> **QA + JARVIS — the AI copilot that keeps your test suite green.**
> Playwright (UI + API) generated and maintained via MCP, triaged by LangGraph agents, run on Docker across multi-CI, alerted and reported end to end.

[![Status](https://img.shields.io/badge/status-POC-orange?style=flat-square)](https://github.com/kallitests/qarvis)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![Playwright](https://img.shields.io/badge/Playwright-MCP-green?style=flat-square&logo=playwright)](https://playwright.dev)
[![Python](https://img.shields.io/badge/python-3.12+-blue?style=flat-square&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangChain-LangGraph-blueviolet?style=flat-square)](https://langchain.com)
[![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat-square&logo=docker)](https://docker.com)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat-square&logo=githubactions)](https://github.com/features/actions)

---

## 🗺️ Table of Contents

- [Why QARVIS?](#-why-qarvis)
- [What it does](#%EF%B8%8F-what-it-does)
- [Architecture](#-architecture)
- [Stack](#-stack)
- [Project Structure](#-project-structure)
- [Chat/RAG & Wiki](#-chatrag--wiki)
- [Getting Started](#-getting-started)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Conventions](#-conventions)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 💡 Why QARVIS?

Startups that ship fast are often stuck between two bad options: **no tests** (praying at every deploy) or **rotten tests** (red, flaky, ignored). Hiring a dedicated SDET costs €50–70k/year plus the hiring effort.

**QARVIS is the third way** — a subscription service that installs, grows, and **keeps a UI + API test suite green on every deployment**, without the client hiring anyone.

```
Playwright CLI (UI + API) ──▶ MCP-assisted generation ──▶ AI triage & self-healing ──▶ Multi-CI ──▶ Alerts & Reports
```

The POC in this repo runs against the [Cypress Real World App](https://github.com/cypress-io/cypress-realworld-app) (front `:3000`, API `:3001`) — a realistic fintech-style app (payments, feed, notifications) used as a demo target, transposable to any client's product.

> **Non-negotiable principle:** MCP (`@playwright/mcp`) is used at **test-build time only** (selector/Page Object generation) — **never as a run-time dependency in CI**. The AI proposes, a human validates and freezes the result into versioned code.

---

## ⚙️ What It Does

| Layer | Role | Description |
|-------|------|-------------|
| 🧪 **Test** | Execute UI + API | Playwright + TypeScript, `playwright-bdd` (Gherkin), smoke/regression/negative suites |
| 🧠 **AI generation** | Scaffold tests & Page Objects | Playwright MCP + Python agent, from an accessibility snapshot of the target app |
| 🤖 **AI brain** | Triage & self-healing | LangGraph agent classifies failures (real regression / flaky / expected UI change / env issue), suggests selector fixes |
| 💬 **RAG chatbot** | "Ask QARVIS" | LLM + RAG conversational assistant for Q&A on test coverage, flakiness trends, and why last night's run is red — see [Chat/RAG & Wiki](#-chatrag--wiki) |
| 📚 **AI-enriched wiki** | "QARVIS Wiki" | Confluence-style documentation space with AI-assisted drafting, summarizing, and semantic search — see [Chat/RAG & Wiki](#-chatrag--wiki) |
| 🐳 **Orchestration** | Reproducible environments | Docker / docker-compose (Kubernetes later, for multi-tenant scale) |
| 🔁 **CI/CD** | Run the pipeline on events | GitHub Actions **and** GitLab CI, same logic on both |
| 🚨 **Alerting** | Notify on regressions | Slack / Discord / Teams webhooks, email (SMTP/SES) |
| 📊 **Reporting** | Dev + decision-maker views | Mochawesome/Allure + JUnit XML, Power BI/QuickSight for trends |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                              QARVIS Pipeline                          │
│                                                                       │
│  ┌───────────────┐    ┌────────────────┐    ┌───────────────────┐    │
│  │ Playwright MCP│───▶│  Page Objects  │───▶│  Playwright Tests │    │
│  │ (build-time)  │    │  + Gherkin BDD │    │  UI + API + Smoke │    │
│  └───────────────┘    └────────────────┘    └─────────┬──────────┘    │
│                                                        │              │
│  ┌───────────────┐    ┌────────────────┐    ┌─────────▼──────────┐    │
│  │ Slack/Discord/│◀───│  Mochawesome / │◀───│  LangGraph Triage  │    │
│  │ Teams / Email │    │  JUnit / Power │    │  (regression vs    │    │
│  │  (alerts)     │    │  BI reporting  │    │   flaky vs env)    │    │
│  └───────────────┘    └────────────────┘    └─────────┬──────────┘    │
│                                                        │              │
│                                                        ▼              │
│              ┌──────────────────────┐    ┌──────────────────────┐    │
│              │  Ask QARVIS (chat)   │◀──▶│    QARVIS Wiki       │    │
│              │  LLM + RAG · React   │    │  AI-enriched docs ·  │    │
│              │  widget on pgvector  │    │  React · pgvector    │    │
│              └──────────────────────┘    └──────────────────────┘    │
│                                                                       │
│  🐳 Docker / docker-compose  ·  🔁 GitHub Actions & GitLab CI          │
└───────────────────────────────────────────────────────────────────────┘
```

Two "universes" cohabit and communicate only through **artifacts** (test results, logs, traces) and an internal API — never through direct runtime coupling in CI:

- **Test universe (Node/TypeScript):** Playwright CLI, BDD, reporting.
- **AI universe (Python):** LangGraph agents, triage, RAG, evals, the Ask QARVIS chat API, and the QARVIS Wiki backend.
- **Client universe (React):** `apps/chat-ui` and `apps/wiki-ui`, the two frontends consuming the AI universe's APIs.

---

## 🧰 Stack

| Layer | Technology |
|-------|-----------|
| **Test execution** | [Playwright Test](https://playwright.dev) + TypeScript (strict) · [`playwright-bdd`](https://github.com/vitalets/playwright-bdd) |
| **Test generation** | [`@playwright/mcp`](https://github.com/microsoft/playwright-mcp) (Microsoft) — build-time only |
| **AI agents** | [LangChain](https://langchain.com) ≥ 1.0 · [LangGraph](https://langchain-ai.github.io/langgraph/) · [LangSmith](https://smith.langchain.com) (observability/evals) |
| **LLM** | Anthropic Claude (direct API or Amazon Bedrock) |
| **RAG / vector store** | `pgvector` on PostgreSQL (Chroma for local prototyping) |
| **Chat/RAG & Wiki backend** | Python (FastAPI) — see [Chat/RAG & Wiki](#-chatrag--wiki) |
| **Chat/RAG & Wiki frontend** | React (TypeScript) — `apps/chat-ui`, `apps/wiki-ui` |
| **Orchestration** | Docker + docker-compose (Kubernetes deferred) |
| **CI/CD** | GitHub Actions **and** GitLab CI (feature parity) |
| **Reporting** | Mochawesome / Allure, JUnit XML, Power BI / QuickSight |
| **Package managers** | `pnpm`/`npm` (Node) · [`uv`](https://github.com/astral-sh/uv) (Python) |
| **Code quality** | ESLint + Prettier (TS) · Ruff + mypy (Python) · `pre-commit` |

---

## 📁 Project Structure

```
qarvis/
├── tests-node/                  # TEST UNIVERSE (TypeScript)
│   ├── src/
│   │   ├── pages/               # Page Objects (LoginPage, FeedPage, NewTransactionPage)
│   │   ├── fixtures/            # Playwright fixtures (auth, seed data)
│   │   └── utils/               # helpers (builders, amounts)
│   ├── tests/
│   │   ├── smoke/                # critical path, gate, < 90s
│   │   ├── e2e/                  # auth, transactions, negative
│   │   ├── api/                  # backend :3001 tests
│   │   ├── integration/ · unit/  # pyramid base
│   ├── features/                 # .feature Gherkin scenarios
│   ├── steps/                    # BDD step definitions
│   ├── playwright.config.ts
│   ├── tsconfig.json
│   └── package.json
├── ai-brain/                     # AI UNIVERSE (Python)
│   ├── agents/                   # triage, self-healing (LangGraph)
│   ├── rag/                      # ingestion, retrievers, "Ask QARVIS" chat API (FastAPI)
│   ├── wiki/                     # QARVIS Wiki backend — pages/spaces/versions, AI draft/summarize/search
│   ├── evals/                    # LangSmith-traced evaluation sets (chat + wiki golden sets)
│   └── pyproject.toml
├── apps/                         # CLIENT UNIVERSE (React)
│   ├── chat-ui/                  # "Ask QARVIS" chat widget
│   └── wiki-ui/                  # QARVIS Wiki editor + semantic search
├── infra/
│   ├── docker/                   # Dockerfile (Cypress RWA target app)
│   ├── docker-compose.yml        # RWA + Postgres/pgvector
│   └── iac/                      # Terraform/CDK (AWS control plane, deferred)
├── docs/                         # functional & technical specs
├── .github/workflows/ci.yml      # GitHub Actions pipeline
├── .pre-commit-config.yaml
├── .editorconfig
├── .env.example
└── README.md
```

---

## 💬 Chat/RAG & Wiki

QARVIS ships two AI-facing products on top of the same backbone (`ai-brain/`, `pgvector`, Claude):

- **Ask QARVIS** — an LLM + RAG chatbot answering natural-language questions about the client's test suite
  (coverage, flakiness, why last night's run is red), always grounded in retrieved evidence with cited
  sources, never a free-floating guess.
- **QARVIS Wiki** — a Confluence-style, AI-enriched documentation space: draft, summarize, and semantically
  search internal docs, cross-linked with the test data indexed for Ask QARVIS.

Both are backend Python (FastAPI, reusing the LangChain/LangGraph stack) + frontend React
(`apps/chat-ui`, `apps/wiki-ui`), covered by the same three-tier testing discipline as the rest of the repo:
unit tests on ingestion/retrieval, functional evals on answer/summary accuracy (LangSmith), and load tests on
concurrent chat/search traffic.

Full functional and technical specification — indexing/retrieval mechanisms, LLM/API integration, testing
strategy, performance targets, repo placement: **[`docs/qarvis-rag-wiki-spec.md`](docs/qarvis-rag-wiki-spec.md)**.

---

## 🚀 Getting Started

```bash
# 1. Clone & environment variables
git clone git@github-kallitests:kallitests/qarvis.git
cd qarvis
cp .env.example .env   # fill in BASE_URL, API_URL, TEST_USER/PASSWORD, ANTHROPIC_API_KEY…

# 2. Target app + services (Cypress RWA + Postgres/pgvector)
cd infra && docker compose up -d && cd ..

# 3. Test universe
cd tests-node
npm install
npx playwright install --with-deps
npm run test:smoke     # gate, < 90s
npm run test            # full suite
cd ..

# 4. AI universe (optional at POC stage)
cd ai-brain
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
cd ..

# 5. Git hooks
pre-commit install
```

---

## 🔁 CI/CD Pipeline

`.github/workflows/ci.yml` runs the same logic as its GitLab CI counterpart, in four gated stages:

| Stage | What it does |
|-------|--------------|
| 1. **quality** | ESLint + Prettier check + `tsc --noEmit` · Ruff + mypy on `ai-brain/` |
| 2. **smoke** *(gate)* | `bddgen && playwright test --grep @smoke`, Chromium headless, no retries |
| 3. **e2e** | Browser matrix (chromium/firefox/webkit) × sharding, `blob` reporter |
| 4. **report** | `merge-reports` → HTML + JUnit + Mochawesome, artifact upload, job summary, Slack alert on failure |

Triggers: `push` on `main`, `pull_request`, `workflow_dispatch`, nightly `schedule`.

**Secrets/variables to configure** (Settings → Secrets and variables → Actions):
- Secrets: `TEST_USER`, `TEST_PASSWORD`, `SLACK_WEBHOOK_URL` (+ `ANTHROPIC_API_KEY`, `LANGSMITH_API_KEY` if the AI universe runs in CI).
- Variables: `BASE_URL`, `API_URL` (defaults to `localhost` otherwise).

---

## 📐 Conventions

- **TypeScript strict**, no unjustified `any`; **POM everywhere** (no selector outside Page Objects); role/label/`data-testid` selectors; web-first assertions (no `waitForTimeout`).
- **Python** typed, Ruff-clean.
- **Git**: `feat/…` / `fix/…` branches, PR required, green CI required to merge, conventional commits.
- **Test tags**: `@smoke`, `@regression`, `@negative`, + domain (`@auth`, `@transactions`…).

---

## 📌 Roadmap

Five phases, each shipping a demonstrable deliverable (see `docs/qarvis-poc-spec.md` §7 for full detail):

- [x] **Phase 0 — Foundations**: repo structure, RWA running locally via Docker, baselines decided.
- [x] **Phase 1 scaffold — Playwright core**: smoke/regression/API suites, Page Objects, BDD, Mochawesome (test code is placeholder, to be wired against a running RWA instance).
- [x] **Phase 2 scaffold — Containerization & multi-CI**: docker-compose, GitHub Actions pipeline (this repo); GitLab CI equivalent and alerting wiring still to do.
- [ ] **Phase 3 — QARVIS AI brain**: MCP-assisted generation, LangGraph triage agent, flaky detection & self-healing, LangSmith observability + evals, **Ask QARVIS chat/RAG** (ingestion, retrieval, chat API, `chat-ui`) — see `docs/qarvis-rag-wiki-spec.md`.
- [ ] **Phase 4 — Decision-maker reporting & packaging**: Power BI dashboard, tier mapping, sales page, Loom demo, **QARVIS Wiki** (AI-enriched docs backend + `wiki-ui`, cross-linked with test data) — see `docs/qarvis-rag-wiki-spec.md`.
- [ ] **Phase 5 — Scalability**: docker-compose → Kubernetes, templated client onboarding, multi-tenant alerting/reporting.

---

## 👤 Author

**Khalid Hafid-Medheb**
Senior SDET & AI Engineer — specialized in autonomous QA agents (HealthTech / BioTech)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-khalid--hafid--medheb-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/khalid-hafid-medheb-40451aa8/)
[![GitHub](https://img.shields.io/badge/GitHub-kallitests-181717?style=flat-square&logo=github)](https://github.com/kallitests)
[![Kallitests](https://img.shields.io/badge/Org-Kallitests-6e40c9?style=flat-square)](https://github.com/kallitests)

---

*Built with 🎭 Playwright · 🦜 LangChain/LangGraph · 🧠 Claude (Anthropic)*
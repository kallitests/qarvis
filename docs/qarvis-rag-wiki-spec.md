# QARVIS — Chat/RAG & AI-Enriched Wiki Specification (EN)

> Companion document to the French **spec fonctionnelle** (`qarvis-poc-spec.md`, §4.5) and **spec technique**
> (`qarvis-spec-technique.md`, §3.4 / §10). It expands the "Ask QARVIS" chatbot into a full LLM+RAG
> specification and introduces a new module: an **AI-enriched documentation platform ("QARVIS Wiki")**,
> Confluence-style, for the QARVIS product itself and — longer term — for client teams.
>
> Written in English on purpose: this is the reference spec for the two modules that map directly onto a
> "LLM/RAG chatbot + AI-enriched Confluence-like wiki" engineering brief (backend Python, frontend React,
> RAG indexing/search, API integration, unit/functional/load testing, CI/CD).

---

## 1. Purpose & scope

Two modules, sharing one AI backbone:

| Module | What it is | Analogous to |
|---|---|---|
| **1. Ask QARVIS (Chat/RAG)** | Conversational assistant answering natural-language questions about the client's test suite, grounded in the client's own test data via RAG. | An internal ChatGPT-style assistant, scoped to test/quality data. |
| **2. QARVIS Wiki** | AI-enriched internal documentation space: write, search, summarize, and keep living docs about the product, its tests, and its known issues. | Confluence, with an AI co-writer/searcher layered on top. |

Both modules sit inside the existing **AI universe (Python)** of the monorepo and expose a **React frontend**.
They are functionally independent (a client can have one without the other) but share: the LLM provider layer,
the vector store, the ingestion/indexing pipeline, and the CI/testing discipline described below.

Out of scope for both modules (POC stage): multi-tenant isolation at the infra level (schema-level only, see
§2.2/§3.4), fine-tuning of models, offline/on-device inference.

---

## 2. Module 1 — Ask QARVIS (Chatbot, LLM + RAG)

### 2.1 Overview

A conversational assistant (web widget, optional Slack/Discord bot) that answers questions about the health
of the client's test suite by retrieving relevant context before generating an answer — never answering from
the model's parametric memory alone. This is what "RAG" (Retrieval-Augmented Generation) means in practice
here: retrieve first, generate second, always cite the source.

Already specified at a high level in `qarvis-poc-spec.md` §4.5; this section makes the "how" explicit.

### 2.2 Indexing & document retrieval mechanisms

**Ingestion pipeline** (`ai-brain/rag/`):

1. **Loaders** — pull from: run history (results, durations, flakiness over time), Mochawesome/JUnit reports,
   failure logs, the test code itself (scenarios, coverage), LangSmith triage traces, and optionally client
   specs/tickets (Jira, Linear, Notion) to cross-reference requirements ↔ tests.
2. **Splitting** — chunking strategy adapted per source type: semantic/paragraph chunking for prose docs
   (specs, tickets), structural chunking for test code (per test case / per `describe` block), row-based
   chunking for structured run results.
3. **Embeddings** — provider embedding model (Anthropic/Bedrock-compatible) or a local open-source model for
   cost-sensitive tiers.
4. **Storage** — `pgvector` on PostgreSQL (Aurora Serverless in the cloud tier), `Chroma` for local
   prototyping. Metadata columns: `client_id`, `source_type`, `created_at`, `test_id` (when applicable) —
   this is what makes multi-tenant filtering and freshness checks possible.
5. **Retrieval** — hybrid search: vector similarity + metadata filters (client/tenant, date range, source
   type) + optional keyword pre-filter (BM25) for exact identifiers (test names, ticket IDs) that embeddings
   alone handle poorly.
6. **Re-ranking (v2)** — a lightweight cross-encoder re-rank pass on the top-k candidates before they are
   handed to the LLM, to reduce hallucination from loosely-relevant chunks.

**Freshness:** ingestion runs incrementally after every CI run (new results/logs) and on-demand for
documentation sources; a nightly full re-index job guards against drift.

### 2.3 Integrating the LLM & APIs

- **LLM access layer**: a thin abstraction (LangChain `create_agent` / LangGraph) over the Anthropic API
  (direct) or Amazon Bedrock — so the provider can be swapped without touching retrieval logic.
- **Tool-calling**: the agent can call internal tools beyond pure retrieval — e.g. "fetch the last N runs for
  test X", "get current flakiness score" — so answers can combine RAG context with live structured queries.
- **API surface exposed to the frontend**: a REST/JSON API (`POST /chat`, `GET /chat/history`,
  `POST /chat/feedback`) fronting the LangGraph agent; streaming responses (SSE or WebSocket) for
  perceived latency.
- **Guardrails**: every answer must cite its source chunks (run ID, report link, doc reference); the agent
  refuses to answer when retrieval returns nothing above a similarity threshold, rather than guessing.

### 2.4 Testing strategy (unit / functional / load)

| Level | What is tested | Tooling |
|---|---|---|
| **Unit** | Loaders (parsing correctness per source type), splitters (chunk boundaries), embedding calls (mocked), retrieval filters (metadata correctness) | `pytest` on `ai-brain/rag/` |
| **Functional / eval** | End-to-end question → answer correctness against a curated golden set (e.g. "why is last night's run red?"); retrieval precision/recall; citation accuracy | LangSmith evals (`ai-brain/evals/`), scored automatically per PR |
| **Load** | Concurrent chat sessions, vector store query latency under load, LLM API rate-limit handling & backoff, streaming stability under many simultaneous connections | `locust` or `k6` against the chat API, run in a dedicated CI job (not on every PR — nightly/pre-release) |

Regression gate: any drop in eval accuracy (precision/recall/citation rate) below an agreed threshold blocks
merge, same discipline as the Playwright `@smoke` gate.

### 2.5 Performance & UX optimization

- **Latency budget**: target < 3s to first token (streaming), < 8s full answer for a typical question.
- **Caching**: cache embeddings for unchanged sources; cache frequent queries (e.g. "status of last run") at
  the API layer with short TTL.
- **UX**: streaming tokens to the widget, visible "sources used" panel, follow-up question suggestions,
  graceful degradation message when retrieval confidence is low (no hallucinated fallback).
- **Cost control**: token-usage quotas per client tier (Smoke / Regression / Quality Partner), model routing
  (cheaper model for simple status questions, stronger model for cross-referencing/coverage-gap analysis).

---

## 3. Module 2 — QARVIS Wiki (AI-enriched documentation platform)

### 3.1 Overview

A Confluence-style internal documentation space, scoped first to the QARVIS project itself (test strategy,
architecture decisions, onboarding, runbooks) and designed to be reusable as a client-facing deliverable
later. The AI layer assists with **writing** (drafting/expanding from bullet points), **summarizing**
(long pages/threads → digest), and **finding** (natural-language search across all pages) — it does not
replace human authorship, it removes the friction around it.

This is a new module; it does not exist yet in the current repo structure (see §4 for placement).

### 3.2 Backend / frontend architecture

- **Backend (Python)**: FastAPI service exposing CRUD for pages/spaces, version history, and the AI
  endpoints (draft, summarize, search). Reuses the same LLM access layer and vector store as Module 1
  (§2.3, §2.2) — a wiki page is just another document type in the shared ingestion pipeline.
- **Frontend (React)**: a dedicated app (`apps/wiki-ui/`) — page editor (Markdown-based, live preview),
  space/page tree navigation, AI sidebar (draft/summarize/ask-this-page actions), full-text + semantic
  search bar.
- **Data model**: `Space > Page > Version`, each `Page` re-indexed into the vector store on save; page
  metadata (`space_id`, `tags`, `updated_at`, `author`) mirrors the RAG metadata schema from §2.2 for
  consistent filtering.

### 3.3 Integration APIs

- **Internal**: shares the chat API's LLM/RAG backbone (`ai-brain/`) rather than duplicating it — a wiki
  page can be asked about directly ("summarize this page", "what does this page say about X") through the
  same chat interface described in Module 1.
- **External (v2, roadmap)**: import/export connectors to existing docs tools the client may already use
  (Confluence, Notion) so QARVIS Wiki can bootstrap from — or feed into — an existing knowledge base rather
  than forcing a migration on day one.
- **Auth**: same session/auth layer as the rest of the control plane (deferred cloud phase — see README
  roadmap Phase 6).

### 3.4 Indexing & RAG search mechanisms

Same pipeline as §2.2, with wiki-specific additions:

- **Chunking**: per-heading chunking (a page section is a natural retrieval unit) rather than fixed-size
  windows.
- **Cross-linking**: when a page is indexed, detected references to test IDs, run IDs, or other pages are
  stored as edges — enabling "what documentation exists for this failing test?" queries that combine the
  wiki index with the test-data index from Module 1.
- **Staleness detection**: pages not updated after a related test/feature has materially changed are
  flagged for review (a lightweight diff-based heuristic, not a full semantic staleness model at POC stage).

### 3.5 Quality, performance & reliability

- **Reliability target**: wiki search results returned in < 1s (p95) for the POC-scale corpus; AI-assisted
  draft/summarize under the same latency budget as chat (§2.5).
- **Data integrity**: version history is append-only; AI-generated drafts are always presented as a diff the
  human must accept, never auto-committed.
- **Testing**: same three-tier discipline as Module 1 (§2.4) — unit tests on backend CRUD + indexing logic,
  functional evals on summarize/search accuracy against a golden set of pages, load tests on concurrent
  editing + search.

---

## 4. Shared foundations & repo placement

Both modules extend the existing monorepo rather than starting a new one. Additions to the structure
documented in the README / `qarvis-spec-technique.md` §6:

```
qarvis/
├── ai-brain/
│   ├── rag/                     # EXISTING — shared ingestion, retrieval, embeddings (Module 1 backend logic)
│   │   ├── ingestion/           # loaders, splitters (test data + wiki pages)
│   │   ├── retrieval/           # hybrid search, re-ranking
│   │   └── api/                 # FastAPI chat endpoints (/chat, /chat/history, /chat/feedback)
│   ├── wiki/                    # NEW — wiki-specific backend (pages, spaces, versions, staleness detection)
│   │   ├── models/               # Space / Page / Version
│   │   └── api/                  # FastAPI wiki endpoints (CRUD, draft, summarize, search)
│   ├── agents/                  # EXISTING — triage, self-healing
│   └── evals/                   # EXISTING — extended with chat + wiki golden sets
├── apps/                        # NEW — frontend applications (React)
│   ├── chat-ui/                 # "Ask QARVIS" widget (Module 1)
│   └── wiki-ui/                 # QARVIS Wiki editor & search (Module 2)
├── tests-node/                  # EXISTING — Playwright UI/API suite; extended to cover chat-ui and wiki-ui
└── docs/
    └── qarvis-rag-wiki-spec.md  # this document
```

- **Backend**: Python (FastAPI), reusing `ai-brain/`'s existing LangChain/LangGraph/LangSmith stack.
- **Frontend**: React (TypeScript), consistent with the `tests-node/` TypeScript toolchain (shared ESLint/
  Prettier config).
- **CI/CD**: both new apps are added as new gated stages in `.github/workflows/ci.yml` /
  `.gitlab-ci.yml`, following the existing four-stage pattern (`quality` → `smoke` → `e2e` → `report`);
  Playwright E2E coverage for `chat-ui`/`wiki-ui` lives under `tests-node/tests/e2e/chat/` and
  `tests-node/tests/e2e/wiki/`.
- **Tooling note**: development on this module is expected to lean on **Claude Code** for the backend/agent
  scaffolding and the Claude API/SDK for the LLM integration layer itself — consistent with the rest of the
  AI universe.

---

## 5. Roadmap placement

Both modules extend **Phase 3 — QARVIS AI brain** and **Phase 4 — Decision-maker reporting & packaging** from
the main roadmap (`README.md` / `qarvis-poc-spec.md` §7):

- **Phase 3** — Ask QARVIS: ingestion pipeline, retrieval, chat API, `chat-ui` widget, eval set.
- **Phase 4** — QARVIS Wiki: backend CRUD + AI endpoints, `wiki-ui`, cross-linking with test data, packaged
  as part of the Quality Partner tier deliverable.

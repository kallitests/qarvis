# 🕵️ QARVIS — Step 1: Validating the Quality of Generated Gherkin

> **What this POC proves (or disproves):** is a user story + a URL enough to produce
> smoke-test Gherkin scenarios that are *actually usable*?
> Until the answer is "yes" on ~10 real cases, **do not build the Jira plugin.**
> The button is the packaging; this is the product.

---

## 🗺️ Table of Contents

- [Why no MCP here?](#-why-no-mcp-here)
- [Installation](#-installation)
- [Usage](#-usage)
- [How the script fights hallucination](#-how-the-script-fights-hallucination)
- [Review Grid (the real deliverable)](#-review-grid-the-real-deliverable)
- [Known Limitations](#-known-limitations)
- [What's Next?](#-whats-next)

---

## 🤖 Why No MCP Here?

The Playwright MCP exists so that an **agent** can drive a browser in a loop. Here we want
something **deterministic and scriptable**. So we use `locator.aria_snapshot()` directly —
this is exactly the accessibility tree that the MCP relies on under the hood, without the
agent loop. Simpler, cheaper, reproducible.
The MCP will take its place later, at the *test-build* stage.

---

## 📦 Installation

```bash
pip install -r requirements.txt
python -m playwright install chromium

cp .env.example .env      # then fill in ANTHROPIC_API_KEY
```

---

## ⚙️ Usage

```bash
# Single case
python generate_gherkin.py \
  --url https://www.saucedemo.com \
  --story "As a customer I want to log in to access the catalog"

# Batch (recommended: this is how you judge quality)
python generate_gherkin.py --cases cases.example.yaml

# Page behind a login: record the session once, reuse it afterward
python -m playwright codegen --save-storage=auth.json https://my-app.com
python generate_gherkin.py --url https://my-app.com/dashboard \
  --story "..." --storage-state auth.json
```

The `.feature` files land in `features/`.

---

## 🧠 How the Script Fights Hallucination

This is the heart of the POC. The model is **never** asked to invent steps from the story
alone. The pipeline is:

| Step | Description |
|------|-------------|
| 1️⃣ **Capture** | Playwright opens the URL and extracts the accessibility tree (roles + accessible names). This is the *source of truth*. |
| 2️⃣ **Constraint** | The system prompt enforces: every step must map to an element present in the snapshot; anything unverifiable becomes a `# TODO(to verify)` instead of being invented. |
| 3️⃣ **Business language** | CSS/XPath/`data-testid` selectors are forbidden in the steps. |

This exact mechanism is what you need to evaluate below.

---

## 🎯 Review Grid (the Real Deliverable)

Generate the 3 example cases, then score **each file** on these 7 criteria.
Simple rating: ✅ compliant / ⚠️ borderline / ❌ failed.

| # | Criterion | Question to ask yourself |
|---|-----------|---------------------------|
| 1 | **Grounding** | Does every step map to an element that *actually* exists on the page? |
| 2 | **Zero invention** | Did the model invent a screen, field, or message that doesn't exist? |
| 3 | **Honesty** | Is what it couldn't verify properly marked `# TODO`, rather than guessed? |
| 4 | **Business language** | Would a PM understand these scenarios? No technical selector leaked through? |
| 5 | **Genuinely a smoke test** | 1-3 scenarios on the critical path — or a pointless exhaustive list? |
| 6 | **Implementability** | Can you write the Playwright step definitions without guessing? |
| 7 | **Real time savings** | Is fixing this output faster than writing it yourself? |

### The 3 Example Cases Are a Deliberate Trap

| Case | What it tests | Expected verdict if the POC is sound |
|------|----------------|----------------------------------------|
| `login_saucedemo` | Correct story + rich page | Clean, implementable Gherkin |
| `story_vague` | "I want to log in," nothing more | Must stay **sober** and rely on the page, not embellish |
| `story_hors_perimetre` | Mentions password reset by email — **absent from the page** | Must produce **TODOs**, must not invent a form |

> **The decisive case is `story_hors_perimetre`.** If it invents a password-reset screen
> that doesn't exist, the concept doesn't hold and the prompt needs rework before anything
> else. If it honestly says "I don't see this on the page," you've got something.

### Decision Criterion (to be fixed BEFORE looking at the results)

- **≥ 7 out of 10 cases usable after minor edits** → the concept holds. Move on to
  Step 2 (Jira Automation webhook), then the Forge plugin.
- **Between 4 and 6** → the concept holds but the prompt/grounding needs rework.
  Iterate on `SYSTEM_PROMPT`, not the plumbing.
- **≤ 3** → do not build the plugin. The problem is upstream (story quality,
  or the need for a real multi-page crawl instead of a single-page snapshot).

---

## ⚠️ Known Limitations

- **Single page only.** The snapshot doesn't cover multi-screen flows (3-step
  checkout...). Expected behavior: the model TODO-izes the rest. A multi-page crawl
  is a Step 2 project, not Step 1.
- **Authenticated pages** → require `--storage-state`. This is the identified wall: in
  production, test credentials per client will be needed.
- **Truncated snapshot** on very heavy pages (`QARVIS_MAX_SNAPSHOT_CHARS`).
  The script warns you when this happens.
- **Output = draft.** A human reviews and signs off. That's the QARVIS principle:
  *AI proposes, the human guarantees.*

---

## 🚀 What's Next?

1. ✅ **Here** — is the quality up to standard? (this POC)
2. Webhook: *Automation for Jira* rule → `Send web request` to this hosted script.
   Triggered from Jira **without writing a plugin**.
3. Forge app + Atlassian Marketplace — only once 1 and 2 are validated.

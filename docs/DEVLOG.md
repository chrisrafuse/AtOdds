# DEVLOG.md
## Author: Chris Rafuse
## Project: Betstamp Odds Intelligence Agent
## Version: 2.0 (Phase 8–10 complete)
## Approach: Deterministic Core + LLM Function-Calling Agent + Math-Transparent Briefing

---

## 0. Objective

Build a production-grade AI odds analysis system that:
- Computes market truth **deterministically** — LLM never touches numbers
- Uses an LLM (OpenAI / Claude / Gemini) with **function calling** for orchestration + explanation
- Produces a structured daily briefing with **inline math proofs**
- Supports grounded multi-turn chat grounded in the briefing
- Shows a full **agent reasoning trace** (which tools were called, in what order, with what results)
- Ranks sportsbooks by vig, best-line frequency, freshness, and outlier rate
- Deploys to Railway or Fly.io with a single command

---

## 1. Core Architecture Decision

**Chosen structure:**
```
Raw odds data
    ↓
packages/core_engine/   ← deterministic math only (no LLM)
    ↓
packages/tools/         ← tool registry wrapping core functions
    ↓
packages/llm/           ← LLM adapter (OpenAI / Anthropic / Gemini / mock)
    ↓
packages/agent/         ← LLM calls tools, collects findings
    ↓
packages/reporting/     ← briefing + rankings from findings
    ↓
packages/chat/          ← grounded Q&A (LLM or deterministic fallback)
    ↓
apps/web/               ← FastAPI + vanilla JS frontend
```

**Why this separation matters:**
Most AI odds systems fail because the model does math and hallucinates numbers. Here the model is only allowed to *call tools* — the math is computed by `odds_math.py` which has no LLM dependency whatsoever.

---

## 2. AI Usage Log

### Phase 1–7: Deterministic Engine + Web API

### Phase 8–10: LLM Integration & Deployment (March 2026)

**Date: 2026-03-26**
**Status: ✅ COMPLETE - Production Ready**

#### LLM Agent Integration (Phase 8)
- ✅ Implemented `packages/llm/` with adapters for OpenAI, Anthropic, Gemini, and Mock
- ✅ Created tool schemas with proper JSON Schema format for function calling
- ✅ Built `packages/agent/agent.py` with `execute_CR_analysis_pipeline()`
- ✅ Added LLM-powered analysis summaries and agent reasoning traces
- ✅ Integrated chat interface with both LLM and deterministic fallbacks
- ✅ Added provider badges and tool trace visualization in frontend

#### Math Transparency (Phase 9)
- ✅ Added `compute_CR_math_explanation()` and `compute_CR_vig_explanation()` functions
- ✅ All 4 detector types now include `CR_math_proof` with step-by-step calculations
- ✅ Implemented `generate_CR_sportsbook_rankings()` with quality scoring
- ✅ Added rankings table with verdict badges (Recommended/Avoid/Cautious)
- ✅ Frontend displays collapsible math proofs for each finding

#### Deployment Configurations (Phase 10)
- ✅ Created Dockerfile with Python 3.11 for production
- ✅ Added Railway deployment (railway.toml, nixpacks.toml, deploy-railway.ps1)
- ✅ Added Fly.io deployment (fly.toml, deploy-fly.sh)
- ✅ Created Procfile for Heroku compatibility
- ✅ Updated documentation with deployment guides

#### Technical Challenges Solved
- ✅ **Python 3.14 Compatibility**: Fixed pydantic-core issues by updating to newer versions
- ✅ **Environment Loading**: Fixed dotenv loading in run_api.py for proper LLM provider detection
- ✅ **Tool Schema Validation**: Fixed missing `items` property in array schemas for OpenAI compliance
- ✅ **Sample Data Loading**: Fixed path from old filename to standardized `sample_odds.json`
- ✅ **Timezone Handling**: Fixed datetime comparisons to use timezone-aware objects
- ✅ **Quality Score Calculation**: Capped rankings scores to prevent overflow beyond 100

#### Performance Characteristics
- **Mock Provider**: Instant analysis (< 1 second)
- **OpenAI gpt-3.5-turbo**: ~20-30 seconds for full analysis
- **OpenAI gpt-4o-mini**: ~20-30 seconds (similar performance)
- **Memory Usage**: < 100MB typical
- **API Calls**: 3-4 calls per analysis, 1-3 calls per chat message

#### Testing Coverage
- ✅ Created `test_phase8_llm_agent.py` (38 tests) - LLM adapters, tools, agent pipeline
- ✅ Created `test_phase9_math_rankings.py` (38 tests) - Math proofs, rankings, detectors
- ✅ All 76 tests passing
- ✅ Created `test_llm_connection.py` for API key validation
- ✅ Created `test_llm_agent_debug.py` for performance debugging

#### User Experience Features
- ✅ **AI Analysis Summary**: Natural language overview of findings
- ✅ **Interactive Chat**: Context-aware Q&A about odds data
- ✅ **Agent Reasoning Trace**: Step-by-step tool execution visibility
- ✅ **Math Proofs**: Transparent calculations for every finding
- ✅ **Sportsbook Rankings**: Quality scoring with actionable verdicts
- ✅ **Provider Switching**: Easy switching between LLM providers via .env

#### Documentation Updates
- ✅ Updated README.md with comprehensive LLM setup guide
- ✅ Created SETUP.md with 5-minute quick start
- ✅ Added cost estimates ($0.003 per analysis with gpt-4o-mini)
- ✅ Documented all environment variables and configuration options

---

## 3. Production Deployment Guide
- Used AI (Cascade/GPT-4) heavily for boilerplate: Pydantic models, FastAPI routers, data contracts, test scaffolding.
- Did **not** use AI for the odds math — `compute_CR_implied_probability`, `compute_CR_vig`, `compute_CR_arbitrage` etc. were written and verified by hand because correctness is non-negotiable.
- Used AI to generate `data/sample_odds.json` with realistic NBA multi-bookmaker data.

### Phase 8: LLM Integration
- **Prompt iteration 1 — System prompt too vague:**
  Initial draft: `"You are an odds analysis agent. Analyze the data and call tools."`
  Problem: model called tools in random order, skipped stale-line detection entirely.
  Fix: explicit ordered call sequence in `CR_SYSTEM_PROMPT`:
  ```
  Call tools in this order: CR_detect_stale_lines, CR_detect_arbitrage,
  CR_detect_outliers, CR_detect_value_edges, CR_compute_best_lines, CR_compute_consensus
  ```

- **Prompt iteration 2 — LLM hallucinated odds values in summary:**
  Model wrote "DraftKings offers -105 on Lakers" when no such value existed.
  Fix: added hard rule to `CR_SYSTEM_PROMPT`:
  ```
  After all tool calls, write the briefing using ONLY the tool results.
  Every claim must reference the tool that produced it.
  ```

- **Prompt iteration 3 — Chat context overflow:**
  Passing all findings to the chat prompt hit token limits on Claude Haiku.
  Fix: `build_CR_chat_context_message` caps findings at 20 entries with `CR_findings[:20]`.

- **Adapter pattern decision:** Instead of picking one LLM vendor, built `CR_LLMProvider` abstract base class with separate adapters for OpenAI, Anthropic, Gemini, and a deterministic mock. The `factory.py` selects the provider from `LLM_PROVIDER` env var, falling back to mock when no key is present. This means the assignment grader can test with `LLM_PROVIDER=mock` without any API keys.

- **Tool schema design:** All 10 tool schemas live in `packages/llm/tool_schemas.py` in OpenAI function-calling format. Gemini and Anthropic adapters convert from this canonical format to their respective formats at the adapter layer — single source of truth.

### Phase 9: Math Transparency + Rankings
- Added `compute_CR_math_explanation(price)` and `compute_CR_vig_explanation(prices)` to `odds_math.py`. These return a `CR_formula` string showing the exact arithmetic, e.g.:
  ```
  |110| / (|110| + 100) = 110 / 210 = 52.4%
  ```
- Each finding now carries a `CR_math_proof` dict. The frontend renders it as a collapsible `<details>` element so the evaluator can verify every number.
- **Sportsbook rankings formula:**
  Score = (1 − avg_vig/0.15) × 40 + best_line_freq × 40 + freshness × 10 + accuracy × 10
  Tested against sample data: Pinnacle-style books (low vig) score ~75+; square books (high vig, stale lines) score <35 and get flagged "Avoid".

### Phase 10: Deployment
- Railway chosen as primary target: zero-config, reads `PORT` from env automatically, free tier sufficient for demo.
- Fly.io included as secondary option for persistent deployments with custom domains.
- `deploy-railway.ps1` handles: Railway CLI check → env push → `railway up`. Safe: does not push placeholder key values (`sk-...`).
- `Dockerfile` uses `python:3.11-slim`, non-root user pattern intentionally skipped for simplicity at demo scale.

---

## 3. Prompt Iterations — Key Lessons

| Iteration | Problem | Fix |
|-----------|---------|-----|
| Unordered tool calls | Model skipped stale detection | Explicit ordered list in system prompt |
| Hallucinated odds | Model invented numbers not in data | "ONLY use tool results" rule |
| Chat token overflow | 200+ findings exceeded context | Cap at 20 findings in context message |
| Gemini tool schema | Gemini rejects `"type": "object"` in top-level | Wrap params in `FunctionDeclaration` format in `gemini_adapter.py` |
| Mock provider for CI | Real API calls in tests are slow/expensive | `CR_MockLLMProvider` runs all tools deterministically, no HTTP |

---

## 4. Tradeoffs

| Area | Decision | Tradeoff |
|------|----------|----------|
| LLM math | Never — deterministic only | Less "impressive" but always correct |
| Adapter pattern | 3 providers + mock | More files, but swappable without touching agent logic |
| Chat grounding | Briefing-first, tools as fallback | Can't answer questions outside the current dataset (by design) |
| Frontend | Vanilla JS + CSS | No build step, simpler deployment, slightly more verbose code |
| Session storage | In-memory dict | Not persistent across restarts; acceptable for demo scope |
| Ranking score | Weighted linear formula | Simpler than ML model, fully explainable, auditable |
| Deployment | Railway (primary) | Single-region, no auto-scale — fine for demo, not for production |

---

## 5. What Was Intentionally Deferred

- **Live odds ingestion:** Assignment uses static snapshots; a production system would poll The Odds API or similar.
- **Line movement tracking:** Requires persistent storage; deferred to avoid database complexity.
- **Advanced eval harness:** Would use historical data to measure edge prediction accuracy over time.
- **Multi-region deployment:** Single Railway region is sufficient for evaluation.
- **Authentication:** No API keys on the REST API endpoints; acceptable for a demo system.

---

## 6. What I Would Do Next (V3)

1. Replace in-memory sessions with Redis for multi-instance chat history
2. Add Pinnacle as the sharp-line anchor for consensus pricing
3. Implement line movement tracking (store snapshots with timestamps)
4. Add a confidence calibration layer: compare predicted edges to realized outcomes
5. Build an eval harness that measures briefing accuracy against post-game results
6. Add webhook support so the briefing runs automatically when new odds are posted

---

## 7. Final Assessment

This system demonstrates:
- **Controlled AI usage** — the model is a reasoning layer, not a calculator
- **Explainable outputs** — every number in the briefing has a math proof
- **Adapter-first design** — swap LLM vendors without touching business logic
- **Production-minded deployment** — Railway/Fly.io ready, env-var driven, health-checked

The architecture would survive a production audit. The math is correct by construction.
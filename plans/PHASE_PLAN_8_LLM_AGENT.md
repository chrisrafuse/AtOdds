# PHASE_PLAN_8_LLM_AGENT.md
## Author: Chris Rafuse
## Phase: 8 — LLM Integration, Chat UI, Agent Reasoning Trace
## Entry Criteria: Phase 7 complete (frontend operational at localhost:8000)
## Exit Criteria: Real LLM drives agent, chat UI in frontend, tool trace visible

---

# 🎯 PHASE OBJECTIVES

Replace the deterministic-only orchestrator with a real LLM-powered agent:
- Add multi-provider LLM adapter (OpenAI / Claude / Gemini) behind a clean interface
- Wire LLM function calling to the existing `CR_TOOL_REGISTRY`
- Add env-var-based API key config (no hardcoding)
- Add chat UI panel to `index.html` with message history
- Surface tool call trace in the UI so the reviewer sees the agent's reasoning

This phase does NOT rewrite the deterministic engine. It plugs the LLM in front of it.

---

# 📁 FILES TO CREATE OR MODIFY

## New Files

### `packages/llm/__init__.py`
Empty init.

### `packages/llm/base.py`
Abstract base class `CR_LLMProvider`:
```python
class CR_LLMProvider(ABC):
    @abstractmethod
    def chat_with_tools(self, messages, tools) -> CR_LLMResponse: ...
    @abstractmethod
    def get_provider_name(self) -> str: ...
```
`CR_LLMResponse` dataclass:
```python
@dataclass
class CR_LLMResponse:
    CR_content: str
    CR_tool_calls: List[CR_ToolCall]   # list of tool calls made
    CR_finish_reason: str               # "stop" | "tool_calls"
    CR_usage: Dict[str, int]            # prompt/completion tokens
```
`CR_ToolCall` dataclass:
```python
@dataclass
class CR_ToolCall:
    CR_tool_name: str
    CR_arguments: Dict[str, Any]
    CR_result: Any         # populated after execution
    CR_error: Optional[str]
```

### `packages/llm/openai_adapter.py`
Adapter for OpenAI (gpt-4o-mini default):
- Reads `OPENAI_API_KEY` from env
- Converts `CR_TOOL_REGISTRY` schemas → OpenAI function definitions
- Runs the tool-calling loop: sends message → receives tool_calls → executes tools → sends results back → repeat until `stop`
- Returns `CR_LLMResponse`

### `packages/llm/anthropic_adapter.py`
Adapter for Anthropic Claude (claude-3-5-haiku default):
- Reads `ANTHROPIC_API_KEY` from env
- Converts `CR_TOOL_REGISTRY` schemas → Anthropic tool_use format
- Same tool-calling loop as OpenAI adapter

### `packages/llm/gemini_adapter.py`
Adapter for Google Gemini (gemini-1.5-flash default):
- Reads `GEMINI_API_KEY` from env
- Converts `CR_TOOL_REGISTRY` schemas → Gemini function declarations
- Same tool-calling loop pattern

### `packages/llm/factory.py`
```python
def get_CR_llm_provider(CR_provider: str = None) -> CR_LLMProvider:
    """
    Returns the configured provider from env.
    CR_provider overrides env var if passed.
    Env: LLM_PROVIDER = "openai" | "anthropic" | "gemini"
    Falls back to mock provider if no API key present (for tests).
    """
```

### `packages/llm/mock_provider.py`
Deterministic mock that returns canned responses — used in tests and when no API key is configured. Allows the full pipeline to run without a live LLM key.

### `packages/llm/tool_schemas.py`
Converts `CR_TOOL_REGISTRY` into the OpenAI-style JSON schema format that all adapters accept. Central place so schemas are defined once:
```python
CR_TOOL_SCHEMAS = [
    {
        "name": "CR_detect_arbitrage",
        "description": "Detect arbitrage opportunities across bookmakers",
        "parameters": { "type": "object", "properties": { "CR_snapshot": {...} }, "required": ["CR_snapshot"] }
    },
    # ... one entry per tool in CR_TOOL_REGISTRY
]
```

## Modify Existing Files

### `packages/agent/agent.py`
**Current:** Pure Python loop calling tools directly.  
**Change:** Add `run_CR_llm_agent(CR_snapshot, CR_provider=None)` function alongside the existing `run_CR_agent`. Do NOT remove `run_CR_agent` — it stays as the fallback.

New function:
1. Build initial `messages` list from `CR_SYSTEM_PROMPT` + user message describing the snapshot
2. Call `provider.chat_with_tools(messages, CR_TOOL_SCHEMAS)`
3. Execute each `CR_tool_call` via `CR_TOOL_REGISTRY`
4. Append tool results to messages, loop until `finish_reason == "stop"`
5. Return `CR_LLMAgentResult`:
```python
@dataclass
class CR_LLMAgentResult:
    CR_findings: List[Dict]
    CR_tool_trace: List[CR_ToolCall]   # every tool call with args + result
    CR_llm_summary: str                # final LLM explanation text
    CR_provider: str
    CR_model: str
```

### `packages/agent/prompts.py`
**Current:** Placeholder prompt that says "ONLY NEEDED IF you integrate LLM".  
**Change:** Replace with production system prompt:
```
You are an odds intelligence agent for Betstamp. You analyze sportsbook odds data
using deterministic tools. You must call tools for ALL calculations — never do
math yourself. After gathering findings, produce a structured briefing section
by section. When answering follow-up questions, retrieve only what tools return.
If a question is outside the data scope, say so explicitly.
```
Add `CR_BRIEFING_PROMPT` and `CR_CHAT_PROMPT` variants.

### `packages/chat/chat_cr.py`
**Current:** Keyword `if/elif` pattern matching.  
**Change:** Add `CR_LLMOddsChat` class that:
- Holds the briefing artifact and findings in context
- On `answer_CR_question(question)`, calls LLM with the briefing + question
- LLM is allowed to call `CR_detect_*` drilldown tools for follow-up detail
- Returns grounded answer with tool trace
Keep `CR_OddsChat` (keyword-based) as fallback when no API key.

### `apps/web/api/routers/analysis.py`
**Change:** `execute_CR_analysis_pipeline` result should now include `CR_tool_trace` and `CR_llm_summary` when LLM is available. Fall back to deterministic pipeline if no provider configured.

### `apps/web/api/routers/chat.py`
**Change:** `ask_question` endpoint should use `CR_LLMOddsChat` when provider available, return `CR_tool_trace` in response alongside `CR_answer`.

### `apps/web/api/config.py`
**Change:** Add LLM config fields:
```python
LLM_PROVIDER: str = "openai"    # openai | anthropic | gemini | mock
OPENAI_API_KEY: str = ""
ANTHROPIC_API_KEY: str = ""
GEMINI_API_KEY: str = ""
OPENAI_MODEL: str = "gpt-4o-mini"
ANTHROPIC_MODEL: str = "claude-3-5-haiku-20241022"
GEMINI_MODEL: str = "gemini-1.5-flash"
```

### `.env.example`
Create or update:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...
```

### `requirements-web.txt`
Add:
```
openai>=1.0.0
anthropic>=0.30.0
google-generativeai>=0.7.0
python-dotenv>=1.0.0
```

## Frontend Changes

### `apps/web/static/index.html`
Add a **Chat Panel** section below the Results section:
```html
<section id="chatSection" class="chat-section hidden">
  <div class="chat-header">
    <h3>Ask the Agent</h3>
    <span id="chatProviderBadge" class="provider-badge"></span>
  </div>
  <div id="chatMessages" class="chat-messages"></div>
  <div class="chat-input-row">
    <input type="text" id="chatInput" placeholder="Why did you flag that game?..." />
    <button id="chatSendBtn" class="btn btn-primary">Ask</button>
  </div>
  <div class="quick-questions">
    <button class="quick-q">Which books have the most stale lines?</button>
    <button class="quick-q">Explain the arbitrage you found</button>
    <button class="quick-q">Which books should I avoid tonight?</button>
  </div>
</section>
```

Add a **Reasoning Trace** collapsible panel per analysis result:
```html
<details class="trace-panel">
  <summary>Agent Reasoning Trace (N tool calls)</summary>
  <div id="toolTrace" class="tool-trace"></div>
</details>
```

### `apps/web/static/app.js`
Add:
- `initChatSession(findings, snapshot)` — calls `POST /api/v1/chat/session`, stores session ID
- `sendChatMessage(question)` — calls `POST /api/v1/chat/ask`, appends message to UI
- `renderChatMessage(role, content, toolTrace)` — renders user/agent messages
- `renderToolTrace(toolCalls)` — renders collapsible trace cards
- `showChatSection()` — unhides chat panel after analysis completes
- Quick question button handlers

### `apps/web/static/styles.css`
Add styles for:
- `.chat-section`, `.chat-messages`, `.chat-input-row`
- `.chat-bubble-user`, `.chat-bubble-agent`
- `.quick-questions`, `.quick-q`
- `.tool-trace`, `.trace-card`, `.trace-tool-name`, `.trace-args`, `.trace-result`
- `.provider-badge` (colored pill showing "OpenAI" / "Claude" / "Gemini" / "Mock")

---

# 🔌 TOOL SCHEMA DESIGN

Each tool in `CR_TOOL_REGISTRY` needs a JSON schema entry in `tool_schemas.py`. The LLM will select and call these tools autonomously.

Tools to expose to LLM:
| Tool Name | Description |
|---|---|
| `CR_detect_arbitrage` | Find cross-book guaranteed profit |
| `CR_detect_stale_lines` | Find lines not updated recently |
| `CR_detect_outliers` | Find statistically unusual odds |
| `CR_detect_value_edges` | Find odds better than consensus |
| `CR_compute_best_lines` | Get best price per outcome per book |
| `CR_compute_consensus` | Get consensus price across books |
| `CR_compute_vig` | Calculate bookmaker margin |
| `CR_compute_implied_probability` | Convert odds to probability |

---

# 🔄 AGENT FLOW (LLM MODE)

```
User triggers "Run Analysis"
  → API sends CR_snapshot to /api/v1/analyze
  → execute_CR_analysis_pipeline checks LLM_PROVIDER
  → if provider: run_CR_llm_agent(snapshot, provider)
    → LLM receives system prompt + "analyze this snapshot"
    → LLM calls CR_detect_stale_lines → result appended
    → LLM calls CR_detect_arbitrage → result appended
    → LLM calls CR_detect_outliers → result appended
    → LLM calls CR_detect_value_edges → result appended
    → LLM calls CR_compute_best_lines → result appended
    → LLM produces final structured briefing text
    → Returns CR_LLMAgentResult (findings + tool_trace + summary)
  → else: run_CR_agent(snapshot) [deterministic fallback]
  → Response includes CR_tool_trace for UI rendering

User sees results + collapsible "Agent Reasoning Trace"
  → Each trace card shows: tool name, args used, result summary

User types chat question
  → POST /api/v1/chat/ask
  → CR_LLMOddsChat passes briefing + question to LLM
  → LLM may call drilldown tools (e.g. re-run detect_outliers for specific event)
  → Returns grounded answer + tool trace
  → Chat bubble rendered with optional trace details
```

---

# ⚙️ CONFIGURATION DESIGN

Priority order for API key resolution:
1. Environment variable (e.g. `OPENAI_API_KEY`)
2. `.env` file loaded by `python-dotenv`
3. Falls back to `mock` provider (no error thrown)

This means:
- Zero-config local dev: mock provider runs automatically
- Production: set `LLM_PROVIDER` + key in env
- The frontend shows provider badge so reviewer knows which provider is active

---

# 📋 TASK CHECKLIST

## Backend
- [ ] Create `packages/llm/` package with `__init__.py`
- [ ] Implement `packages/llm/base.py` — `CR_LLMProvider`, `CR_LLMResponse`, `CR_ToolCall`
- [ ] Implement `packages/llm/tool_schemas.py` — JSON schemas for all 8 tools
- [ ] Implement `packages/llm/openai_adapter.py`
- [ ] Implement `packages/llm/anthropic_adapter.py`
- [ ] Implement `packages/llm/gemini_adapter.py`
- [ ] Implement `packages/llm/mock_provider.py`
- [ ] Implement `packages/llm/factory.py` — provider selection from env
- [ ] Add `run_CR_llm_agent()` to `packages/agent/agent.py`
- [ ] Rewrite `packages/agent/prompts.py` with production prompts
- [ ] Add `CR_LLMOddsChat` to `packages/chat/chat_cr.py`
- [ ] Update `apps/web/api/config.py` with LLM fields
- [ ] Update `apps/web/api/routers/analysis.py` to use LLM agent when available
- [ ] Update `apps/web/api/routers/chat.py` to use `CR_LLMOddsChat` when available
- [ ] Create `.env.example`
- [ ] Update `requirements-web.txt`

## Frontend
- [ ] Add Chat Panel HTML to `index.html`
- [ ] Add Reasoning Trace collapsible to results section
- [ ] Add provider badge display
- [ ] Implement chat session init + message send in `app.js`
- [ ] Implement tool trace renderer in `app.js`
- [ ] Add chat + trace styles to `styles.css`

## Tests
- [ ] Add `tests/test_llm_adapters.py` — mock provider integration test
- [ ] Verify full pipeline runs with mock provider (no API key needed)
- [ ] Verify `CR_tool_trace` returned in analysis response

---

# ✅ EXIT CRITERIA

- `LLM_PROVIDER=openai` + valid key → LLM calls tools, returns grounded briefing
- `LLM_PROVIDER=mock` (or no key) → deterministic fallback, still returns `CR_tool_trace`
- Chat panel visible in UI after analysis
- Tool trace visible and shows which tools were called
- Provider badge shows "OpenAI" / "Claude" / "Gemini" / "Mock"
- All existing tests still pass

---

**Phase 8 Status**: Ready to implement
**Dependencies**: Phase 7 complete
**Next Phase**: Phase 9 — Math transparency + sportsbook rankings

# ARCHITECTURE.md
## Betstamp Odds Intelligence Agent
Version: 1.0

# 0. ARCHITECTURE GOAL
Separate deterministic truth generation from model-driven orchestration and explanation.

# 1. HIGH-LEVEL DESIGN

[Input Snapshot]
    ->
[Normalization + Validation]
    ->
[Deterministic Analytics Engine]
    ->
[Tool Registry]
    ->
[Agent Orchestrator]
    ->
[Structured Briefing Artifact]
    ->
[Renderer / UI]
    ->
[Grounded Chat]

Supporting planes:
- Trace / Observability
- Config / Schema Registry
- Replay / Eval Harness

# 2. LAYERS

## 2.1 Data Layer
Responsibilities:
- ingest raw snapshot
- normalize records
- validate schema
- construct canonical market structures

Artifacts:
- normalized_snapshot.json
- event index
- book index

## 2.2 Core Analytics Layer
Responsibilities:
- implied probability
- vig
- no-vig
- best line
- consensus
- stale detection
- outlier detection
- arbitrage
- value edge detection
- sportsbook ranking

Properties:
- deterministic
- pure where possible
- independently testable
- zero LLM dependency

## 2.3 Tool Layer
Responsibilities:
- expose analytics functions as typed callable tools
- enforce input / output schema
- provide drilldown access for agent and UI

Properties:
- stable interface boundary
- JSON-only contracts
- auditable calls

## 2.4 Agent Layer
Responsibilities:
- plan tool usage
- gather evidence
- compose structured briefing
- answer grounded follow-up questions

Properties:
- no hidden business logic
- no arithmetic authority
- provider-agnostic

## 2.5 Artifact Layer
Responsibilities:
- persist run bundles
- store findings
- store briefing object
- store trace events
- support replay

## 2.6 UI Layer
Responsibilities:
- start runs
- display briefing
- inspect findings
- show trace and evidence
- handle follow-up Q&A

# 3. EXECUTION FLOWS

## 3.1 Daily Briefing Flow
1. load input snapshot
2. normalize and validate
3. compute analytics
4. generate findings
5. expose findings via tools
6. agent assembles structured briefing
7. validate briefing schema
8. persist artifacts
9. render report

## 3.2 Follow-up Q&A Flow
1. user asks question
2. scope classifier checks if answerable
3. retrieve relevant briefing sections
4. call drilldown tools if needed
5. answer using evidence-backed data
6. persist trace + answer artifact

# 4. DATA MODEL

## 4.1 Canonical Entities
- Event
- SportsbookRecord
- Market
- Outcome
- Finding
- BriefingSection
- EvidenceReference
- RunManifest

## 4.2 Key IDs
- run_id
- event_id
- market_id
- sportsbook_id
- finding_id
- evidence_id

# 5. DETECTOR ARCHITECTURE
Each detector must expose:
- detector_id
- input contract
- output contract
- thresholds
- severity rules
- explanation payload

Detectors:
- stale_line_detector
- outlier_detector
- arb_detector
- integrity_detector
- value_detector

# 6. PROVIDER ABSTRACTION
The LLM layer must be isolated behind an adapter.

Interface:
- generate_structured()
- run_with_tools()
- validate_capabilities()
- get_provider_metadata()

Possible adapters:
- OpenAI adapter
- Anthropic adapter
- local model adapter

# 7. REPLAY ARCHITECTURE
Replay bundle contains:
- normalized input
- analytics outputs
- briefing object
- trace object
- config manifest
- model metadata

Purpose:
- reproducibility
- debugging
- regression checking
- model swap verification

# 8. OBSERVABILITY
Capture:
- run started / completed
- tool call graph
- tool timing
- agent decision summary
- schema validation errors
- token / latency metrics
- replay identifiers

# 9. BUILD SYSTEM SHAPE
Recommended monorepo:

/apps
  /api
  /web
/packages
  /data
  /core-engine
  /tools
  /agent
  /reporting
  /chat
  /schemas
  /observability
/spec
/tests

# 10. TECHNICAL PRINCIPLES
- truth lives in deterministic engine
- agent narrates, does not arbitrate truth
- artifacts are the source of conversational grounding
- schemas define system contracts
- every important output must be replayable
- model vendor is an implementation detail, not the core architecture
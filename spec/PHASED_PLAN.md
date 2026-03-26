# PHASED_PLAN.md
## Betstamp Odds Intelligence Agent
Version: 1.0

# PHASE 0 — SPEC + CONTRACT LOCK
Goal:
- define what is being built and the rules of the system

Create:
- SPEC.md
- ARCHITECTURE.md
- AGENT.md
- DATA_CONTRACTS.md
- TOOL_REGISTRY.md
- BRIEFING_SCHEMA.json
- FINDING_SCHEMA.json
- CONFIG_SCHEMA.json
- EVAL_CRITERIA.md

Exit Criteria:
- all major outputs and interfaces defined
- no ambiguity about deterministic vs agent responsibilities

# PHASE 1 — REPO + BUILD SYSTEM
Goal:
- create a maintainable monorepo and execution shell

Create:
- monorepo root
- package manager config
- workspace config
- lint / format config
- test runner config
- environment config template
- CI pipeline skeleton
- Dockerfile / optional compose
- README.md

Assets:
- /apps/api
- /apps/web
- /packages/data
- /packages/core-engine
- /packages/tools
- /packages/agent
- /packages/reporting
- /packages/chat
- /packages/schemas
- /packages/observability
- /tests

Exit Criteria:
- project installs, tests boot, builds boot

# PHASE 2 — DATA INGESTION + NORMALIZATION
Goal:
- convert raw odds file into canonical internal representation

Build:
- dataset loader
- normalization pipeline
- schema validation
- timestamp normalization
- canonical IDs
- event/market/outcome grouping

Create:
- normalized_snapshot.json
- data validators
- sample fixture set
- ingestion tests

Exit Criteria:
- dataset loads and validates consistently
- canonical structures available for engine use

# PHASE 3 — DETERMINISTIC ANALYTICS ENGINE
Goal:
- build the truth engine

Build:
- implied probability calculator
- vig calculator
- no-vig normalizer
- best line engine
- consensus engine
- stale detector
- outlier detector
- arbitrage detector
- integrity checker
- value detector
- sportsbook ranking engine

Create:
- engine modules
- engine test vectors
- analytics_results.json
- findings.json

Exit Criteria:
- math is correct
- seeded anomaly classes can be surfaced
- engine is independent of LLM

# PHASE 4 — TOOL REGISTRY
Goal:
- expose deterministic functions as typed tools

Build:
- tool wrapper layer
- tool input/output validation
- tool registry manifest
- error handling and serialization
- drilldown tool support

Create:
- tool definitions
- TOOL_REGISTRY.md
- tool contract tests

Exit Criteria:
- agent can query analytics strictly through tools
- tools are stable and replayable

# PHASE 5 — BRIEFING GENERATION
Goal:
- produce the core artifact reviewers will inspect

Build:
- briefing composer
- section ordering
- evidence references
- severity tags
- limitations section
- schema validator

Create:
- briefing.json
- markdown/html renderer
- briefing snapshot tests

Exit Criteria:
- one command produces a complete structured briefing
- briefing is readable and evidence-backed

# PHASE 6 — AGENT ORCHESTRATION
Goal:
- connect model to tools and briefing production

Build:
- provider adapter
- system prompt
- tool-calling loop
- schema-enforced output generation
- fallback / retry policy
- safe scope checking

Create:
- agent runtime
- agent config profile
- prompt assets
- agent eval fixtures

Exit Criteria:
- model uses tools, not raw reasoning, for core analysis
- outputs conform to schemas

# PHASE 7 — GROUNDED CHAT
Goal:
- answer follow-up questions based on generated artifacts

Build:
- question scope checker
- artifact retrieval layer
- drilldown tool flow
- grounded answer formatter
- refusal path for unsupported questions

Create:
- chat handler
- answer schema
- chat eval dataset

Exit Criteria:
- follow-up answers remain grounded and bounded
- unsupported questions do not hallucinate

# PHASE 8 — OBSERVABILITY + REPLAY
Goal:
- make runs inspectable and repeatable

Build:
- trace collector
- tool call log
- run manifest
- replay runner
- result comparison runner
- latency/token metrics

Create:
- trace.json
- config_manifest.json
- replay scripts
- replay snapshots

Exit Criteria:
- same input/config can be replayed
- trace of tool usage is visible

# PHASE 9 — EVALS + VALIDATION
Goal:
- prove reliability and block regressions

Build:
- deterministic math tests
- anomaly regression tests
- schema validation tests
- groundedness evals
- refusal correctness evals
- tool-usage evals

Create:
- golden datasets
- eval runner
- release gate checklist
- EVAL_REPORT.md

Exit Criteria:
- core tests pass
- system behavior is measurable
- changes can be judged objectively

# PHASE 10 — UI + REVIEWER EXPERIENCE
Goal:
- make the system easy to inspect during review

Build:
- generate briefing screen
- report viewer
- findings drilldown
- chat panel
- trace panel
- run history

Create:
- minimal frontend
- reviewer walkthrough notes
- seed dataset loader path

Exit Criteria:
- reviewer can generate, inspect, and ask questions easily

# PHASE 11 — SUBMISSION PACKAGE
Goal:
- package the system as a strong take-home and future platform seed

Create:
- deployed app URL
- GitHub repo
- README.md
- DEVLOG.md
- ARCHITECTURE.md
- SPEC.md
- AGENT.md
- setup instructions
- demo notes
- known limitations
- future roadmap

Exit Criteria:
- repo is understandable
- app runs
- documents explain engineering decisions clearly

# PHASE 12 — POST-ASSIGNMENT PRODUCTIZATION
Goal:
- evolve into reusable odds intelligence platform

Next Builds:
- live odds feed adapters
- historical movement tracking
- drift detection
- model swap benchmarks
- alerting layer
- compliance logging
- user profiles / saved runs
- strategy-specific ranking profiles
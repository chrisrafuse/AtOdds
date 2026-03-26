# SPEC.md
## Betstamp Odds Intelligence Agent
Version: 1.0
Status: Build Spec
Purpose: Build a deterministic, tool-driven AI odds agent that analyzes sportsbook odds data, produces a daily briefing, and supports grounded follow-up Q&A.

# 0. OBJECTIVE
Build an AI-powered odds analysis system that:
1. Ingests odds snapshots
2. Computes correct betting math deterministically
3. Detects anomalies and opportunities
4. Produces a structured daily market briefing
5. Supports follow-up Q&A grounded in prior generated artifacts

# 1. PRIMARY DELIVERABLES
1. Working application
2. Daily Odds Briefing artifact
3. Grounded chat over briefing
4. Tool-based agent orchestration
5. DEVLOG / implementation notes
6. Clean architecture and tests

# 2. NON-NEGOTIABLE RULES
- Raw odds dataset must not be dumped wholesale into the model prompt for analysis
- Odds math must be performed by deterministic code, not freeform model reasoning
- Agent must use tools/functions for retrieval and computation
- Outputs must be explainable, repeatable, and evidence-backed
- Follow-up answers must stay grounded in artifacts and tool outputs
- Unknowns must be stated explicitly

# 3. INPUTS
- Sample odds dataset
- Event metadata
- Sportsbook metadata
- User chat questions
- Config thresholds

# 4. CORE OUTPUTS
## 4.1 Daily Briefing
Must contain:
- Market overview
- Anomalies
- Value opportunities
- Arbitrage opportunities
- Sportsbook quality ranking
- Limitations / uncertainty notes

## 4.2 Follow-up Answers
Must:
- Reference prior findings
- Retrieve evidence on demand
- Refuse unsupported claims

## 4.3 Run Artifacts
Per run:
- normalized_snapshot.json
- analytics_results.json
- findings.json
- briefing.json
- trace.json
- config_manifest.json

# 5. DOMAIN REQUIREMENTS
## 5.1 Supported Market Types
- Moneyline
- Spread
- Total

## 5.2 Deterministic Calculations
- American odds to implied probability
- Overround / vig
- No-vig normalization
- Best line detection
- Consensus pricing
- Cross-book arbitrage detection

# 6. DETECTION REQUIREMENTS
## 6.1 Stale Line Detection
Flag records whose update timestamps are materially older than peer books within the same event/market context.

## 6.2 Outlier Detection
Flag prices that materially deviate from market consensus or chosen sharp-book reference.

## 6.3 Arbitrage Detection
Detect combinations of best available prices where summed implied probabilities are below 1.0.

## 6.4 Integrity Checks
Detect:
- missing outcomes
- malformed market structure
- implausible odds
- inconsistent spread / total symmetry

## 6.5 Value Detection
Compare offered prices against no-vig consensus fair price proxy and flag positive edge situations.

# 7. SPORTSBOOK RANKING REQUIREMENTS
Rank books using weighted metrics:
- average vig
- stale rate
- outlier frequency
- integrity issues
- competitiveness of best lines

# 8. AGENT REQUIREMENTS
## 8.1 Model Role
Allowed:
- choose tools
- sequence retrieval / analysis calls
- summarize results
- produce structured report
- answer follow-up questions from evidence

Forbidden:
- invent calculations
- skip tools for core analysis
- answer beyond available evidence

## 8.2 Output Contract
Agent output must be schema-driven and machine-validated before render.

# 9. TOOL REQUIREMENTS
Minimum tools:
- load_snapshot
- list_events
- get_event_markets
- compute_implied_probabilities
- compute_vig
- compute_no_vig
- compute_consensus
- detect_stale_lines
- detect_outliers
- detect_arbitrage
- detect_value_edges
- rank_sportsbooks
- get_finding_details
- answer_scope_check

All tools:
- typed
- deterministic
- side-effect free for analysis paths
- JSON in / JSON out

# 10. UI REQUIREMENTS
Views:
- Generate Briefing
- Briefing Reader
- Findings Drilldown
- Chat Panel
- Trace Panel
- Run History

UI priority:
- correctness
- transparency
- analyst usability
- not visual flourish

# 11. TESTING REQUIREMENTS
## 11.1 Deterministic Unit Tests
- implied probability
- vig
- no-vig normalization
- arbitrage math
- ranking math

## 11.2 Dataset Regression
Must detect seeded:
- stale lines
- outliers
- arbitrage candidate(s)

## 11.3 Agent Evals
- schema compliance
- tool usage correctness
- groundedness
- refusal correctness
- answer completeness

# 12. REPRODUCIBILITY REQUIREMENTS
- fixed config manifest
- canonical sorting
- low-temperature generation
- seeded generation where supported
- replayable runs from stored artifacts

# 13. OBSERVABILITY REQUIREMENTS
Track:
- tool calls
- prompt / response metadata
- latency
- token usage
- error rate
- eval scores
- run lineage

# 14. BUILD REQUIREMENTS
- modular package structure
- separable analytics core
- provider-agnostic agent layer
- deployable backend + lightweight frontend
- CI for tests and schema validation

# 15. FUTURE-PROOFING
- easy model swap
- pluggable tool registry
- configurable detector thresholds
- live odds adapters later
- historical baseline / drift detection later
- compliance / governed AI posture compatible

# 16. SUCCESS DEFINITION
The system is successful if it:
- computes odds math correctly
- surfaces the seeded anomaly classes
- produces a useful daily briefing
- answers follow-up questions from evidence
- demonstrates senior-level AI systems engineering judgment
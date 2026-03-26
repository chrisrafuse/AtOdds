# PHASE_PLAN_9_MATH_AND_RANKINGS.md
## Author: Chris Rafuse
## Phase: 9 — Math Transparency + Sportsbook Quality Rankings
## Entry Criteria: Phase 8 complete (LLM agent operational)
## Exit Criteria: Briefing shows explicit math steps; sportsbook rankings table in briefing + UI

---

# 🎯 PHASE OBJECTIVES

The assignment explicitly says: *"Perform real calculations — implied probability, vig, best available line — and show its math"*. Currently the calculations happen but the output does not expose the work. This phase makes every finding **self-explanatory** with inline math proof.

Two discrete goals:
1. **Math transparency** — every finding in the briefing shows the numbers behind the conclusion
2. **Sportsbook quality rankings** — a ranked table of all bookmakers by vig, staleness, outlier count, and best-line frequency

---

# 📁 FILES TO CREATE OR MODIFY

## Modify Existing Files

### `packages/core_engine/odds_math.py`
Add `compute_CR_math_explanation(CR_price: int) -> Dict` that returns a structured math breakdown:
```python
{
    "CR_price": -150,
    "CR_implied_prob": 0.6,
    "CR_formula": "|−150| / (|−150| + 100) = 150/250",
    "CR_result_pct": "60.0%"
}
```
And `compute_CR_vig_explanation(CR_prices: List[int]) -> Dict`:
```python
{
    "CR_prices": [-110, -110],
    "CR_implied_probs": [0.5238, 0.5238],
    "CR_sum": 1.0476,
    "CR_vig": 0.0476,
    "CR_formula": "52.38% + 52.38% = 104.76% → vig = 4.76%"
}
```

### `packages/core_engine/detectors.py`
**Change:** Each finding dict must include a `CR_math_proof` field. Add it to every return value:

- `detect_CR_arbitrage` findings: add
```python
"CR_math_proof": {
    "CR_implied_probs": {"DraftKings": {"home": 0.476}, "FanDuel": {"away": 0.476}},
    "CR_sum": 0.952,
    "CR_profit_margin": 0.048,
    "CR_formula": "1 − (0.476 + 0.476) = 4.8% guaranteed margin"
}
```
- `detect_CR_outlier` findings: add
```python
"CR_math_proof": {
    "CR_market_odds": [-110, -108, -115, -200, -112],
    "CR_mean": -109.0,
    "CR_std_dev": 34.2,
    "CR_z_score": 2.66,
    "CR_formula": "(−200 − (−109.0)) / 34.2 = 2.66σ deviation"
}
```
- `detect_CR_value_edge` findings: add
```python
"CR_math_proof": {
    "CR_book_price": -105,
    "CR_book_implied": 0.5122,
    "CR_consensus_price": -118,
    "CR_consensus_implied": 0.5413,
    "CR_edge": 0.0291,
    "CR_formula": "consensus 54.1% − book 51.2% = 2.9% edge"
}
```
- `detect_CR_stale_line` findings: add
```python
"CR_math_proof": {
    "CR_last_updated": "2024-01-15T08:00:00Z",
    "CR_current_time": "2024-01-15T17:30:00Z",
    "CR_hours_stale": 9.5,
    "CR_threshold_hours": 24,
    "CR_formula": "17:30 − 08:00 = 9.5h (below 24h threshold, but oldest in dataset)"
}
```

### `packages/reporting/briefing.py`
**Change:** In `generate_CR_briefing()`, when rendering each finding, call new helper `format_CR_math_proof(CR_finding)` that outputs the math proof inline:

```
1. 🟢 ARBITRAGE
   Event: NBA_2024_LAL_BOS
   Market: moneyline
   Bookmakers: DraftKings, FanDuel
   Confidence: 95.0%
   Math: DraftKings home -105 → 51.2%, FanDuel away -108 → 51.9%
         51.2% + 51.9% = 103.1% total → vig = 3.1%
         Cross-book sum: 51.2% + 48.1% = 99.3% → 0.7% guaranteed margin
```

Also add a new `generate_CR_sportsbook_rankings(CR_snapshot, CR_findings)` function:
```python
def generate_CR_sportsbook_rankings(
    CR_snapshot: Dict[str, Any],
    CR_findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Ranks each bookmaker by:
    - CR_avg_vig: average margin across all their markets
    - CR_best_line_count: how many times they had the best price
    - CR_stale_count: how many stale lines flagged
    - CR_outlier_count: how many outlier prices flagged
    - CR_quality_score: composite 0-100 (lower vig = better, more best lines = better)
    Returns list sorted by CR_quality_score desc.
    """
```

Score formula:
```
quality_score = (
    (1 - avg_vig) * 40          # lower vig = higher score (40 pts max)
    + (best_line_count / total_markets) * 40   # best line frequency (40 pts max)
    + (1 - stale_count / total_markets) * 10   # freshness (10 pts max)
    + (1 - outlier_count / total_markets) * 10 # accuracy (10 pts max)
)
```

### `packages/agent/agent.py`
**Change:** `execute_CR_analysis_pipeline` now calls `generate_CR_sportsbook_rankings` and includes the result in the returned dict:
```python
return {
    'CR_snapshot_analysis': ...,
    'CR_findings': ...,
    'CR_findings_summary': ...,
    'CR_sportsbook_rankings': CR_sportsbook_rankings,   # NEW
    'CR_pipeline_timestamp': ...
}
```

### `packages/agent/prompts.py`
**Change:** Add sportsbook rankings context to the system prompt so the LLM knows to include them in the briefing section:
```
After analyzing findings, produce the briefing in this order:
1. Market Overview (events, books, total markets)
2. Flagged Anomalies (stale lines, outliers) with math proof
3. Top Value Opportunities (value edges, arbitrage) with math proof
4. Sportsbook Quality Rankings (table ranked by quality score)
5. Recommendations
```

### `packages/chat/chat_cr.py`
**Change:** Add handling for sportsbook ranking questions:
- `"which books should I avoid"` → look up sportsbook rankings, return bottom 2-3 books with reasons
- `"explain the math"` + any finding type → return the `CR_math_proof` from that finding
- `"why did you flag"` + event name → search findings for that event, return finding detail + math proof

### `apps/web/api/routers/report.py`
**Change:** `generate_briefing` endpoint response should include `CR_sportsbook_rankings` alongside the text briefing.

## New Files

### `packages/reporting/rankings.py`
Extract `generate_CR_sportsbook_rankings` into its own module for clarity. Imports `compute_CR_vig` and `compute_CR_best_lines` from the core engine. Returns:
```python
[
    {
        "CR_bookmaker": "DraftKings",
        "CR_avg_vig": 0.042,
        "CR_best_line_count": 18,
        "CR_stale_count": 0,
        "CR_outlier_count": 1,
        "CR_quality_score": 82.4,
        "CR_rank": 1,
        "CR_verdict": "Recommended",    # Recommended / Average / Avoid
        "CR_avg_vig_pct": "4.2%",
        "CR_best_line_pct": "60.0%"
    },
    ...
]
```

## Frontend Changes

### `apps/web/static/index.html`
Add **Sportsbook Rankings** table inside the results section:
```html
<div id="rankingsSection" class="rankings-section hidden">
    <h3>📊 Sportsbook Quality Rankings</h3>
    <table id="rankingsTable" class="rankings-table">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Sportsbook</th>
                <th>Avg Vig</th>
                <th>Best Lines</th>
                <th>Stale Lines</th>
                <th>Outliers</th>
                <th>Score</th>
                <th>Verdict</th>
            </tr>
        </thead>
        <tbody id="rankingsBody"></tbody>
    </table>
</div>
```

Add **math proof** collapsible inside each finding card:
```html
<details class="math-proof">
    <summary>Show math</summary>
    <code class="math-formula"></code>
</details>
```

### `apps/web/static/app.js`
Add:
- `renderSportsbookRankings(rankings)` — populates `#rankingsBody`, color-codes verdict
- `renderMathProof(finding)` — populates `.math-formula` for each finding card
- Update `renderResults(data)` to call both new renderers

### `apps/web/static/styles.css`
Add:
- `.rankings-table` — clean bordered table with hover rows
- `.verdict-recommended` — green badge
- `.verdict-average` — yellow badge
- `.verdict-avoid` — red badge
- `.math-proof` — monospace code block style, collapsible
- `.math-formula` — light gray background, pre-formatted

---

# 📋 TASK CHECKLIST

## Core Engine
- [ ] Add `compute_CR_math_explanation()` to `packages/core_engine/odds_math.py`
- [ ] Add `compute_CR_vig_explanation()` to `packages/core_engine/odds_math.py`
- [ ] Add `CR_math_proof` field to all findings in `packages/core_engine/detectors.py`

## Reporting
- [ ] Create `packages/reporting/rankings.py` with `generate_CR_sportsbook_rankings()`
- [ ] Update `packages/reporting/briefing.py` to render math proof per finding
- [ ] Add sportsbook rankings section to `generate_CR_briefing()`

## Agent
- [ ] Update `execute_CR_analysis_pipeline()` in `agent.py` to include rankings
- [ ] Update `prompts.py` briefing structure to include rankings section

## Chat
- [ ] Add sportsbook question handler in `chat_cr.py`
- [ ] Add math explanation handler in `chat_cr.py`
- [ ] Add "why did you flag" event lookup in `chat_cr.py`

## API
- [ ] Update `/api/v1/report/briefing` response to include `CR_sportsbook_rankings`
- [ ] Update analysis response model if needed

## Frontend
- [ ] Add sportsbook rankings table to `index.html`
- [ ] Add math proof collapsible to finding cards in `index.html`
- [ ] Implement `renderSportsbookRankings()` in `app.js`
- [ ] Implement `renderMathProof()` in `app.js`
- [ ] Add table + verdict + math styles to `styles.css`

## Tests
- [ ] Add test for `generate_CR_sportsbook_rankings()` with known data
- [ ] Add test verifying `CR_math_proof` present in all finding types
- [ ] Add test for `compute_CR_math_explanation()` with positive and negative odds

---

# ✅ EXIT CRITERIA

- Every finding in the briefing shows inline math (formula + numbers)
- Sportsbook rankings table appears in both briefing text and frontend UI
- Rankings include: avg vig, best line %, stale count, quality score, verdict
- Chat correctly answers "explain the math" and "which books to avoid" questions
- All existing tests still pass
- Math explanation tests pass for standard odds examples (-110/-110, -150/+130, etc.)

---

**Phase 9 Status**: Ready to implement after Phase 8
**Dependencies**: Phase 8 complete (LLM agent wired in)
**Next Phase**: Phase 10 — Deployment + DEVLOG

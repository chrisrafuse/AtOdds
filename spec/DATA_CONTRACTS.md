# DATA_CONTRACTS.md
## Author: Chris Rafuse
## Version: 1.0
## Language: Python (Simple, Deterministic, Typed-Light)

# 0. RULES

- ALL variables MUST be prefixed with `CR_`
- ALL data objects are JSON-serializable dictionaries
- NO implicit fields
- NO dynamic shape changes at runtime
- ALL timestamps are ISO 8601 strings
- ALL odds stored as integers (American odds)
- ALL probabilities stored as floats (0.0 → 1.0)

---

# 1. ROOT SNAPSHOT CONTRACT

CR_snapshot = {
    "CR_snapshot_id": str,
    "CR_generated_at": str,
    "CR_events": [CR_event]
}

---

# 2. EVENT CONTRACT

CR_event = {
    "CR_event_id": str,
    "CR_sport": str,
    "CR_home_team": str,
    "CR_away_team": str,
    "CR_commence_time": str,
    "CR_markets": [CR_market]
}

---

# 3. MARKET CONTRACT

CR_market = {
    "CR_market_type": str,  # moneyline | spread | total
    "CR_sportsbooks": [CR_sportsbook_record]
}

---

# 4. SPORTSBOOK RECORD

CR_sportsbook_record = {
    "CR_sportsbook_id": str,
    "CR_last_update": str,
    "CR_outcomes": [CR_outcome]
}

---

# 5. OUTCOME CONTRACT

CR_outcome = {
    "CR_name": str,           # team name or Over/Under
    "CR_line": float | None,  # spread or total value
    "CR_price": int           # American odds
}

---

# 6. NORMALIZED ANALYTICS CONTRACT

CR_analytics_result = {
    "CR_event_id": str,
    "CR_market_type": str,
    "CR_best_lines": dict,
    "CR_consensus": dict,
    "CR_vig_by_book": dict,
    "CR_no_vig_probs": dict
}

---

# 7. FINDING CONTRACT

CR_finding = {
    "CR_finding_id": str,
    "CR_type": str,       # stale | outlier | arb | integrity | value
    "CR_severity": str,   # low | medium | high | critical
    "CR_event_id": str,
    "CR_market_type": str,
    "CR_evidence_ids": [str],
    "CR_rule_id": str,
    "CR_summary": str,
    "CR_metrics": dict
}

---

# 8. BRIEFING CONTRACT

CR_briefing = {
    "CR_run_id": str,
    "CR_snapshot_id": str,
    "CR_generated_at": str,
    "CR_market_overview": dict,
    "CR_anomalies": [CR_finding],
    "CR_value_opportunities": [CR_finding],
    "CR_arbitrage_opportunities": [CR_finding],
    "CR_sportsbook_rankings": list,
    "CR_limitations": [str],
    "CR_evidence_index": dict
}

---

# 9. CHAT RESPONSE CONTRACT

CR_chat_response = {
    "CR_answer": str,
    "CR_evidence_ids": [str],
    "CR_confidence": float,
    "CR_status": str  # success | partial | unsupported
}

---

# 10. TRACE CONTRACT

CR_trace = {
    "CR_run_id": str,
    "CR_steps": list,
    "CR_tool_calls": list,
    "CR_errors": list,
    "CR_latency_ms": int
}
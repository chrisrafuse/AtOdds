# TOOL_REGISTRY.md
## Author: Chris Rafuse
## Version: 1.0
## Language: Python

# 0. RULES

- ALL tools must be deterministic
- ALL inputs/outputs must follow DATA_CONTRACTS.md
- ALL variables must use CR_ prefix
- NO side effects in analysis tools
- ALL tools return JSON-serializable dicts

---

# 1. SNAPSHOT TOOLS

## load_snapshot

Input:
CR_input = {
    "CR_snapshot_path": str
}

Output:
CR_output = CR_snapshot

---

# 2. EVENT TOOLS

## list_events

Output:
CR_output = {
    "CR_events": [CR_event_id]
}

---

## get_event_markets

Input:
CR_input = {
    "CR_event_id": str
}

Output:
CR_output = {
    "CR_markets": [CR_market]
}

---

# 3. ODDS MATH TOOLS

## compute_implied_probability

Input:
CR_input = {
    "CR_price": int
}

Output:
CR_output = {
    "CR_implied_probability": float
}

---

## compute_vig

Input:
CR_input = {
    "CR_outcomes": [CR_outcome]
}

Output:
CR_output = {
    "CR_vig": float
}

---

## compute_no_vig_probabilities

Input:
CR_input = {
    "CR_outcomes": [CR_outcome]
}

Output:
CR_output = {
    "CR_no_vig_probs": dict
}

---

# 4. MARKET ANALYSIS TOOLS

## compute_best_lines

Input:
CR_input = {
    "CR_event_id": str,
    "CR_market_type": str
}

Output:
CR_output = {
    "CR_best_lines": dict
}

---

## compute_consensus

Input:
CR_input = {
    "CR_event_id": str,
    "CR_market_type": str
}

Output:
CR_output = {
    "CR_consensus": dict
}

---

# 5. DETECTION TOOLS

## detect_stale_lines

Output:
CR_output = {
    "CR_findings": [CR_finding]
}

---

## detect_outliers

Output:
CR_output = {
    "CR_findings": [CR_finding]
}

---

## detect_arbitrage

Output:
CR_output = {
    "CR_findings": [CR_finding]
}

---

## detect_value_edges

Output:
CR_output = {
    "CR_findings": [CR_finding]
}

---

## detect_integrity_issues

Output:
CR_output = {
    "CR_findings": [CR_finding]
}

---

# 6. RANKING TOOLS

## rank_sportsbooks

Output:
CR_output = {
    "CR_rankings": list
}

---

# 7. EVIDENCE TOOL

## get_finding_details

Input:
CR_input = {
    "CR_finding_id": str
}

Output:
CR_output = CR_finding

---

# 8. CHAT SUPPORT TOOL

## answer_scope_check

Input:
CR_input = {
    "CR_question": str
}

Output:
CR_output = {
    "CR_is_supported": bool,
    "CR_reason": str
}
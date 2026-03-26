# DATA_STRUCTURE_ALIGNMENT_PLAN.md
## Author: Chris Rafuse
## Purpose: Align current data structures with CR_ specification contracts
## Priority: HIGH - Core data consistency requirement

---

# 0. EXECUTIVE SUMMARY

**Current State**: Mixed data structure approach (dataclasses + dictionaries)
**Target State**: 100% CR_ compliant JSON-serializable dictionaries
**Impact**: Critical for data consistency, serialization, and system reliability

---

# 1. CURRENT VS TARGET STRUCTURES

## Current Implementation Issues

### Dataclasses vs Dictionaries
```python
# CURRENT - Mixed approach
@dataclass
class CR_event:
    id: str
    name: str
    sport: str
    markets: List[CR_market]

# TARGET - Pure dictionaries
CR_event = {
    "CR_event_id": str,
    "CR_sport": str,
    "CR_home_team": str,
    "CR_away_team": str,
    "CR_commence_time": str,
    "CR_markets": [CR_market]
}
```

### Missing CR_ Fields
```python
# CURRENT - Missing required CR_ fields
CR_outcome = {
    "name": "Team A",
    "price": 1.85  # Decimal odds
}

# TARGET - Complete CR_ structure
CR_outcome = {
    "CR_name": str,           # team name or Over/Under
    "CR_line": float | None,  # spread or total value
    "CR_price": int           # American odds
}
```

---

# 2. SPECIFICATION COMPLIANCE GAPS

## Data Contracts Specification Requirements

### Missing Fields Analysis
| Contract | Missing Fields | Current Issues |
|----------|----------------|----------------|
| CR_snapshot | CR_snapshot_id, CR_generated_at | Uses datetime objects |
| CR_event | CR_home_team, CR_away_team, CR_commence_time | Missing team fields |
| CR_market | CR_market_type, CR_sportsbooks | Different structure |
| CR_outcome | CR_line, CR_price (American) | Uses decimal odds |
| CR_finding | CR_finding_id, CR_severity, CR_rule_id | Incomplete structure |
| CR_briefing | CR_run_id, CR_snapshot_id, CR_evidence_index | Different structure |

### Data Type Mismatches
| Field | Current Type | Required Type | Action |
|-------|---------------|----------------|--------|
| CR_price | float (decimal) | int (American) | Convert odds format |
| CR_timestamp | datetime object | str (ISO 8601) | Serialize to string |
| CR_probability | float | float (0.0-1.0) | Validate range |
| CR_line | mixed | float | Standardize |

---

# 3. MIGRATION STRATEGY

## Phase 1: Contract Definition (Foundation)
**Priority**: CRITICAL
**Files**: `packages/data/contracts.py`

### Tasks
1. **Replace Dataclasses with Dictionary Schemas**
```python
# REMOVE dataclass approach
@dataclass
class CR_event:
    id: str
    name: str

# REPLACE with dictionary templates
CR_EVENT_SCHEMA = {
    "CR_event_id": str,
    "CR_sport": str,
    "CR_home_team": str,
    "CR_away_team": str,
    "CR_commence_time": str,
    "CR_markets": list
}
```

2. **Define Validation Functions**
```python
def validate_CR_event(CR_event_data: dict) -> dict:
    """Validate CR_event structure against schema"""
    required_fields = ["CR_event_id", "CR_sport", "CR_home_team", "CR_away_team", "CR_commence_time", "CR_markets"]
    # Validation logic
```

3. **Create Factory Functions**
```python
def create_CR_event(CR_event_id: str, CR_sport: str, CR_home_team: str, CR_away_team: str, CR_commence_time: str, CR_markets: list) -> dict:
    """Create valid CR_event dictionary"""
    return {
        "CR_event_id": CR_event_id,
        "CR_sport": CR_sport,
        "CR_home_team": CR_home_team,
        "CR_away_team": CR_away_team,
        "CR_commence_time": CR_commence_time,
        "CR_markets": CR_markets
    }
```

## Phase 2: Data Loading Transformation
**Priority**: CRITICAL
**Files**: `packages/data/loader.py`, `data/sample_data.json`

### Tasks
1. **Transform Sample Data Structure**
```json
// CURRENT sample_data.json
{
  "events": [
    {
      "id": "event_001",
      "name": "Lakers vs Warriors",
      "sport": "basketball",
      "markets": [...]
    }
  ]
}

// TARGET sample_data.json
{
  "CR_events": [
    {
      "CR_event_id": "event_001",
      "CR_sport": "basketball", 
      "CR_home_team": "Lakers",
      "CR_away_team": "Warriors",
      "CR_commence_time": "2024-01-15T19:00:00Z",
      "CR_markets": [...]
    }
  ]
}
```

2. **Update Loader Logic**
```python
def load_data(CR_file_path: str = None) -> dict:
    """Load and transform to CR_snapshot structure"""
    # Load raw JSON
    # Transform to CR_snapshot
    # Validate structure
    # Return CR_snapshot dict
```

3. **Add Odds Conversion**
```python
def convert_decimal_to_american(CR_decimal_price: float) -> int:
    """Convert decimal odds to American odds"""
    if CR_decimal_price >= 2.0:
        return int((CR_decimal_price - 1) * 100)
    else:
        return int(-100 / (CR_decimal_price - 1))
```

## Phase 3: Core Engine Adaptation
**Priority**: HIGH
**Files**: `packages/core_engine/*.py`

### Tasks
1. **Update Math Functions for American Odds**
```python
def compute_implied_probability(CR_price: int) -> dict:
    """Compute implied probability from American odds"""
    if CR_price > 0:
        CR_prob = 100 / (CR_price + 100)
    else:
        CR_prob = abs(CR_price) / (abs(CR_price) + 100)
    
    return {
        "CR_implied_probability": CR_prob,
        "CR_american_price": CR_price
    }
```

2. **Update Detection Logic**
```python
def detect_arbitrage(CR_events: list) -> list:
    """Detect arbitrage in CR_events structure"""
    CR_findings = []
    
    for CR_event in CR_events:
        for CR_market in CR_event["CR_markets"]:
            # Detection logic with CR_ variables
            pass
    
    return CR_findings
```

## Phase 4: Tools Registry Update
**Priority**: HIGH
**Files**: `packages/tools/registry.py`

### Tasks
1. **Update Tool Signatures**
```python
def tool_detect_arbitrage(CR_snapshot: dict) -> dict:
    """Tool wrapper for arbitrage detection"""
    try:
        CR_findings = detect_arbitrage(CR_snapshot["CR_events"])
        return {
            "CR_success": True,
            "CR_findings": CR_findings,
            "CR_count": len(CR_findings)
        }
    except Exception as CR_error:
        return {
            "CR_success": False,
            "CR_error": str(CR_error)
        }
```

## Phase 5: Agent Layer Transformation
**Priority**: HIGH
**Files**: `packages/agent/*.py`

### Tasks
1. **Update Agent Data Flow**
```python
def run_agent(CR_snapshot: dict) -> list:
    """Run agent with CR_ data structures"""
    CR_findings = []
    
    # Tool calls with CR_ data
    CR_arb_result = tool_detect_arbitrage(CR_snapshot)
    if CR_arb_result["CR_success"]:
        CR_findings.extend(CR_arb_result["CR_findings"])
    
    return CR_findings
```

## Phase 6: Reporting Structure Update
**Priority**: MEDIUM
**Files**: `packages/reporting/briefing.py`

### Tasks
1. **Update Briefing Structure**
```python
def generate_briefing(CR_findings: list, CR_snapshot: dict = None) -> str:
    """Generate briefing with CR_ structure"""
    CR_briefing_data = {
        "CR_run_id": generate_run_id(),
        "CR_snapshot_id": CR_snapshot.get("CR_snapshot_id") if CR_snapshot else None,
        "CR_generated_at": datetime.now().isoformat(),
        "CR_anomalies": [f for f in CR_findings if f["CR_type"] == "stale"],
        "CR_value_opportunities": [f for f in CR_findings if f["CR_type"] == "value"],
        "CR_arbitrage_opportunities": [f for f in CR_findings if f["CR_type"] == "arbitrage"]
    }
```

---

# 4. VALIDATION FRAMEWORK

## Structure Validation Functions

```python
def validate_CR_snapshot(CR_snapshot_data: dict) -> dict:
    """Validate complete CR_snapshot structure"""
    CR_validation_result = {
        "CR_valid": True,
        "CR_errors": [],
        "CR_warnings": []
    }
    
    # Check required fields
    CR_required_fields = ["CR_snapshot_id", "CR_generated_at", "CR_events"]
    for CR_field in CR_required_fields:
        if CR_field not in CR_snapshot_data:
            CR_validation_result["CR_errors"].append(f"Missing {CR_field}")
            CR_validation_result["CR_valid"] = False
    
    # Validate events
    if "CR_events" in CR_snapshot_data:
        for CR_event in CR_snapshot_data["CR_events"]:
            CR_event_validation = validate_CR_event(CR_event)
            if not CR_event_validation["CR_valid"]:
                CR_validation_result["CR_errors"].extend(CR_event_validation["CR_errors"])
    
    return CR_validation_result
```

## Data Type Validation

```python
def validate_data_types(CR_data: dict, CR_schema: dict) -> dict:
    """Validate data types against schema"""
    CR_validation_result = {"CR_valid": True, "CR_errors": []}
    
    for CR_field, CR_expected_type in CR_schema.items():
        if CR_field in CR_data:
            CR_actual_value = CR_data[CR_field]
            CR_actual_type = type(CR_actual_value)
            
            # Type checking logic
            if not isinstance(CR_actual_value, CR_expected_type):
                CR_validation_result["CR_errors"].append(
                    f"Type mismatch for {CR_field}: expected {CR_expected_type}, got {CR_actual_type}"
                )
                CR_validation_result["CR_valid"] = False
    
    return CR_validation_result
```

---

# 5. MIGRATION TOOLS

## Automated Transformation Script

```python
#!/usr/bin/env python3
"""
Data Structure Migration Tool
Transforms current data structures to CR_ compliant format
"""

import json
from datetime import datetime

def transform_event_to_CR(CR_old_event: dict) -> dict:
    """Transform old event structure to CR format"""
    CR_name_parts = CR_old_event.get("name", " vs ").split(" vs ")
    
    return {
        "CR_event_id": CR_old_event.get("id", ""),
        "CR_sport": CR_old_event.get("sport", ""),
        "CR_home_team": CR_name_parts[0] if len(CR_name_parts) > 1 else "",
        "CR_away_team": CR_name_parts[1] if len(CR_name_parts) > 1 else "",
        "CR_commence_time": datetime.now().isoformat(),  # Default to now
        "CR_markets": [transform_market_to_CR(m) for m in CR_old_event.get("markets", [])]
    }

def transform_market_to_CR(CR_old_market: dict) -> dict:
    """Transform old market structure to CR format"""
    return {
        "CR_market_type": CR_old_market.get("name", ""),
        "CR_sportsbooks": [transform_sportsbook_to_CR(CR_old_market)]
    }

def transform_sportsbook_to_CR(CR_old_market: dict) -> dict:
    """Transform market to sportsbook record"""
    return {
        "CR_sportsbook_id": CR_old_market.get("bookmaker", ""),
        "CR_last_update": datetime.now().isoformat(),
        "CR_outcomes": [transform_outcome_to_CR(o) for o in CR_old_market.get("outcomes", [])]
    }

def transform_outcome_to_CR(CR_old_outcome: dict) -> dict:
    """Transform outcome to CR format with American odds"""
    CR_decimal_price = CR_old_outcome.get("price", 1.0)
    CR_american_price = convert_decimal_to_american(CR_decimal_price)
    
    return {
        "CR_name": CR_old_outcome.get("name", ""),
        "CR_line": None,  # Default for moneyline
        "CR_price": CR_american_price
    }

def migrate_sample_data(CR_input_path: str, CR_output_path: str) -> None:
    """Migrate sample data file to CR format"""
    with open(CR_input_path, 'r') as f:
        CR_old_data = json.load(f)
    
    CR_new_data = {
        "CR_snapshot_id": f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "CR_generated_at": datetime.now().isoformat(),
        "CR_events": [transform_event_to_CR(event) for event in CR_old_data.get("events", [])]
    }
    
    with open(CR_output_path, 'w') as f:
        json.dump(CR_new_data, f, indent=2)
```

---

# 6. TESTING STRATEGY

## Unit Tests for Data Structures

```python
def test_CR_event_structure():
    """Test CR_event structure validation"""
    CR_valid_event = {
        "CR_event_id": "test_001",
        "CR_sport": "basketball",
        "CR_home_team": "Lakers",
        "CR_away_team": "Warriors",
        "CR_commence_time": "2024-01-15T19:00:00Z",
        "CR_markets": []
    }
    
    CR_result = validate_CR_event(CR_valid_event)
    assert CR_result["CR_valid"] == True

def test_odds_conversion():
    """Test decimal to American odds conversion"""
    # Test positive odds
    CR_american = convert_decimal_to_american(2.5)
    assert CR_american == 150
    
    # Test negative odds
    CR_american = convert_decimal_to_american(1.8)
    assert CR_american == -125
```

## Integration Tests

```python
def test_end_to_end_data_flow():
    """Test complete data flow with CR structures"""
    # Load CR data
    CR_snapshot = load_data("data/sample_data_cr.json")
    
    # Validate structure
    CR_validation = validate_CR_snapshot(CR_snapshot)
    assert CR_validation["CR_valid"] == True
    
    # Run analysis
    CR_findings = run_agent(CR_snapshot)
    
    # Generate briefing
    CR_briefing = generate_briefing(CR_findings, CR_snapshot)
    
    # Validate output
    assert isinstance(CR_briefing, str)
    assert len(CR_briefing) > 0
```

---

# 7. ROLLBACK PLAN

## Git Strategy
1. **Branch per Phase**: Separate branch for each migration phase
2. **Validation Gates**: Tests must pass before merge
3. **Rollback Points**: Tag each successful phase

## Recovery Procedures
1. **Data Backup**: Backup all data files before migration
2. **Code Reversion**: Git revert if critical issues found
3. **Partial Rollback**: Revert specific phases if needed

---

# 8. SUCCESS METRICS

## Technical Metrics
- [ ] 100% data structure compliance with CR specification
- [ ] All data serializable to JSON
- [ ] All validation functions pass
- [ ] Zero data loss during migration
- [ ] Performance maintained (<5% regression)

## Quality Metrics
- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Sample data transformed correctly

---

# 9. ESTIMATED TIMELINE

| Phase | Duration | Complexity |
|-------|----------|------------|
| Phase 1: Contract Definition | 3 hours | Medium |
| Phase 2: Data Loading | 2 hours | Medium |
| Phase 3: Core Engine | 4 hours | High |
| Phase 4: Tools Registry | 2 hours | Medium |
| Phase 5: Agent Layer | 2 hours | Medium |
| Phase 6: Reporting | 2 hours | Low |
| **Total** | **15 hours** | **Medium-High** |

---

# 10. LONG-TERM BENEFITS

## Immediate Benefits
- Consistent data structures across system
- Improved serialization and deserialization
- Better validation and error handling
- Clearer data contracts

## Long-term Benefits
- Easier data format evolution
- Better integration with external systems
- Improved debugging and tracing
- Strong foundation for production scaling

---

This alignment is fundamental to establishing a robust, consistent, and maintainable data foundation for the entire odds analysis system.

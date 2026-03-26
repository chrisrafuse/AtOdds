# CR_SIGNATURE_MIGRATION_PLAN.md
## Author: Chris Rafuse
## Purpose: Migrate all variables to CR_ prefix signature
## Priority: HIGH - Core architectural requirement

---

# 0. EXECUTIVE SUMMARY

**Current State**: System uses mixed naming conventions (some CR_ prefixes, but not comprehensive)
**Target State**: 100% CR_ prefix compliance across all variables, functions, and data structures
**Impact**: Critical for system consistency, authorship attribution, and architectural clarity

---

# 1. MIGRATION SCOPE

## Files Requiring Updates

### Core Data Contracts
- `packages/data/contracts.py` - All class definitions and field names
- `packages/data/loader.py` - All local variables and return structures

### Core Engine
- `packages/core_engine/odds_math.py` - All function parameters and variables
- `packages/core_engine/consensus.py` - All calculation variables and returns
- `packages/core_engine/detectors.py` - All detection logic variables

### Tools Registry
- `packages/tools/registry.py` - All tool function signatures and internal variables

### Agent Layer
- `packages/agent/agent.py` - All orchestration variables and data structures
- `packages/agent/prompts.py` - All prompt variables and templates

### Reporting
- `packages/reporting/briefing.py` - All briefing generation variables
- `packages/schemas/briefing_schema.py` - All validation variables

### Chat Interface
- `packages/chat/chat.py` - All chat session variables and responses

### Observability
- `packages/observability/trace.py` - All tracing variables and session data

### Tests
- `tests/test_core.py` - All test variables and assertions

### Entry Points
- `apps/cli/main.py` - All main script variables

---

# 2. CR_ PREFIX STANDARDS

## Variable Naming Rules

```python
# GOOD - All CR_ prefixed
CR_event_id = "event_001"
CR_implied_probability = 0.65
CR_best_lines = {"Team A": (bookmaker, price)}
CR_findings = [CR_finding1, CR_finding2]

# BAD - Mixed or no prefixes
event_id = "event_001"
implied_prob = 0.65
best_lines = {"Team A": (bookmaker, price)}
```

## Function Naming Rules

```python
# GOOD - CR_ prefixes for parameters and returns
def compute_implied_probability(CR_price: int) -> dict:
    CR_prob = calculate_probability(CR_price)
    return {"CR_implied_probability": CR_prob}

# BAD - Mixed naming
def compute_implied_probability(price: int) -> dict:
    prob = calculate_probability(price)
    return {"implied_probability": prob}
```

## Data Structure Rules

```python
# GOOD - All keys CR_ prefixed
CR_event = {
    "CR_event_id": "event_001",
    "CR_sport": "basketball",
    "CR_markets": [CR_market1, CR_market2]
}

# BAD - Mixed keys
CR_event = {
    "id": "event_001",
    "sport": "basketball",
    "markets": [market1, market2]
}
```

---

# 3. PHASED MIGRATION STRATEGY

## Phase 1: Data Contracts (Foundation)
**Priority**: CRITICAL
**Files**: `packages/data/contracts.py`, `packages/data/loader.py`

### Tasks
1. Update all dataclass field names to CR_ prefix
2. Update all dictionary keys in loader.py
3. Update all function parameters and returns
4. Update sample_data.json to match new structure

### Validation
- All data structures serialize correctly
- Loading pipeline works end-to-end
- No breaking changes in data flow

## Phase 2: Core Engine (Truth Layer)
**Priority**: CRITICAL  
**Files**: `packages/core_engine/*.py`

### Tasks
1. Update all mathematical function parameters to CR_ prefix
2. Update all local variables in calculations
3. Update all return structures to use CR_ keys
4. Update detector function signatures and internal variables

### Validation
- All mathematical calculations produce same results
- Detection algorithms function correctly
- No performance regression

## Phase 3: Tools Registry (Interface Layer)
**Priority**: HIGH
**Files**: `packages/tools/registry.py`

### Tasks
1. Update all tool function parameters to CR_ prefix
2. Update all tool return structures
3. Update all internal tool variables
4. Update tool registry mappings

### Validation
- All tools callable with new signatures
- Agent can successfully call all tools
- Tool outputs match expected CR_ structure

## Phase 4: Agent Layer (Orchestration)
**Priority**: HIGH
**Files**: `packages/agent/*.py`

### Tasks
1. Update all orchestration variables to CR_ prefix
2. Update agent function parameters and returns
3. Update prompt templates to use CR_ terminology
4. Update analysis summary variables

### Validation
- Agent orchestration works end-to-end
- Tool calls succeed with new signatures
- Analysis outputs use CR_ structure

## Phase 5: Reporting & Output (Presentation Layer)
**Priority**: MEDIUM
**Files**: `packages/reporting/*.py`, `packages/schemas/*.py`

### Tasks
1. Update all briefing generation variables
2. Update all validation schema variables
3. Update all formatting variables
4. Update output structure keys

### Validation
- Briefing generation produces correct output
- Schema validation works with new structures
- Output formatting maintains readability

## Phase 6: Chat Interface (Interaction Layer)
**Priority**: MEDIUM
**Files**: `packages/chat/*.py`

### Tasks
1. Update all chat session variables
2. Update all response structure variables
3. Update all question processing variables
4. Update evidence retrieval variables

### Validation
- Chat interface functions correctly
- Responses use CR_ structure
- Grounded Q&A maintains accuracy

## Phase 7: Observability (Monitoring Layer)
**Priority**: LOW
**Files**: `packages/observability/*.py`

### Tasks
1. Update all tracing variables
2. Update all session variables
3. Update all logging structures
4. Update all metric variables

### Validation
- Tracing system works correctly
- Logs use CR_ structure
- Metrics collection functions

## Phase 8: Tests & Entry Points (Validation Layer)
**Priority**: MEDIUM
**Files**: `tests/*.py`, `apps/cli/*.py`

### Tasks
1. Update all test variables and assertions
2. Update main script variables
3. Update test data structures
4. Update validation logic

### Validation
- All tests pass with new structure
- Main entry point functions correctly
- Test coverage maintained

---

# 4. IMPLEMENTATION DETAILS

## Migration Script Template

```python
#!/usr/bin/env python3
"""
CR_ Prefix Migration Helper
Automates common variable renaming patterns
"""

import re
import os

def migrate_file(filepath: str) -> None:
    """Migrate a single file to CR_ prefix"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Common patterns to replace
    patterns = [
        (r'\bevent_id\b', 'CR_event_id'),
        (r'\bprice\b', 'CR_price'),
        (r'\bprobability\b', 'CR_probability'),
        (r'\bmarket\b', 'CR_market'),
        (r'\bfinding\b', 'CR_finding'),
        (r'\bbriefing\b', 'CR_briefing'),
        # Add more patterns as needed
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

def migrate_directory(directory: str) -> None:
    """Migrate all Python files in directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                migrate_file(os.path.join(root, file))
```

## Validation Checklist

For each migrated file:
- [ ] All variables start with CR_
- [ ] All function parameters use CR_ prefix
- [ ] All return structures use CR_ keys
- [ ] No mixed naming conventions
- [ ] File functionality preserved
- [ ] Tests pass (if applicable)

---

# 5. RISK MITIGATION

## Potential Issues
1. **Breaking Changes**: Migration may break dependent code
2. **Human Error**: Manual migration may miss variables
3. **Test Coverage**: Tests may not catch all regressions

## Mitigation Strategies
1. **Incremental Migration**: Phase by phase approach
2. **Automated Validation**: Scripts to check CR_ compliance
3. **Comprehensive Testing**: Full test suite after each phase
4. **Rollback Plan**: Git branches for each phase

---

# 6. SUCCESS CRITERIA

## Technical Criteria
- [ ] 100% variable compliance with CR_ prefix
- [ ] All functionality preserved
- [ ] All tests pass
- [ ] No performance regression
- [ ] Clean, consistent codebase

## Architectural Criteria
- [ ] Clear authorship attribution
- [ ] Consistent naming conventions
- [ ] Improved code readability
- [ ] Enhanced maintainability
- [ ] Strong architectural identity

---

# 7. ESTIMATED TIMELINE

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Data Contracts | 2 hours | None |
| Phase 2: Core Engine | 3 hours | Phase 1 |
| Phase 3: Tools Registry | 1 hour | Phase 2 |
| Phase 4: Agent Layer | 2 hours | Phase 3 |
| Phase 5: Reporting | 2 hours | Phase 4 |
| Phase 6: Chat Interface | 1 hour | Phase 5 |
| Phase 7: Observability | 1 hour | Phase 6 |
| Phase 8: Tests & Entry | 2 hours | Phase 7 |
| **Total** | **14 hours** | **Sequential** |

---

# 8. NEXT STEPS

1. **Create Migration Branches**: Git branch for each phase
2. **Develop Migration Tools**: Automated scripts for common patterns
3. **Execute Phase 1**: Start with data contracts (foundation)
4. **Validate Each Phase**: Comprehensive testing before proceeding
5. **Final Integration**: End-to-end system validation
6. **Documentation Update**: Update all documentation to reflect CR_ structure

---

# 9. LONG-TERM BENEFITS

## Immediate Benefits
- Consistent codebase architecture
- Clear authorship attribution
- Enhanced code readability
- Improved maintainability

## Long-term Benefits
- Strong system identity
- Easier onboarding for new developers
- Better debugging and tracing
- Professional codebase presentation
- Foundation for production evolution

---

This migration is not just cosmetic—it's fundamental to establishing the system's architectural identity and ensuring long-term maintainability and clarity.

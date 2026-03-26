# PHASE_PLAN_2_CR_SIGNATURE_MIGRATION.md
## Author: Chris Rafuse
## Duration: Week 2-3 (10-14 days)
## Purpose: Migrate all variables to CR_ prefix signature
## Entry Criteria: Phase 1 completed and approved
## Exit Criteria: 100% CR_ prefix compliance achieved

---

# 🎯 PHASE OBJECTIVES

Achieve complete CR_ signature compliance across the entire codebase:
- Migrate all variables to CR_ prefix
- Update all function signatures
- Transform all data structure keys
- Maintain system functionality throughout
- Ensure no regressions in performance or behavior

---

# 📋 TASK CHECKLIST

## Week 2: Core Components Migration

### Day 1-2: Core Engine Migration
- [ ] **Odds Math Module** (`packages/core_engine/odds_math.py`)
  - [ ] Migrate all function parameters to CR_ prefix
  - [ ] Update all local variables
  - [ ] Transform return structures to use CR_ keys
  - [ ] Update mathematical formulas with CR_ variables
  - [ ] Add American odds handling
  - [ ] Create comprehensive unit tests

- [ ] **Consensus Module** (`packages/core_engine/consensus.py`)
  - [ ] Migrate all function parameters to CR_ prefix
  - [ ] Update calculation variables
  - [ ] Transform return structures
  - [ ] Update best line calculation logic
  - [ ] Add CR_ compliance validation
  - [ ] Create integration tests

- [ ] **Detectors Module** (`packages/core_engine/detectors.py`)
  - [ ] Migrate all detection function parameters
  - [ ] Update detection algorithm variables
  - [ ] Transform finding structures
  - [ ] Update confidence calculation variables
  - [ ] Add CR_ compliance to all findings
  - [ ] Create comprehensive detection tests

### Day 3-4: Tools Registry Migration
- [ ] **Registry Module** (`packages/tools/registry.py`)
  - [ ] Update all tool function signatures to CR_ prefix
  - [ ] Migrate all internal tool variables
  - [ ] Transform tool return structures
  - [ ] Update tool registry mappings
  - [ ] Add CR_ validation to tool outputs
  - [ ] Create tool compliance tests

- [ ] **Tool Wrapper Functions**
  - [ ] Update all tool wrapper parameters
  - [ ] Migrate error handling variables
  - [ ] Transform success/error structures
  - [ ] Add CR_ logging to tool calls
  - [ ] Update tool documentation
  - [ ] Create tool integration tests

### Day 5: Agent Layer Migration
- [ ] **Agent Module** (`packages/agent/agent.py`)
  - [ ] Update orchestration variables to CR_ prefix
  - [ ] Migrate agent function parameters
  - [ ] Transform agent return structures
  - [ ] Update analysis summary variables
  - [ ] Add CR_ compliance validation
  - [ ] Create agent orchestration tests

- [ ] **Prompts Module** (`packages/agent/prompts.py`)
  - [ ] Update all prompt template variables
  - [ ] Migrate system prompt variables
  - [ ] Transform prompt structure variables
  - [ ] Add CR_ terminology throughout
  - [ ] Update prompt documentation
  - [ ] Create prompt validation tests

## Week 3: Interface and Support Components Migration

### Day 6-7: Reporting and Chat Migration
- [ ] **Briefing Module** (`packages/reporting/briefing.py`)
  - [ ] Update all briefing generation variables
  - [ ] Migrate formatting variables to CR_ prefix
  - [ ] Transform output structure variables
  - [ ] Update recommendation variables
  - [ ] Add CR_ compliance to all outputs
  - [ ] Create comprehensive briefing tests

- [ ] **Chat Module** (`packages/chat/chat.py`)
  - [ ] Update all chat session variables
  - [ ] Migrate response structure variables
  - [ ] Transform question processing variables
  - [ ] Update evidence retrieval variables
  - [ ] Add CR_ compliance to chat responses
  - [ ] Create chat interface tests

### Day 8-9: Observability and Testing Migration
- [ ] **Trace Module** (`packages/observability/trace.py`)
  - [ ] Update all tracing variables to CR_ prefix
  - [ ] Migrate session variables
  - [ ] Transform logging structures
  - [ ] Update metric collection variables
  - [ ] Add CR_ compliance to all traces
  - [ ] Create tracing compliance tests

- [ ] **Test Suite** (`tests/test_core.py` and all test files)
  - [ ] Update all test variables to CR_ prefix
  - [ ] Migrate test assertion variables
  - [ ] Transform test data structures
  - [ ] Update mock object variables
  - [ ] Add CR_ compliance validation to tests
  - [ ] Create comprehensive migration tests

### Day 10: Integration and Validation
- [ ] **Entry Points Migration** (`apps/cli/main.py`)
  - [ ] Update main script variables to CR_ prefix
  - [ ] Migrate command-line argument variables
  - [ ] Transform pipeline variables
  - [ ] Update error handling variables
  - [ ] Add CR_ compliance validation
  - [ ] Create end-to-end integration tests

- [ ] **Configuration and Settings**
  - [ ] Update all configuration variables
  - [ ] Migrate environment variable references
  - [ ] Transform setting structures
  - [ ] Update default value variables
  - [ ] Add CR_ compliance validation
  - [ ] Create configuration tests

---

# 🔍 BUILD VERIFICATION CHECKLIST

## Pre-Build Requirements
- [ ] All core components migrated to CR_ prefix
- [ ] All interface components migrated
- [ ] All support components migrated
- [ ] All unit tests updated and passing

## Build Process Verification
```bash
# 1. Core Engine Build Test
python -c "
from packages.core_engine.odds_math import compute_implied_probability
from packages.core_engine.consensus import compute_best_lines
from packages.core_engine.detectors import detect_arbitrage
print('Core engine builds successfully')
"

# 2. Tools Registry Build Test
python -c "
from packages.tools.registry import TOOL_REGISTRY, get_tool
print('Tools registry builds successfully')
"

# 3. Agent Layer Build Test
python -c "
from packages.agent.agent import run_agent
from packages.agent.prompts import SYSTEM_PROMPT
print('Agent layer builds successfully')
"

# 4. Interface Components Build Test
python -c "
from packages.reporting.briefing import generate_briefing
from packages.chat.chat import OddsChat
print('Interface components build successfully')
"

# 5. Full System Build Test
python apps/cli/main.py --test-mode
```

## Build Success Criteria
- [ ] All components build without errors
- [ ] All imports work correctly
- [ ] No syntax errors in any file
- [ ] All type hints are correct
- [ ] All dependencies resolve correctly
- [ ] System starts and runs without errors

---

# 🧪 TESTING VERIFICATION CHECKLIST

## Unit Tests
- [ ] **Core Engine Tests**: All functions tested with CR_ variables
- [ ] **Tools Registry Tests**: All tools tested with CR_ signatures
- [ ] **Agent Tests**: All orchestration tested with CR_ variables
- [ ] **Interface Tests**: All components tested with CR_ compliance
- [ ] **Migration Tests**: All migration changes tested
- [ ] **Compliance Tests**: CR_ prefix compliance validated

## Integration Tests
- [ ] **End-to-End Tests**: Complete pipeline tested
- [ ] **Data Flow Tests**: Data flow through all components tested
- [ ] **Tool Integration Tests**: All tools work with CR_ data
- [ ] **Agent Integration Tests**: Orchestration works correctly
- [ ] **Reporting Integration Tests**: Briefing generation works
- [ ] **Chat Integration Tests**: Q&A functions correctly

## Regression Tests
- [ ] **Functional Regression**: All original functionality preserved
- [ ] **Performance Regression**: No performance degradation
- [ ] **Behavioral Regression**: No behavioral changes
- [ ] **API Regression**: All interfaces work as before
- [ ] **Data Regression**: Data processing unchanged
- [ ] **Output Regression**: Output formats consistent

## Compliance Tests
- [ ] **Prefix Compliance**: 100% CR_ prefix compliance
- [ ] **Naming Convention**: All naming conventions followed
- [ ] **Structure Compliance**: All structures use CR_ keys
- [ ] **Type Compliance**: All types correct and consistent
- [ ] **Format Compliance**: All formats match specification
- [ ] **Documentation Compliance**: All documentation updated

---

# ✅ PHASE COMPLETION VERIFICATION

## CR_ Compliance Verification
- [ ] **Variable Compliance**: 100% variables use CR_ prefix
- [ ] **Function Compliance**: 100% functions use CR_ parameters
- [ ] **Structure Compliance**: 100% structures use CR_ keys
- [ ] **Import Compliance**: All imports work correctly
- [ ] **Type Compliance**: All types correctly annotated
- [ ] **Documentation Compliance**: All documentation updated

## Functionality Verification
- [ ] **Core Engine**: All calculations work correctly
- [ ] **Detection Algorithms**: All algorithms function properly
- [ ] **Tools Registry**: All tools work with CR_ signatures
- [ ] **Agent Orchestration**: Orchestration works correctly
- [ ] **Reporting Generation**: Briefing generation works
- [ ] **Chat Interface**: Q&A functions properly

## Quality Assurance
- [ ] **Test Coverage**: 95%+ coverage for all migrated code
- [ ] **Code Quality**: All code quality standards met
- [ ] **Performance**: No performance regression
- [ ] **Memory Usage**: No memory leaks or excessive usage
- [ ] **Error Handling**: Robust error handling maintained
- [ ] **Documentation**: Complete and accurate documentation

## Build and Deployment
- [ ] **Build Success**: All builds pass without errors
- [ ] **Integration Success**: All integrations work correctly
- [ ] **Deployment Ready**: System ready for deployment
- [ ] **Rollback Ready**: Rollback procedures tested
- [ ] **Monitoring Ready**: Monitoring systems operational
- [ ] **Support Ready**: Support procedures documented

---

# 🚀 PHASE EXIT CRITERIA

## Mandatory Requirements (ALL must be satisfied)
- [ ] ✅ **CR_ Prefix Compliance**: 100% variable compliance achieved
- [ ] ✅ **Function Signature Compliance**: All functions use CR_ parameters
- [ ] ✅ **Structure Compliance**: All structures use CR_ keys
- [ ] ✅ **Build Success**: All builds pass without errors
- [ ] ✅ **Test Success**: All tests pass with 95%+ coverage
- [ ] ✅ **Functionality Success**: All functionality preserved

## Quality Gates
- [ ] **Code Quality**: All code quality standards met
- [ ] **Performance**: No performance regression detected
- [ ] **Documentation**: Complete and accurate documentation
- [ ] **Integration**: All integrations tested and working
- [ ] **Compliance**: 100% CR_ specification compliance

## Stakeholder Approval
- [ ] **Technical Lead**: Migration quality and compliance approved
- [ ] **QA Lead**: Testing and validation approved
- [ ] **Development Team**: Migration process approved
- [ ] **Project Manager**: Phase deliverables and timeline approved

---

# 📊 PROGRESS TRACKING

## Completion Metrics
- **Variables Migrated**: [ ] / [ ] total variables
- **Functions Migrated**: [ ] / [ ] total functions
- **Structures Migrated**: [ ] / [ ] total structures
- **Tests Updated**: [ ] / [ ] total tests
- **Files Migrated**: [ ] / [ ] total files

## Quality Metrics
- **CR_ Compliance**: [ ]% compliance achieved
- **Test Pass Rate**: [ ]% pass rate
- **Code Quality Score**: [ ]% quality score
- **Performance Score**: [ ]% performance score
- **Documentation Score**: [ ]% documentation score

## Risk Status
- **Technical Risks**: [Low/Medium/High]
- **Schedule Risks**: [Low/Medium/High]
- **Quality Risks**: [Low/Medium/High]
- **Integration Risks**: [Low/Medium/High]

---

# 🔄 NEXT PHASE DEPENDENCIES

## Prerequisites for Phase 3
- [ ] Phase 2 fully completed and approved
- [ ] 100% CR_ prefix compliance achieved
- [ ] All builds and tests passing
- [ ] Performance benchmarks maintained
- [ ] Documentation complete and approved
- [ ] Migration artifacts archived

## Handoff Requirements
- [ ] Migration documentation delivered
- [ ] CR_ compliance training completed
- [ ] Code review and approval completed
- [ ] Test results and reports delivered
- [ ] Performance benchmarks documented

---

**Phase 2 completion is mandatory before proceeding to Phase 3: System Enhancements.**

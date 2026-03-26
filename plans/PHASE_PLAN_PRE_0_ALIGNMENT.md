# PHASE_PLAN_PRE_0_ALIGNMENT.md
## Author: Chris Rafuse
## Duration: 2-3 days (before Phase 0)
## Purpose: Align codebase with Betstamp AI Odds Agent requirements and sample data format
## Entry Criteria: Project kickoff and requirements analysis
## Exit Criteria: Codebase aligned with Betstamp requirements and ready for Phase 0

---

# 🎯 PHASE OBJECTIVES

Align the existing codebase with Betstamp AI Odds Agent take-home requirements:
- Analyze Betstamp requirements from PDF
- Understand sample data structure and format
- Identify gaps between current code and requirements
- Update data structures to match Betstamp format
- Ensure detection algorithms work with Betstamp data
- Update all references from deleted sample_data.json

---

# 📋 REQUIREMENTS ANALYSIS

## Betstamp AI Odds Agent Requirements (from sample data analysis)

### Data Structure Requirements
- **Format**: JSON with nested structure
- **Sports**: NBA focus (expandable to other sports)
- **Sportsbooks**: 8 sportsbooks (DraftKings, FanDuel, BetMGM, Caesars, PointsBet, bet365, Pinnacle, BetRivers)
- **Markets**: 3 market types per game
  - `spread`: home_line, home_odds, away_line, away_odds
  - `moneyline`: home_odds, away_odds
  - `total`: line, over_odds, under_odds
- **Odds Format**: American odds (e.g., -111, 196)
- **Timestamps**: ISO 8601 format
- **Game Structure**: game_id, sport, home_team, away_team, commence_time, sportsbook, markets, last_updated

### Detection Requirements (inferred from data notes)
- **Arbitrage Detection**: Find opportunities across sportsbooks
- **Stale Line Detection**: Identify outdated last_updated times
- **Outlier Detection**: Find anomalous odds values
- **Value Edge Detection**: Identify favorable odds vs consensus
- **Market Efficiency Analysis**: Compare sportsbook margins

### Sample Data Characteristics
- **10 NBA games** × **8 sportsbooks** = **80 records**
- **Intentional anomalies** seeded for detection
- **American odds** throughout
- **Variance in spreads** (normal 0.5 point differences)
- **Pinnacle** has tightest margins (reference sportsbook)

---

# 📋 TASK CHECKLIST

## Day 1: Requirements Analysis and Gap Identification

### [ ] 1.1 Betstamp Requirements Analysis
- [ ] Read and analyze Betstamp AI Odds Agent PDF requirements
- [ ] Document all functional requirements
- [ ] Document all technical requirements
- [ ] Document all data format requirements
- [ ] Document all detection algorithm requirements
- [ ] Document all output format requirements

### [ ] 1.2 Current Codebase Analysis
- [ ] Analyze current data structures vs Betstamp format
- [ ] Review current detection algorithms vs requirements
- [ ] Assess current output formats vs requirements
- [ ] Identify missing functionality
- [ ] Identify incompatible functionality
- [ ] Document all gaps and misalignments

### [ ] 1.3 Sample Data Integration Analysis
- [ ] Analyze Betstamp sample data structure
- [ ] Map sample data fields to current data structures
- [ ] Identify required data transformations
- [ ] Test current loader with Betstamp data
- [ ] Document data mapping requirements
- [ ] Create data transformation plan

## Day 2: Data Structure Alignment

### [ ] 2.1 Update Data Contracts
- [ ] Update `packages/data/contracts.py` for Betstamp format
- [ ] Create CR_game structure matching Betstamp game data
- [ ] Create CR_market structure for spread/moneyline/total
- [ ] Create CR_sportsbook structure
- [ ] Update CR_snapshot structure for Betstamp data
- [ ] Maintain CR_ prefix compliance throughout

### [ ] 2.2 Update Data Loader
- [ ] Modify `packages/data/loader.py` for Betstamp JSON format
- [ ] Remove references to deleted `data/sample_data.json`
- [ ] Update to use `data/Betstamp AI Odds Agent - sample_odds_data.json`
- [ ] Add data validation for Betstamp format
- [ ] Add American odds handling
- [ ] Add sportsbook normalization

### [ ] 2.3 Update Detection Algorithms
- [ ] Review `packages/core_engine/detectors.py` for Betstamp data
- [ ] Update arbitrage detection for 3 market types
- [ ] Update stale line detection for last_updated field
- [ ] Update outlier detection for American odds
- [ ] Update value edge detection for consensus calculation
- [ ] Add market efficiency analysis

## Day 3: Integration and Testing

### [ ] 3.1 Update Core Engine
- [ ] Review `packages/core_engine/odds_math.py` for American odds
- [ ] Update implied probability calculations for American odds
- [ ] Update vig calculations for 3-outcome markets
- [ ] Update consensus calculations for multiple sportsbooks
- [ ] Add market efficiency metrics
- [ ] Maintain CR_ prefix compliance

### [ ] 3.2 Update Tools and Agent
- [ ] Update `packages/tools/registry.py` for new data structures
- [ ] Update `packages/agent/agent.py` for Betstamp analysis
- [ ] Update `packages/reporting/briefing.py` for Betstamp output
- [ ] Update `packages/chat/chat.py` for Betstamp queries
- [ ] Test all tools with Betstamp data
- [ ] Validate all outputs

### [ ] 3.3 Testing and Validation
- [ ] Create tests for Betstamp data loading
- [ ] Create tests for detection algorithms with Betstamp data
- [ ] Create tests for American odds handling
- [ ] Create tests for sportsbook analysis
- [ ] Run end-to-end test with Betstamp sample data
- [ ] Validate all functionality works correctly

---

# 🔍 BUILD VERIFICATION CHECKLIST

## Pre-Build Requirements
- [ ] All requirements analysis completed
- [ ] All gaps identified and documented
- [ ] All data structures updated for Betstamp format
- [ ] All detection algorithms updated
- [ ] All references to old sample data removed

## Build Process Verification
```bash
# 1. Data Loading Test
python -c "
from packages.data.loader import load_data
CR_snapshot = load_data('data/Betstamp AI Odds Agent - sample_odds_data.json')
print(f'Loaded {len(CR_snapshot.events)} games')
print(f'Sample game: {CR_snapshot.events[0]}')
"

# 2. Detection Algorithms Test
python -c "
from packages.data.loader import load_data
from packages.core_engine.detectors import detect_arbitrage, detect_stale_lines, detect_outliers, detect_value_edges
CR_snapshot = load_data('data/Betstamp AI Odds Agent - sample_odds_data.json')
arbitrages = detect_arbitrage(CR_snapshot.events)
stale_lines = detect_stale_lines(CR_snapshot.events)
print(f'Found {len(arbitrages)} arbitrages, {len(stale_lines)} stale lines')
"

# 3. Core Engine Test
python -c "
from packages.core_engine.odds_math import compute_implied_probability
# Test American odds
CR_prob = compute_implied_probability(-111)
print(f'American odds -111 implied probability: {CR_prob}')
"

# 4. End-to-End Test
python apps/cli/main.py --data-path="data/Betstamp AI Odds Agent - sample_odds_data.json"
```

## Build Success Criteria
- [ ] Betstamp sample data loads successfully
- [ ] All detection algorithms work with Betstamp data
- [ ] American odds calculations work correctly
- [ ] All outputs are CR_ compliant
- [ ] No references to deleted sample_data.json
- [ ] End-to-end pipeline works with Betstamp data

---

# 🧪 TESTING VERIFICATION CHECKLIST

## Data Loading Tests
- [ ] **Betstamp Data Loading**: Sample data loads without errors
- [ ] **Data Validation**: All data fields validated correctly
- [ ] **American Odds**: American odds handled properly
- [ ] **Sportsbook Data**: All 8 sportsbooks processed
- [ ] **Market Data**: All 3 market types processed
- [ ] **Timestamp Parsing**: ISO 8601 timestamps parsed correctly

## Detection Algorithm Tests
- [ ] **Arbitrage Detection**: Finds arbitrage opportunities in sample data
- [ ] **Stale Line Detection**: Identifies outdated data
- [ ] **Outlier Detection**: Finds anomalous odds
- [ ] **Value Edge Detection**: Identifies value opportunities
- [ ] **Market Efficiency**: Analyzes sportsbook efficiency
- [ ] **Consensus Calculations**: Computes consensus correctly

## Core Engine Tests
- [ ] **American Odds Math**: All calculations work with American odds
- [ ] **Implied Probability**: Calculations accurate for American odds
- [ ] **Vig Calculations**: Works for 2-way and 3-way markets
- [ ] **Consensus Calculations**: Handles multiple sportsbooks
- [ ] **Market Efficiency**: Metrics calculated correctly
- [ ] **CR_ Compliance**: All variables use CR_ prefix

## Integration Tests
- [ ] **End-to-End Pipeline**: Complete pipeline works with Betstamp data
- [ ] **Tools Integration**: All tools work with new data structures
- [ ] **Agent Integration**: Agent processes Betstamp data correctly
- [ ] **Reporting Integration**: Briefings generated correctly
- [ ] **Chat Integration**: Q&A works with Betstamp data
- [ ] **Output Validation**: All outputs are correct format

---

# ✅ PHASE COMPLETION VERIFICATION

## Requirements Alignment
- [ ] **Functional Requirements**: All Betstamp requirements met
- [ ] **Technical Requirements**: All technical specifications met
- [ ] **Data Format Requirements**: Betstamp data format fully supported
- [ ] **Detection Requirements**: All detection algorithms working
- [ ] **Output Requirements**: Output formats match requirements
- [ ] **Performance Requirements**: Performance meets expectations

## Codebase Alignment
- [ ] **Data Structures**: All structures match Betstamp format
- [ ] **Data Loading**: Betstamp data loads correctly
- [ ] **Detection Algorithms**: All algorithms work with Betstamp data
- [ ] **Core Engine**: All calculations work with American odds
- [ ] **Tools and Agent**: All components work with new data
- [ ] **References**: All old sample data references removed

## Quality Assurance
- [ ] **Functionality**: All functionality works correctly
- [ ] **CR_ Compliance**: 100% CR_ prefix compliance maintained
- [ ] **Data Integrity**: Data integrity maintained throughout
- [ ] **Error Handling**: Robust error handling for Betstamp data
- [ ] **Performance**: No performance regression
- [ ] **Testing**: Comprehensive test coverage

## Documentation Updates
- [ ] **Data Structure Documentation**: Updated for Betstamp format
- [ ] **API Documentation**: Updated for new data structures
- [ ] **Usage Documentation**: Updated for Betstamp data
- [ ] **Examples**: Updated examples with Betstamp data
- [ ] **Troubleshooting**: Updated for Betstamp issues
- [ ] **Migration Guide**: Document changes from old format

---

# 🚀 PHASE EXIT CRITERIA

## Mandatory Requirements (ALL must be satisfied)
- [ ] ✅ **Requirements Analysis**: Complete understanding of Betstamp requirements
- [ ] ✅ **Data Structure Alignment**: All structures match Betstamp format
- [ ] ✅ **Data Loading**: Betstamp sample data loads successfully
- [ ] ✅ **Detection Algorithms**: All algorithms work with Betstamp data
- [ ] ✅ **Build Success**: All builds pass without errors
- [ ] ✅ **Test Success**: All tests pass with Betstamp data

## Quality Gates
- [ ] **Functionality**: All required functionality implemented
- [ ] **Performance**: Performance meets requirements
- [ ] **CR_ Compliance**: 100% CR_ prefix compliance
- [ ] **Data Quality**: Data quality maintained
- [ ] **Error Handling**: Robust error handling implemented

## Stakeholder Approval
- [ ] **Technical Lead**: Technical alignment approved
- [ ] **Product Owner**: Requirements alignment approved
- [ ] **QA Lead**: Testing and quality approved
- [ ] **Project Manager**: Phase deliverables approved

---

# 📊 PROGRESS TRACKING

## Completion Metrics
- **Requirements Analysis**: [ ] / [ ] requirements analyzed
- **Gap Identification**: [ ] / [ ] gaps identified
- **Data Structure Updates**: [ ] / [ ] structures updated
- **Algorithm Updates**: [ ] / [ ] algorithms updated
- **Test Creation**: [ ] / [ ] tests created

## Quality Metrics
- **Requirements Coverage**: [ ]% coverage achieved
- **Test Coverage**: [ ]% coverage achieved
- **Build Success Rate**: [ ]% success rate
- **CR_ Compliance**: [ ]% compliance achieved
- **Performance Score**: [ ]% performance score

## Risk Status
- **Requirements Risks**: [Low/Medium/High]
- **Technical Risks**: [Low/Medium/High]
- **Schedule Risks**: [Low/Medium/High]
- **Quality Risks**: [Low/Medium/High]

---

# 🔄 NEXT PHASE DEPENDENCIES

## Prerequisites for Phase 0
- [ ] Phase PRE-0 fully completed and approved
- [ ] All Betstamp requirements understood and addressed
- [ ] All data structures aligned with Betstamp format
- [ ] All detection algorithms working with Betstamp data
- [ ] All tests passing with Betstamp data
- [ ] Documentation updated for Betstamp alignment

## Handoff Requirements
- [ ] Requirements analysis documentation delivered
- [ ] Data structure mapping documentation delivered
- [ ] Updated codebase with Betstamp alignment
- [ ] Test results and reports delivered
- [ ] Updated documentation delivered
- [ ] Risk assessment and mitigation plan

---

# 📝 NOTES AND CHANGES

## Key Changes Required
1. **Data File Reference**: Change from `data/sample_data.json` to `data/Betstamp AI Odds Agent - sample_odds_data.json`
2. **Data Structure**: Align with Betstamp JSON structure (game_id, sport, home_team, away_team, commence_time, sportsbook, markets, last_updated)
3. **Market Types**: Support 3 market types (spread, moneyline, total) with specific field structures
4. **American Odds**: Ensure all calculations work with American odds format
5. **Sportsbook Count**: Support 8 sportsbooks instead of generic structure
6. **Detection Focus**: Align detection algorithms with seeded anomalies in sample data

## Critical Success Factors
- **Data Compatibility**: Ensure seamless loading of Betstamp data
- **Algorithm Accuracy**: Detection algorithms must find seeded anomalies
- **Performance**: Maintain performance with new data structure
- **CR_ Compliance**: Maintain 100% CR_ prefix compliance
- **Documentation**: Clear documentation of changes and mappings

---

**Phase PRE-0 completion is mandatory before proceeding to Phase 0: Preparation.**

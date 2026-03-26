#!/usr/bin/env python3
"""
Betstamp AI Odds Agent Alignment Validation Script
Validates that the codebase is properly aligned with Betstamp requirements
"""

import sys
import os
import time
from datetime import datetime

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages'))

def test_data_loading():
    """Test data loading with Betstamp format"""
    print("🔍 Testing data loading...")

    from data.loader import load_data

    try:
        snapshot = load_data()
        assert len(snapshot.events) == 10, f"Expected 10 events, got {len(snapshot.events)}"
        assert snapshot.events[0].sport == "NBA", f"Expected NBA sport, got {snapshot.events[0].sport}"
        print("✅ Data loading: PASSED")
        return True, snapshot
    except Exception as e:
        print(f"❌ Data loading: FAILED - {e}")
        return False, None

def test_american_odds():
    """Test American odds calculations"""
    print("🔍 Testing American odds calculations...")

    from core_engine.odds_math import compute_implied_probability, compute_vig

    try:
        # Test positive American odds
        prob_pos = compute_implied_probability(196)
        expected_pos = 100.0 / (196 + 100)
        assert abs(prob_pos - expected_pos) < 0.001, f"Positive odds calculation failed"

        # Test negative American odds
        prob_neg = compute_implied_probability(-228)
        expected_neg = abs(-228) / (abs(-228) + 100)
        assert abs(prob_neg - expected_neg) < 0.001, f"Negative odds calculation failed"

        # Test vig calculation
        vig = compute_vig([-111, -111])
        assert vig > 0, "Vig calculation failed"

        print("✅ American odds: PASSED")
        return True
    except Exception as e:
        print(f"❌ American odds: FAILED - {e}")
        return False

def test_detection_algorithms(snapshot):
    """Test detection algorithms with Betstamp data"""
    print("🔍 Testing detection algorithms...")

    from core_engine.detectors import detect_arbitrage, detect_stale_lines, detect_outliers, detect_value_edges

    try:
        # Test arbitrage detection
        arbitrages = detect_arbitrage(snapshot.events)
        assert len(arbitrages) > 0, "No arbitrages found"
        assert all(arb.type == 'arbitrage' for arb in arbitrages), "Invalid arbitrage types"

        # Test other detections
        stale_lines = detect_stale_lines(snapshot.events)
        outliers = detect_outliers(snapshot.events)
        value_edges = detect_value_edges(snapshot.events)

        assert isinstance(stale_lines, list), "Stale lines not a list"
        assert isinstance(outliers, list), "Outliers not a list"
        assert isinstance(value_edges, list), "Value edges not a list"

        print(f"✅ Detection algorithms: PASSED (arbitrages: {len(arbitrages)}, outliers: {len(outliers)}, value edges: {len(value_edges)})")
        return True
    except Exception as e:
        print(f"❌ Detection algorithms: FAILED - {e}")
        return False

def test_agent_orchestration(snapshot):
    """Test agent orchestration"""
    print("🔍 Testing agent orchestration...")

    from agent.agent import run_agent

    try:
        findings = run_agent(snapshot)
        assert isinstance(findings, list), "Findings not a list"
        assert len(findings) > 0, "No findings generated"

        # Check finding types
        finding_types = {finding.type for finding in findings}
        expected_types = {'arbitrage', 'value_edge', 'outlier'}
        assert finding_types.intersection(expected_types), "Missing expected finding types"

        print(f"✅ Agent orchestration: PASSED ({len(findings)} findings)")
        return True, findings
    except Exception as e:
        print(f"❌ Agent orchestration: FAILED - {e}")
        return False, None

def test_briefing_generation(findings, snapshot):
    """Test briefing generation"""
    print("🔍 Testing briefing generation...")

    from reporting.briefing import generate_briefing

    try:
        briefing = generate_briefing(findings, snapshot)
        assert isinstance(briefing, str), "Briefing not a string"
        assert len(briefing) > 0, "Empty briefing"
        assert "ODDS ANALYSIS BRIEFING" in briefing, "Briefing header missing"

        print(f"✅ Briefing generation: PASSED ({len(briefing)} chars)")
        return True
    except Exception as e:
        print(f"❌ Briefing generation: FAILED - {e}")
        return False

def test_sportsbook_coverage(snapshot):
    """Test sportsbook coverage"""
    print("🔍 Testing sportsbook coverage...")

    expected_sportsbooks = {
        'DraftKings', 'FanDuel', 'BetMGM', 'Caesars',
        'PointsBet', 'bet365', 'Pinnacle', 'BetRivers'
    }

    try:
        found_sportsbooks = set()
        for event in snapshot.events:
            for market in event.markets:
                found_sportsbooks.add(market.bookmaker)

        assert found_sportsbooks == expected_sportsbooks, f"Missing sportsbooks: {expected_sportsbooks - found_sportsbooks}"

        print(f"✅ Sportsbook coverage: PASSED ({len(found_sportsbooks)} sportsbooks)")
        return True
    except Exception as e:
        print(f"❌ Sportsbook coverage: FAILED - {e}")
        return False

def test_market_types(snapshot):
    """Test market types"""
    print("🔍 Testing market types...")

    expected_market_types = {'spread', 'moneyline', 'total'}

    try:
        found_market_types = set()
        for event in snapshot.events:
            for market in event.markets:
                found_market_types.add(market.name)

        assert found_market_types == expected_market_types, f"Missing market types: {expected_market_types - found_market_types}"

        print(f"✅ Market types: PASSED ({len(found_market_types)} types)")
        return True
    except Exception as e:
        print(f"❌ Market types: FAILED - {e}")
        return False

def test_performance(snapshot):
    """Test performance requirements"""
    print("🔍 Testing performance...")

    try:
        # Test data loading performance
        start_time = time.time()
        from data.loader import load_data
        test_snapshot = load_data()
        load_time = time.time() - start_time

        assert load_time < 1.0, f"Data loading too slow: {load_time:.2f}s"

        # Test detection performance
        start_time = time.time()
        from core_engine.detectors import detect_arbitrage
        arbitrages = detect_arbitrage(test_snapshot.events)
        detection_time = time.time() - start_time

        assert detection_time < 2.0, f"Detection too slow: {detection_time:.2f}s"

        print(f"✅ Performance: PASSED (load: {load_time:.3f}s, detect: {detection_time:.3f}s)")
        return True
    except Exception as e:
        print(f"❌ Performance: FAILED - {e}")
        return False

def test_cr_compliance():
    """Test CR_ prefix compliance"""
    print("🔍 Testing CR_ compliance...")

    try:
        from data.contracts import CR_snapshot, CR_event, CR_market, CR_outcome, CR_finding

        # Check class names
        assert CR_snapshot.__name__.startswith('CR_'), "CR_snapshot not CR_ compliant"
        assert CR_event.__name__.startswith('CR_'), "CR_event not CR_ compliant"
        assert CR_market.__name__.startswith('CR_'), "CR_market not CR_ compliant"
        assert CR_outcome.__name__.startswith('CR_'), "CR_outcome not CR_ compliant"
        assert CR_finding.__name__.startswith('CR_'), "CR_finding not CR_ compliant"

        print("✅ CR_ compliance: PASSED")
        return True
    except Exception as e:
        print(f"❌ CR_ compliance: FAILED - {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Betstamp AI Odds Agent Alignment Validation")
    print("=" * 50)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    results = []

    # Run all tests
    success, snapshot = test_data_loading()
    results.append(success)

    if success:
        results.append(test_american_odds())
        results.append(test_detection_algorithms(snapshot))
        results.append(test_sportsbook_coverage(snapshot))
        results.append(test_market_types(snapshot))
        results.append(test_performance(snapshot))
        results.append(test_cr_compliance())

        success, findings = test_agent_orchestration(snapshot)
        results.append(success)

        if success:
            results.append(test_briefing_generation(findings, snapshot))

    # Summary
    print()
    print("=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Betstamp alignment complete!")
        print("✅ Ready for Phase 0: Preparation")
        return 0
    else:
        print("❌ Some tests failed - fix issues before proceeding")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

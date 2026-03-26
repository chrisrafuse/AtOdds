#!/usr/bin/env python3
"""
Test Suite for Phase 3: CR Signature Migration - Tools and Agent
Tests for tools registry and agent orchestration with CR_ prefix compliance
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.tools.registry import (
    tool_CR_compute_implied_probability,
    tool_CR_compute_vig,
    tool_CR_convert_odds,
    tool_CR_detect_arbitrage,
    tool_CR_detect_stale_lines,
    tool_CR_detect_outliers,
    tool_CR_detect_value_edges,
    tool_CR_compute_best_lines,
    tool_CR_compute_consensus,
    tool_CR_compute_market_efficiency,
    get_CR_tool,
    list_CR_tools,
    CR_TOOL_REGISTRY
)

from packages.agent.agent import (
    run_CR_agent,
    analyze_CR_snapshot,
    generate_CR_analysis_summary,
    execute_CR_analysis_pipeline
)

from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_snapshot
)


class TestToolsRegistry(unittest.TestCase):
    """Test tools registry with CR_ prefix"""

    def test_tool_registry_exists(self):
        """Test that CR_TOOL_REGISTRY exists and has tools"""
        self.assertIsNotNone(CR_TOOL_REGISTRY)
        self.assertGreater(len(CR_TOOL_REGISTRY), 0)

    def test_list_tools(self):
        """Test listing all available tools"""
        CR_tools = list_CR_tools()
        self.assertIsInstance(CR_tools, list)
        self.assertEqual(len(CR_tools), 10)
        self.assertIn('CR_compute_implied_probability', CR_tools)
        self.assertIn('CR_detect_arbitrage', CR_tools)

    def test_get_tool(self):
        """Test getting a tool by name"""
        CR_tool = get_CR_tool('CR_compute_implied_probability')
        self.assertIsNotNone(CR_tool)
        self.assertTrue(callable(CR_tool))

    def test_get_nonexistent_tool(self):
        """Test getting a nonexistent tool returns None"""
        CR_tool = get_CR_tool('nonexistent_tool')
        self.assertIsNone(CR_tool)

    def test_tool_compute_implied_probability(self):
        """Test implied probability tool"""
        CR_result = tool_CR_compute_implied_probability(-110)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertIn('CR_timestamp', CR_result)
        self.assertAlmostEqual(CR_result['CR_result'], 0.524, places=2)

    def test_tool_compute_vig(self):
        """Test vig calculation tool"""
        CR_result = tool_CR_compute_vig([-110, -110])

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertGreater(CR_result['CR_result'], 0.0)

    def test_tool_convert_odds_american_to_decimal(self):
        """Test odds conversion tool - American to decimal"""
        CR_result = tool_CR_convert_odds(150, 'american', 'decimal')

        self.assertTrue(CR_result['CR_success'])
        self.assertAlmostEqual(CR_result['CR_result'], 2.5, places=2)

    def test_tool_convert_odds_decimal_to_american(self):
        """Test odds conversion tool - decimal to American"""
        CR_result = tool_CR_convert_odds(2.5, 'decimal', 'american')

        self.assertTrue(CR_result['CR_success'])
        self.assertEqual(CR_result['CR_result'], 150)

    def test_tool_convert_odds_invalid_format(self):
        """Test odds conversion with invalid format"""
        CR_result = tool_CR_convert_odds(150, 'invalid', 'decimal')

        self.assertFalse(CR_result['CR_success'])
        self.assertIn('CR_error', CR_result)

    def test_tool_detect_arbitrage(self):
        """Test arbitrage detection tool"""
        # Create test snapshot with arbitrage opportunity
        CR_outcome1_dk = create_CR_outcome("Lakers", 150)
        CR_outcome2_dk = create_CR_outcome("Warriors", -110)
        CR_market_dk = create_CR_market("moneyline", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")

        CR_outcome1_fd = create_CR_outcome("Lakers", -105)
        CR_outcome2_fd = create_CR_outcome("Warriors", 200)
        CR_market_fd = create_CR_market("moneyline", [CR_outcome1_fd, CR_outcome2_fd], "FanDuel")

        CR_event = create_CR_event(
            CR_event_id="test_arb",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_dk, CR_market_fd]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        CR_result = tool_CR_detect_arbitrage(CR_snapshot)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertIn('CR_count', CR_result)
        self.assertGreater(CR_result['CR_count'], 0)

    def test_tool_detect_value_edges(self):
        """Test value edge detection tool"""
        CR_outcome1_a = create_CR_outcome("Lakers", -110)
        CR_outcome2_a = create_CR_outcome("Warriors", -110)
        CR_market_a = create_CR_market("moneyline", [CR_outcome1_a, CR_outcome2_a], "BookA")

        CR_outcome1_b = create_CR_outcome("Lakers", 150)
        CR_outcome2_b = create_CR_outcome("Warriors", -110)
        CR_market_b = create_CR_market("moneyline", [CR_outcome1_b, CR_outcome2_b], "BookB")

        CR_event = create_CR_event(
            CR_event_id="test_value",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_a, CR_market_b]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        CR_result = tool_CR_detect_value_edges(CR_snapshot, CR_edge_threshold=0.05)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertIn('CR_count', CR_result)

    def test_tool_compute_best_lines(self):
        """Test best lines computation tool"""
        CR_outcome1_dk = create_CR_outcome("Lakers +5.5", -110)
        CR_outcome2_dk = create_CR_outcome("Warriors -5.5", -110)
        CR_market_dk = create_CR_market("spread", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")

        CR_outcome1_fd = create_CR_outcome("Lakers +5.5", -105)
        CR_outcome2_fd = create_CR_outcome("Warriors -5.5", -115)
        CR_market_fd = create_CR_market("spread", [CR_outcome1_fd, CR_outcome2_fd], "FanDuel")

        CR_event = create_CR_event(
            CR_event_id="test_best",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_dk, CR_market_fd]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        CR_result = tool_CR_compute_best_lines(CR_snapshot)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertIn('test_best', CR_result['CR_result'])

    def test_tool_compute_consensus(self):
        """Test consensus computation tool"""
        CR_outcome1_dk = create_CR_outcome("Lakers", -110)
        CR_outcome2_dk = create_CR_outcome("Warriors", -110)
        CR_market_dk = create_CR_market("moneyline", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")

        CR_outcome1_fd = create_CR_outcome("Lakers", -105)
        CR_outcome2_fd = create_CR_outcome("Warriors", -115)
        CR_market_fd = create_CR_market("moneyline", [CR_outcome1_fd, CR_outcome2_fd], "FanDuel")

        CR_event = create_CR_event(
            CR_event_id="test_consensus",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_dk, CR_market_fd]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        CR_result = tool_CR_compute_consensus(CR_snapshot)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)
        self.assertIn('test_consensus', CR_result['CR_result'])

    def test_tool_compute_market_efficiency(self):
        """Test market efficiency computation tool"""
        CR_outcome1_dk = create_CR_outcome("Lakers", -110)
        CR_outcome2_dk = create_CR_outcome("Warriors", -110)
        CR_market_dk = create_CR_market("moneyline", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")

        CR_event = create_CR_event(
            CR_event_id="test_efficiency",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_dk]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        CR_result = tool_CR_compute_market_efficiency(CR_snapshot)

        self.assertTrue(CR_result['CR_success'])
        self.assertIn('CR_result', CR_result)


class TestAgentOrchestration(unittest.TestCase):
    """Test agent orchestration with CR_ prefix"""

    def setUp(self):
        """Set up test fixtures"""
        # Create comprehensive test snapshot
        CR_outcome1_dk = create_CR_outcome("Lakers +5.5", -110)
        CR_outcome2_dk = create_CR_outcome("Warriors -5.5", -110)
        CR_market_dk = create_CR_market("spread", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")

        CR_outcome1_fd = create_CR_outcome("Lakers +5.5", -105)
        CR_outcome2_fd = create_CR_outcome("Warriors -5.5", -115)
        CR_market_fd = create_CR_market("spread", [CR_outcome1_fd, CR_outcome2_fd], "FanDuel")

        self.CR_event = create_CR_event(
            CR_event_id="game_1",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_dk, CR_market_fd],
            CR_home_team="Warriors",
            CR_away_team="Lakers"
        )

        from datetime import datetime
        self.CR_snapshot = create_CR_snapshot([self.CR_event], datetime.now().isoformat(), "test")

    def test_analyze_snapshot(self):
        """Test snapshot analysis"""
        CR_analysis = analyze_CR_snapshot(self.CR_snapshot)

        self.assertIn('CR_total_events', CR_analysis)
        self.assertIn('CR_total_markets', CR_analysis)
        self.assertIn('CR_total_outcomes', CR_analysis)
        self.assertIn('CR_unique_bookmakers', CR_analysis)
        self.assertIn('CR_bookmaker_list', CR_analysis)

        self.assertEqual(CR_analysis['CR_total_events'], 1)
        self.assertEqual(CR_analysis['CR_total_markets'], 2)
        self.assertEqual(CR_analysis['CR_total_outcomes'], 4)
        self.assertEqual(CR_analysis['CR_unique_bookmakers'], 2)

    def test_generate_analysis_summary(self):
        """Test findings summary generation"""
        from packages.data.contracts import create_CR_finding

        CR_finding1 = create_CR_finding(
            CR_type='arbitrage',
            CR_description='Test arbitrage',
            CR_confidence=0.9,
            CR_event_id='game_1',
            CR_market_name='moneyline',
            CR_bookmakers=['DraftKings', 'FanDuel'],
            CR_details={'CR_profit_margin': 0.05}
        )

        CR_finding2 = create_CR_finding(
            CR_type='value_edge',
            CR_description='Test value edge',
            CR_confidence=0.7,
            CR_event_id='game_1',
            CR_market_name='spread',
            CR_bookmakers=['DraftKings'],
            CR_details={'CR_edge': 0.08}
        )

        CR_findings = [CR_finding1, CR_finding2]
        CR_summary = generate_CR_analysis_summary(CR_findings)

        self.assertEqual(CR_summary['CR_total_findings'], 2)
        self.assertIn('CR_by_type', CR_summary)
        self.assertIn('CR_by_confidence', CR_summary)
        self.assertIn('CR_by_bookmaker', CR_summary)
        self.assertIn('CR_by_event', CR_summary)

        self.assertEqual(CR_summary['CR_by_type']['arbitrage'], 1)
        self.assertEqual(CR_summary['CR_by_type']['value_edge'], 1)
        self.assertEqual(CR_summary['CR_by_confidence']['CR_high'], 1)
        self.assertEqual(CR_summary['CR_by_confidence']['CR_medium'], 1)

    def test_run_agent(self):
        """Test agent orchestration"""
        CR_findings = run_CR_agent(self.CR_snapshot)

        self.assertIsInstance(CR_findings, list)
        # Findings are sorted by confidence
        for i in range(len(CR_findings) - 1):
            self.assertGreaterEqual(
                CR_findings[i].get('CR_confidence', 0),
                CR_findings[i + 1].get('CR_confidence', 0)
            )

    def test_execute_analysis_pipeline(self):
        """Test complete analysis pipeline"""
        CR_results = execute_CR_analysis_pipeline(self.CR_snapshot)

        self.assertIn('CR_snapshot_analysis', CR_results)
        self.assertIn('CR_findings', CR_results)
        self.assertIn('CR_findings_summary', CR_results)
        self.assertIn('CR_pipeline_timestamp', CR_results)

        # Verify snapshot analysis
        CR_snapshot_analysis = CR_results['CR_snapshot_analysis']
        self.assertEqual(CR_snapshot_analysis['CR_total_events'], 1)

        # Verify findings
        CR_findings = CR_results['CR_findings']
        self.assertIsInstance(CR_findings, list)

        # Verify summary
        CR_summary = CR_results['CR_findings_summary']
        self.assertIn('CR_total_findings', CR_summary)


class TestIntegration(unittest.TestCase):
    """Integration tests for tools and agent"""

    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        # Create test data
        CR_markets = []

        for CR_book in ['DraftKings', 'FanDuel', 'MGM']:
            CR_outcome1 = create_CR_outcome("Lakers +5.5", -110)
            CR_outcome2 = create_CR_outcome("Warriors -5.5", -110)
            CR_market = create_CR_market("spread", [CR_outcome1, CR_outcome2], CR_book)
            CR_markets.append(CR_market)

        CR_event = create_CR_event(
            CR_event_id="integration_test",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=CR_markets,
            CR_home_team="Warriors",
            CR_away_team="Lakers"
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")

        # Run complete pipeline
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)

        # Verify all components work together
        self.assertIsNotNone(CR_results)
        self.assertIn('CR_snapshot_analysis', CR_results)
        self.assertIn('CR_findings', CR_results)
        self.assertIn('CR_findings_summary', CR_results)

        # Verify snapshot analysis is correct
        CR_analysis = CR_results['CR_snapshot_analysis']
        self.assertEqual(CR_analysis['CR_total_events'], 1)
        self.assertEqual(CR_analysis['CR_total_markets'], 3)
        self.assertEqual(CR_analysis['CR_unique_bookmakers'], 3)

    def test_tools_work_with_agent(self):
        """Test that all tools work correctly when called by agent"""
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")

        CR_event = create_CR_event(
            CR_event_id="tools_test",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market]
        )

        from datetime import datetime
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")

        # Run agent (which calls all detection tools)
        CR_findings = run_CR_agent(CR_snapshot)

        # Agent should complete without errors
        self.assertIsInstance(CR_findings, list)

        # All findings should have CR_ prefix in keys
        for CR_finding in CR_findings:
            self.assertIn('CR_type', CR_finding)
            self.assertIn('CR_confidence', CR_finding)
            self.assertIn('CR_event_id', CR_finding)


def run_tests():
    """Run all tests and generate report"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

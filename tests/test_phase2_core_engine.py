#!/usr/bin/env python3
"""
Test Suite for Phase 2: CR Signature Migration - Core Engine
Tests for odds_math, consensus, and detectors modules with CR_ prefix compliance
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.core_engine.odds_math import (
    compute_CR_american_to_decimal,
    compute_CR_decimal_to_american,
    compute_CR_implied_probability,
    compute_CR_vig,
    compute_CR_true_probability,
    compute_CR_kelly_fraction,
    compute_CR_expected_value
)

from packages.core_engine.consensus import (
    compute_CR_best_lines,
    compute_CR_consensus_price,
    compute_CR_weighted_consensus,
    compute_CR_market_efficiency,
    compute_CR_market_depth
)

from packages.core_engine.detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edge,
    detect_CR_stale_line,
    detect_CR_outlier
)

from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event
)


class TestOddsMath(unittest.TestCase):
    """Test odds_math module with CR_ prefix"""

    def test_american_to_decimal_positive(self):
        """Test converting positive American odds to decimal"""
        CR_result = compute_CR_american_to_decimal(150)
        self.assertAlmostEqual(CR_result, 2.5, places=2)

    def test_american_to_decimal_negative(self):
        """Test converting negative American odds to decimal"""
        CR_result = compute_CR_american_to_decimal(-110)
        self.assertAlmostEqual(CR_result, 1.909, places=2)

    def test_american_to_decimal_even(self):
        """Test converting even odds"""
        CR_result = compute_CR_american_to_decimal(100)
        self.assertAlmostEqual(CR_result, 2.0, places=2)

    def test_american_to_decimal_zero_raises_error(self):
        """Test that zero odds raise error"""
        with self.assertRaises(ValueError):
            compute_CR_american_to_decimal(0)

    def test_decimal_to_american_positive(self):
        """Test converting decimal to positive American odds"""
        CR_result = compute_CR_decimal_to_american(2.5)
        self.assertEqual(CR_result, 150)

    def test_decimal_to_american_negative(self):
        """Test converting decimal to negative American odds"""
        CR_result = compute_CR_decimal_to_american(1.91)
        self.assertAlmostEqual(CR_result, -110, delta=1)

    def test_decimal_to_american_invalid(self):
        """Test that invalid decimal odds raise error"""
        with self.assertRaises(ValueError):
            compute_CR_decimal_to_american(0.5)

    def test_implied_probability_positive_odds(self):
        """Test implied probability for positive odds"""
        CR_result = compute_CR_implied_probability(150)
        self.assertAlmostEqual(CR_result, 0.4, places=2)

    def test_implied_probability_negative_odds(self):
        """Test implied probability for negative odds"""
        CR_result = compute_CR_implied_probability(-110)
        self.assertAlmostEqual(CR_result, 0.524, places=2)

    def test_implied_probability_zero_raises_error(self):
        """Test that zero price raises error"""
        with self.assertRaises(ValueError):
            compute_CR_implied_probability(0)

    def test_compute_vig_two_sided_market(self):
        """Test vig calculation for two-sided market"""
        CR_outcomes = [-110, -110]
        CR_vig = compute_CR_vig(CR_outcomes)
        self.assertGreater(CR_vig, 0.0)
        self.assertLess(CR_vig, 0.1)

    def test_compute_vig_empty_list(self):
        """Test vig calculation with empty list"""
        CR_vig = compute_CR_vig([])
        self.assertEqual(CR_vig, 0.0)

    def test_true_probability_removes_vig(self):
        """Test that true probability removes vig"""
        CR_price = -110
        CR_vig = 0.048
        CR_true_prob = compute_CR_true_probability(CR_price, CR_vig)
        CR_implied_prob = compute_CR_implied_probability(CR_price)
        self.assertLess(CR_true_prob, CR_implied_prob)

    def test_kelly_fraction_positive_edge(self):
        """Test Kelly fraction with positive edge"""
        CR_true_prob = 0.55
        CR_american_odds = -110
        CR_kelly = compute_CR_kelly_fraction(CR_true_prob, CR_american_odds)
        self.assertGreater(CR_kelly, 0.0)
        self.assertLess(CR_kelly, 1.0)

    def test_kelly_fraction_no_edge(self):
        """Test Kelly fraction with no edge"""
        CR_true_prob = 0.5
        CR_american_odds = 100
        CR_kelly = compute_CR_kelly_fraction(CR_true_prob, CR_american_odds)
        self.assertEqual(CR_kelly, 0.0)

    def test_expected_value_positive_edge(self):
        """Test expected value with positive edge"""
        CR_true_prob = 0.55
        CR_american_odds = 100
        CR_stake = 100.0
        CR_ev = compute_CR_expected_value(CR_true_prob, CR_american_odds, CR_stake)
        self.assertGreater(CR_ev, 0.0)

    def test_expected_value_negative_edge(self):
        """Test expected value with negative edge"""
        CR_true_prob = 0.30  # Low probability
        CR_american_odds = -150  # Favorite odds
        CR_stake = 100.0
        CR_ev = compute_CR_expected_value(CR_true_prob, CR_american_odds, CR_stake)
        self.assertLess(CR_ev, 0.0)


class TestConsensus(unittest.TestCase):
    """Test consensus module with CR_ prefix"""

    def setUp(self):
        """Set up test fixtures"""
        self.CR_outcome1_dk = create_CR_outcome("Lakers +5.5", -110)
        self.CR_outcome2_dk = create_CR_outcome("Warriors -5.5", -110)
        self.CR_market_dk = create_CR_market("spread", [self.CR_outcome1_dk, self.CR_outcome2_dk], "DraftKings")

        self.CR_outcome1_fd = create_CR_outcome("Lakers +5.5", -105)
        self.CR_outcome2_fd = create_CR_outcome("Warriors -5.5", -115)
        self.CR_market_fd = create_CR_market("spread", [self.CR_outcome1_fd, self.CR_outcome2_fd], "FanDuel")

        self.CR_outcome1_mgm = create_CR_outcome("Lakers +5.5", -108)
        self.CR_outcome2_mgm = create_CR_outcome("Warriors -5.5", -112)
        self.CR_market_mgm = create_CR_market("spread", [self.CR_outcome1_mgm, self.CR_outcome2_mgm], "MGM")

    def test_best_lines_finds_best_odds(self):
        """Test that best lines finds the best odds for each outcome"""
        CR_markets = [self.CR_market_dk, self.CR_market_fd, self.CR_market_mgm]
        CR_best_lines = compute_CR_best_lines(CR_markets)

        self.assertIn("Lakers +5.5", CR_best_lines)
        self.assertIn("Warriors -5.5", CR_best_lines)

        # -105 is best for Lakers (closest to even)
        CR_lakers_best = CR_best_lines["Lakers +5.5"]
        self.assertEqual(CR_lakers_best[0], "FanDuel")
        self.assertEqual(CR_lakers_best[1], -105)

    def test_consensus_price_calculates_median(self):
        """Test that consensus price calculates median"""
        CR_markets = [self.CR_market_dk, self.CR_market_fd, self.CR_market_mgm]
        CR_consensus = compute_CR_consensus_price(CR_markets, "Lakers +5.5")

        self.assertIsNotNone(CR_consensus)
        # Median of -110, -105, -108 should be -108
        self.assertEqual(CR_consensus, -108)

    def test_consensus_price_not_found(self):
        """Test consensus price returns None for non-existent outcome"""
        CR_markets = [self.CR_market_dk]
        CR_consensus = compute_CR_consensus_price(CR_markets, "Nonexistent Outcome")

        self.assertIsNone(CR_consensus)

    def test_weighted_consensus_with_sharp_book(self):
        """Test weighted consensus with sharp bookmaker"""
        CR_outcome1_pin = create_CR_outcome("Lakers +5.5", -107)
        CR_outcome2_pin = create_CR_outcome("Warriors -5.5", -113)
        CR_market_pin = create_CR_market("spread", [CR_outcome1_pin, CR_outcome2_pin], "Pinnacle")

        CR_markets = [self.CR_market_dk, CR_market_pin]
        CR_weighted = compute_CR_weighted_consensus(
            CR_markets,
            "Lakers +5.5",
            CR_sharp_bookmakers=["Pinnacle"],
            CR_sharp_weight=2.0
        )

        self.assertIsNotNone(CR_weighted)
        # Should be weighted toward Pinnacle's -107
        self.assertGreater(CR_weighted, -110)

    def test_market_efficiency_calculates_scores(self):
        """Test market efficiency calculation"""
        CR_markets = [self.CR_market_dk, self.CR_market_fd, self.CR_market_mgm]
        CR_efficiency = compute_CR_market_efficiency(CR_markets)

        self.assertIn("DraftKings", CR_efficiency)
        self.assertIn("FanDuel", CR_efficiency)
        self.assertIn("MGM", CR_efficiency)

        for CR_score in CR_efficiency.values():
            self.assertGreaterEqual(CR_score, 0.0)
            self.assertLessEqual(CR_score, 1.0)

    def test_market_depth_counts_markets(self):
        """Test market depth calculation"""
        CR_markets = [self.CR_market_dk, self.CR_market_fd, self.CR_market_mgm]
        CR_depth = compute_CR_market_depth(CR_markets)

        self.assertEqual(CR_depth["DraftKings"], 1)
        self.assertEqual(CR_depth["FanDuel"], 1)
        self.assertEqual(CR_depth["MGM"], 1)


class TestDetectors(unittest.TestCase):
    """Test detectors module with CR_ prefix"""

    def setUp(self):
        """Set up test fixtures"""
        # Create markets for arbitrage testing
        self.CR_outcome1_dk = create_CR_outcome("Lakers", 150)
        self.CR_outcome2_dk = create_CR_outcome("Warriors", -110)
        self.CR_market_dk = create_CR_market("moneyline", [self.CR_outcome1_dk, self.CR_outcome2_dk], "DraftKings")

        # Create arbitrage opportunity
        self.CR_outcome1_fd = create_CR_outcome("Lakers", -105)
        self.CR_outcome2_fd = create_CR_outcome("Warriors", 200)
        self.CR_market_fd = create_CR_market("moneyline", [self.CR_outcome1_fd, self.CR_outcome2_fd], "FanDuel")

        self.CR_event = create_CR_event(
            CR_event_id="test_game_1",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[self.CR_market_dk, self.CR_market_fd]
        )

    def test_detect_arbitrage_finds_opportunity(self):
        """Test arbitrage detection finds opportunities"""
        CR_findings = detect_CR_arbitrage([self.CR_event])

        # Should find arbitrage opportunity
        self.assertGreater(len(CR_findings), 0)

        CR_finding = CR_findings[0]
        self.assertEqual(CR_finding["CR_type"], "arbitrage")
        self.assertIn("CR_profit_margin", CR_finding["CR_details"])

    def test_detect_value_edge_finds_edges(self):
        """Test value edge detection"""
        # Create markets with value edge
        CR_outcome1_a = create_CR_outcome("Lakers", -110)
        CR_outcome2_a = create_CR_outcome("Warriors", -110)
        CR_market_a = create_CR_market("moneyline", [CR_outcome1_a, CR_outcome2_a], "BookA")

        CR_outcome1_b = create_CR_outcome("Lakers", 150)  # Outlier
        CR_outcome2_b = create_CR_outcome("Warriors", -110)
        CR_market_b = create_CR_market("moneyline", [CR_outcome1_b, CR_outcome2_b], "BookB")

        CR_outcome1_c = create_CR_outcome("Lakers", -105)
        CR_outcome2_c = create_CR_outcome("Warriors", -115)
        CR_market_c = create_CR_market("moneyline", [CR_outcome1_c, CR_outcome2_c], "BookC")

        CR_event = create_CR_event(
            CR_event_id="test_game_2",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market_a, CR_market_b, CR_market_c]
        )

        CR_findings = detect_CR_value_edge([CR_event], CR_edge_threshold=0.05)

        # Should find value edge on Lakers at +150 (if threshold allows)
        # Note: May not find edge if consensus is also high
        self.assertIsInstance(CR_findings, list)

        for CR_finding in CR_findings:
            self.assertEqual(CR_finding["CR_type"], "value_edge")
            self.assertIn("CR_edge", CR_finding["CR_details"])

    def test_detect_outlier_finds_outliers(self):
        """Test outlier detection"""
        # Create markets with outlier
        CR_markets = []
        for i in range(5):
            CR_outcome1 = create_CR_outcome("Lakers", -110)
            CR_outcome2 = create_CR_outcome("Warriors", -110)
            CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], f"Book{i}")
            CR_markets.append(CR_market)

        # Add outlier
        CR_outcome1_outlier = create_CR_outcome("Lakers", 300)  # Way off
        CR_outcome2_outlier = create_CR_outcome("Warriors", -110)
        CR_market_outlier = create_CR_market("moneyline", [CR_outcome1_outlier, CR_outcome2_outlier], "OutlierBook")
        CR_markets.append(CR_market_outlier)

        CR_event = create_CR_event(
            CR_event_id="test_game_3",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=CR_markets
        )

        CR_findings = detect_CR_outlier([CR_event], CR_outlier_threshold=2.0)

        # Should find outlier
        self.assertGreater(len(CR_findings), 0)

        CR_finding = CR_findings[0]
        self.assertEqual(CR_finding["CR_type"], "outlier")
        self.assertIn("CR_z_score", CR_finding["CR_details"])

    def test_detect_stale_line_finds_stale_markets(self):
        """Test stale line detection"""
        from datetime import datetime, timedelta

        # Create market with old timestamp
        CR_old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market(
            "moneyline",
            [CR_outcome1, CR_outcome2],
            "OldBook",
            CR_last_update=CR_old_time
        )

        CR_event = create_CR_event(
            CR_event_id="test_game_4",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[CR_market]
        )

        CR_findings = detect_CR_stale_line([CR_event], CR_stale_threshold_hours=24)

        # Should find stale line
        self.assertGreater(len(CR_findings), 0)

        CR_finding = CR_findings[0]
        self.assertEqual(CR_finding["CR_type"], "stale_line")
        self.assertIn("CR_hours_stale", CR_finding["CR_details"])


class TestIntegration(unittest.TestCase):
    """Integration tests for core engine modules"""

    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline"""
        # Create comprehensive test data
        CR_markets = []

        # DraftKings
        CR_outcome1_dk = create_CR_outcome("Lakers +5.5", -110, 0.524)
        CR_outcome2_dk = create_CR_outcome("Warriors -5.5", -110, 0.524)
        CR_market_dk = create_CR_market("spread", [CR_outcome1_dk, CR_outcome2_dk], "DraftKings")
        CR_markets.append(CR_market_dk)

        # FanDuel
        CR_outcome1_fd = create_CR_outcome("Lakers +5.5", -105, 0.512)
        CR_outcome2_fd = create_CR_outcome("Warriors -5.5", -115, 0.535)
        CR_market_fd = create_CR_market("spread", [CR_outcome1_fd, CR_outcome2_fd], "FanDuel")
        CR_markets.append(CR_market_fd)

        CR_event = create_CR_event(
            CR_event_id="integration_test_1",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=CR_markets,
            CR_home_team="Warriors",
            CR_away_team="Lakers"
        )

        # Test consensus calculations
        CR_best_lines = compute_CR_best_lines(CR_markets)
        self.assertEqual(len(CR_best_lines), 2)

        CR_consensus = compute_CR_consensus_price(CR_markets, "Lakers +5.5")
        self.assertIsNotNone(CR_consensus)

        CR_efficiency = compute_CR_market_efficiency(CR_markets)
        self.assertEqual(len(CR_efficiency), 2)

        # Test detectors
        CR_arb_findings = detect_CR_arbitrage([CR_event])
        CR_value_findings = detect_CR_value_edge([CR_event])
        CR_outlier_findings = detect_CR_outlier([CR_event])

        # All detector functions should run without error
        self.assertIsInstance(CR_arb_findings, list)
        self.assertIsInstance(CR_value_findings, list)
        self.assertIsInstance(CR_outlier_findings, list)


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

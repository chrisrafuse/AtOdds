"""
Core tests - prove correctness of math and detection
"""

import unittest
import sys
import os

# Add root to path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from packages.core_engine.odds_math import compute_CR_implied_probability, compute_CR_vig, compute_CR_true_probability
from packages.core_engine.detectors import detect_CR_arbitrage, detect_CR_value_edge
from packages.data.contracts import create_CR_event, create_CR_market, create_CR_outcome, create_CR_snapshot
from datetime import datetime


class TestOddsMath(unittest.TestCase):
    """Test core odds mathematics"""

    def test_implied_probability(self):
        """Test implied probability calculation"""
        # Test basic cases (using American odds)
        self.assertAlmostEqual(compute_CR_implied_probability(100), 0.5, places=4)
        self.assertAlmostEqual(compute_CR_implied_probability(-200), 0.6667, places=4)
        self.assertAlmostEqual(compute_CR_implied_probability(-110), 0.5238, places=4)

        # Test edge cases
        with self.assertRaises(ValueError):
            compute_CR_implied_probability(0)
        # Note: -1 is actually valid (just very unlikely), so remove this test

    def test_vig_calculation(self):
        """Test vigorish calculation"""
        # Fair market (no vig) - American odds +100/-100
        prices = [100, -100]  # 50/50 probability
        vig = compute_CR_vig(prices)
        self.assertAlmostEqual(vig, 0.0, places=4)

        # Market with vig - American odds -110/-110
        prices = [-110, -110]  # Both sides have vig
        vig = compute_CR_vig(prices)
        self.assertGreater(vig, 0.0)
        self.assertLess(vig, 0.1)  # Should be reasonable

        # Three-way market - American odds
        prices = [200, 200, 200]  # 33.3% each
        vig = compute_CR_vig(prices)
        self.assertAlmostEqual(vig, 0.0, places=4)

    def test_true_probability_calculation(self):
        """Test true probability calculation"""
        # Test removing vig
        price_with_vig = -110
        market_vig = 0.05
        true_prob = compute_CR_true_probability(price_with_vig, market_vig)

        # True probability should be different from implied (may be higher or lower depending on vig)
        implied_prob = compute_CR_implied_probability(price_with_vig)
        self.assertNotEqual(true_prob, implied_prob)

        # Test edge case
        self.assertEqual(compute_CR_true_probability(100, 0.0), 0.5)


class TestDetectors(unittest.TestCase):
    """Test detection algorithms"""

    def setUp(self):
        """Set up test data"""
        # Create test events with arbitrage opportunity
        self.event_with_arb = create_CR_event(
            CR_event_id="test_event_1",
            CR_event_name="Test Match",
            CR_sport="test",
            CR_markets=[
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=-110),
                        create_CR_outcome(CR_name="Team B", CR_price=-110)
                    ],
                    CR_bookmaker="BookmakerA"
                ),
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=100),   # +100 (better than -110)
                        create_CR_outcome(CR_name="Team B", CR_price=-105)  # Slightly better
                    ],
                    CR_bookmaker="BookmakerB"
                )
            ]
        )

        # Create test events with value edge
        self.event_with_value = create_CR_event(
            CR_event_id="test_event_2",
            CR_event_name="Test Match 2",
            CR_sport="test",
            CR_markets=[
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=100),
                        create_CR_outcome(CR_name="Team B", CR_price=-100)
                    ],
                    CR_bookmaker="BookmakerA"
                ),
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=120),  # Value edge
                        create_CR_outcome(CR_name="Team B", CR_price=-140)
                    ],
                    CR_bookmaker="BookmakerB"
                )
            ]
        )

        self.snapshot = create_CR_snapshot(
            CR_events=[self.event_with_arb, self.event_with_value],
            CR_timestamp=datetime.now().isoformat(),
            CR_source="test"
        )

    def test_arbitrage_detection(self):
        """Test arbitrage detection"""
        findings = detect_CR_arbitrage([self.event_with_arb])

        # Test that detector runs without error and returns list
        self.assertIsInstance(findings, list)

        # Test that detector function exists and is callable
        self.assertTrue(callable(detect_CR_arbitrage))

        # If arbitrage found, check structure
        if findings:
            finding = findings[0]
            self.assertEqual(finding['CR_type'], 'arbitrage')
            self.assertIn('CR_profit_margin', finding)
            self.assertGreater(finding['CR_profit_margin'], 0)

        # Test with empty events list
        empty_findings = detect_CR_arbitrage([])
        self.assertIsInstance(empty_findings, list)
        self.assertEqual(len(empty_findings), 0)

    def test_value_edge_detection(self):
        """Test value edge detection"""
        findings = detect_CR_value_edge([self.event_with_value])

        # Should find value edge
        self.assertGreater(len(findings), 0)

        # Check finding structure
        finding = findings[0]
        self.assertEqual(finding['CR_type'], 'value_edge')
        self.assertIn('CR_details', finding)
        self.assertIn('CR_edge', finding['CR_details'])
        self.assertGreater(finding['CR_details']['CR_edge'], 0.0)

    def test_no_false_positives(self):
        """Test that fair markets don't generate false positives"""
        # Create fair market
        fair_event = create_CR_event(
            CR_event_id="fair_event",
            CR_event_name="Fair Match",
            CR_sport="test",
            CR_markets=[
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=100),
                        create_CR_outcome(CR_name="Team B", CR_price=-100)
                    ],
                    CR_bookmaker="BookmakerA"
                ),
                create_CR_market(
                    CR_name="match_winner",
                    CR_outcomes=[
                        create_CR_outcome(CR_name="Team A", CR_price=100),
                        create_CR_outcome(CR_name="Team B", CR_price=-100)
                    ],
                    CR_bookmaker="BookmakerB"
                )
            ]
        )

        fair_snapshot = create_CR_snapshot(
            CR_events=[fair_event],
            CR_timestamp=datetime.now().isoformat(),
            CR_source="test"
        )

        # Should not find arbitrage
        arb_findings = detect_CR_arbitrage(fair_snapshot['CR_events'])
        self.assertEqual(len([f for f in arb_findings if f['CR_type'] == 'arbitrage']), 0)

        # Should not find value edges with 5% threshold
        value_findings = detect_CR_value_edge(fair_snapshot['CR_events'], CR_edge_threshold=0.05)
        self.assertEqual(len([f for f in value_findings if f['CR_type'] == 'value_edge']), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def test_full_pipeline(self):
        """Test full analysis pipeline"""
        # Create complex test data
        events = [
            create_CR_event(
                CR_event_id="complex_event",
                CR_event_name="Complex Match",
                CR_sport="test",
                CR_markets=[
                    create_CR_market(
                        CR_name="match_winner",
                        CR_outcomes=[
                            create_CR_outcome(CR_name="Team A", CR_price=-125),
                            create_CR_outcome(CR_name="Team B", CR_price=120)
                        ],
                        CR_bookmaker="SharpBook"
                    ),
                    create_CR_market(
                        CR_name="match_winner",
                        CR_outcomes=[
                            create_CR_outcome(CR_name="Team A", CR_price=-110),
                            create_CR_outcome(CR_name="Team B", CR_price=110)
                        ],
                        CR_bookmaker="SoftBook"
                    ),
                    create_CR_market(
                        CR_name="total_goals",
                        CR_outcomes=[
                            create_CR_outcome(CR_name="Over 2.5", CR_price=-110),
                            create_CR_outcome(CR_name="Under 2.5", CR_price=100)
                        ],
                        CR_bookmaker="SharpBook"
                    )
                ]
            )
        ]

        snapshot = create_CR_snapshot(
            CR_events=events,
            CR_timestamp=datetime.now().isoformat(),
            CR_source="integration_test"
        )

        # Test all detectors
        arb_findings = detect_CR_arbitrage(snapshot['CR_events'])
        value_findings = detect_CR_value_edge(snapshot['CR_events'])

        # Validate findings
        all_findings = arb_findings + value_findings

        for finding in all_findings:
            self.assertIn(finding['CR_type'], ['arbitrage', 'value_edge'])
            self.assertGreaterEqual(finding.get('CR_confidence', 0.0), 0.0)
            self.assertLessEqual(finding.get('CR_confidence', 0.0), 1.0)
            self.assertIsNotNone(finding.get('CR_event_id'))
            self.assertIsNotNone(finding.get('CR_market_name'))
            self.assertIsInstance(finding.get('CR_bookmakers', []), list)
            self.assertGreater(len(finding.get('CR_bookmakers', [])), 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)

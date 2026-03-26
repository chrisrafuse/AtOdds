#!/usr/bin/env python3
"""
Test Suite for Phase 9: Math Transparency + Sportsbook Rankings
Tests for math proof helpers, CR_math_proof on all detectors, and sportsbook rankings.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.core_engine.odds_math import (
    compute_CR_math_explanation,
    compute_CR_vig_explanation,
    compute_CR_implied_probability,
    compute_CR_vig,
)
from packages.core_engine.detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edge,
    detect_CR_stale_line,
    detect_CR_outlier,
)
from packages.reporting.rankings import generate_CR_sportsbook_rankings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _make_events_with_arb():
    """Two bookmakers with inverted lines → guaranteed arbitrage."""
    return [
        {
            "CR_event_id": "arb_test_001",
            "CR_markets": [
                {
                    "CR_bookmaker": "BookA",
                    "CR_name": "moneyline",
                    "CR_last_update": "2026-01-01T00:00:00Z",
                    "CR_outcomes": [
                        {"CR_name": "Home", "CR_price": 200},
                        {"CR_name": "Away", "CR_price": 200},
                    ],
                },
                {
                    "CR_bookmaker": "BookB",
                    "CR_name": "moneyline",
                    "CR_last_update": "2026-01-01T00:00:00Z",
                    "CR_outcomes": [
                        {"CR_name": "Home", "CR_price": 200},
                        {"CR_name": "Away", "CR_price": 200},
                    ],
                },
            ],
        }
    ]


def _make_events_with_stale():
    return [
        {
            "CR_event_id": "stale_test_001",
            "CR_markets": [
                {
                    "CR_bookmaker": "OldBook",
                    "CR_name": "moneyline",
                    "CR_last_update": "2020-01-01T00:00:00Z",
                    "CR_outcomes": [
                        {"CR_name": "Home", "CR_price": -110},
                        {"CR_name": "Away", "CR_price": -110},
                    ],
                }
            ],
        }
    ]


def _make_events_with_outlier():
    """Five bookmakers where one has wildly different odds."""
    return [
        {
            "CR_event_id": "outlier_test_001",
            "CR_markets": [
                {
                    "CR_bookmaker": f"Book{i}",
                    "CR_name": "moneyline",
                    "CR_last_update": "2026-01-01T00:00:00Z",
                    "CR_outcomes": [
                        {"CR_name": "Home", "CR_price": -110 if i < 4 else -600},
                        {"CR_name": "Away", "CR_price": -110 if i < 4 else 400},
                    ],
                }
                for i in range(5)
            ],
        }
    ]


def _make_snapshot():
    return {
        "CR_events": (
            _make_events_with_arb()
            + _make_events_with_stale()
        )
    }


# ---------------------------------------------------------------------------
# Math explanation helpers
# ---------------------------------------------------------------------------
class TestComputeCRMathExplanation(unittest.TestCase):

    def test_negative_odds_returns_dict(self):
        result = compute_CR_math_explanation(-110)
        self.assertIsInstance(result, dict)

    def test_positive_odds_returns_dict(self):
        result = compute_CR_math_explanation(150)
        self.assertIsInstance(result, dict)

    def test_required_keys_present(self):
        result = compute_CR_math_explanation(-110)
        for key in ("CR_price", "CR_implied_prob", "CR_formula", "CR_result_pct"):
            self.assertIn(key, result, f"Missing key: {key}")

    def test_negative_odds_formula_contains_abs(self):
        result = compute_CR_math_explanation(-110)
        self.assertIn("110", result["CR_formula"])

    def test_positive_odds_formula_contains_100(self):
        result = compute_CR_math_explanation(200)
        self.assertIn("100", result["CR_formula"])

    def test_implied_prob_matches_compute_function(self):
        price = -110
        result = compute_CR_math_explanation(price)
        expected = compute_CR_implied_probability(price)
        self.assertAlmostEqual(result["CR_implied_prob"], expected, places=4)

    def test_result_pct_format(self):
        result = compute_CR_math_explanation(-110)
        self.assertTrue(result["CR_result_pct"].endswith("%"))

    def test_implied_prob_range(self):
        for price in [-300, -110, 100, 200, 500]:
            result = compute_CR_math_explanation(price)
            self.assertGreater(result["CR_implied_prob"], 0.0)
            self.assertLess(result["CR_implied_prob"], 1.0)


class TestComputeCRVigExplanation(unittest.TestCase):

    def test_returns_dict(self):
        result = compute_CR_vig_explanation([-110, -110])
        self.assertIsInstance(result, dict)

    def test_required_keys_present(self):
        result = compute_CR_vig_explanation([-110, -110])
        for key in ("CR_prices", "CR_implied_probs", "CR_sum", "CR_vig", "CR_vig_pct", "CR_formula"):
            self.assertIn(key, result, f"Missing key: {key}")

    def test_vig_nonnegative(self):
        result = compute_CR_vig_explanation([-110, -110])
        self.assertGreaterEqual(result["CR_vig"], 0.0)

    def test_vig_pct_format(self):
        result = compute_CR_vig_explanation([-110, -110])
        self.assertTrue(result["CR_vig_pct"].endswith("%"))

    def test_vig_matches_compute_function(self):
        prices = [-110, -110]
        result = compute_CR_vig_explanation(prices)
        expected = compute_CR_vig(prices)
        self.assertAlmostEqual(result["CR_vig"], expected, places=4)

    def test_formula_is_string(self):
        result = compute_CR_vig_explanation([-110, -110])
        self.assertIsInstance(result["CR_formula"], str)
        self.assertGreater(len(result["CR_formula"]), 0)

    def test_even_market_has_small_vig(self):
        result = compute_CR_vig_explanation([100, -100])
        self.assertEqual(result["CR_vig"], 0.0)


# ---------------------------------------------------------------------------
# Detectors — CR_math_proof presence
# ---------------------------------------------------------------------------
class TestDetectCRArbitrageMathProof(unittest.TestCase):

    def setUp(self):
        self.events = _make_events_with_arb()

    def test_arb_findings_have_math_proof(self):
        findings = detect_CR_arbitrage(self.events)
        for f in findings:
            self.assertIn("CR_math_proof", f, "Arbitrage finding missing CR_math_proof")

    def test_arb_math_proof_has_formula(self):
        findings = detect_CR_arbitrage(self.events)
        for f in findings:
            proof = f["CR_math_proof"]
            self.assertIn("CR_formula", proof)
            self.assertIsInstance(proof["CR_formula"], str)
            self.assertGreater(len(proof["CR_formula"]), 0)

    def test_arb_math_proof_has_implied_probs(self):
        findings = detect_CR_arbitrage(self.events)
        for f in findings:
            proof = f["CR_math_proof"]
            self.assertIn("CR_implied_probs", proof)
            self.assertIn("CR_total_implied", proof)
            self.assertIn("CR_profit_margin", proof)

    def test_arb_profit_margin_positive(self):
        findings = detect_CR_arbitrage(self.events)
        for f in findings:
            margin = f["CR_math_proof"]["CR_profit_margin"]
            self.assertGreater(margin, 0.0)


class TestDetectCRStaleLineMathProof(unittest.TestCase):

    def setUp(self):
        self.events = _make_events_with_stale()

    def test_stale_findings_returned(self):
        findings = detect_CR_stale_line(self.events, CR_stale_threshold_hours=1)
        self.assertGreater(len(findings), 0)

    def test_stale_findings_have_math_proof(self):
        findings = detect_CR_stale_line(self.events, CR_stale_threshold_hours=1)
        for f in findings:
            self.assertIn("CR_math_proof", f, "Stale line finding missing CR_math_proof")

    def test_stale_math_proof_has_formula(self):
        findings = detect_CR_stale_line(self.events, CR_stale_threshold_hours=1)
        for f in findings:
            proof = f["CR_math_proof"]
            self.assertIn("CR_formula", proof)
            self.assertIn("CR_hours_stale", proof)
            self.assertIn("CR_threshold_hours", proof)

    def test_stale_hours_stale_positive(self):
        findings = detect_CR_stale_line(self.events, CR_stale_threshold_hours=1)
        for f in findings:
            self.assertGreater(f["CR_math_proof"]["CR_hours_stale"], 0)


class TestDetectCROutlierMathProof(unittest.TestCase):

    def setUp(self):
        self.events = _make_events_with_outlier()

    def test_outlier_findings_have_math_proof(self):
        findings = detect_CR_outlier(self.events)
        for f in findings:
            self.assertIn("CR_math_proof", f, "Outlier finding missing CR_math_proof")

    def test_outlier_math_proof_keys(self):
        findings = detect_CR_outlier(self.events)
        for f in findings:
            proof = f["CR_math_proof"]
            self.assertIn("CR_z_score", proof)
            self.assertIn("CR_mean", proof)
            self.assertIn("CR_std_dev", proof)
            self.assertIn("CR_formula", proof)

    def test_outlier_z_score_positive(self):
        findings = detect_CR_outlier(self.events)
        for f in findings:
            self.assertGreater(f["CR_math_proof"]["CR_z_score"], 0)


class TestDetectCRValueEdgeMathProof(unittest.TestCase):

    def _make_value_events(self):
        """One book offering +200 when consensus is -110 → clear value edge."""
        return [
            {
                "CR_event_id": "value_test_001",
                "CR_markets": [
                    {
                        "CR_bookmaker": f"Book{i}",
                        "CR_name": "moneyline",
                        "CR_last_update": "2026-01-01T00:00:00Z",
                        "CR_outcomes": [
                            {"CR_name": "Home", "CR_price": -110 if i > 0 else 200},
                            {"CR_name": "Away", "CR_price": -110},
                        ],
                    }
                    for i in range(4)
                ],
            }
        ]

    def test_value_edge_findings_have_math_proof(self):
        findings = detect_CR_value_edge(self._make_value_events())
        for f in findings:
            self.assertIn("CR_math_proof", f, "Value edge finding missing CR_math_proof")

    def test_value_edge_math_proof_keys(self):
        findings = detect_CR_value_edge(self._make_value_events())
        for f in findings:
            proof = f["CR_math_proof"]
            self.assertIn("CR_book_price", proof)
            self.assertIn("CR_consensus_price", proof)
            self.assertIn("CR_edge", proof)
            self.assertIn("CR_formula", proof)

    def test_value_edge_edge_positive(self):
        findings = detect_CR_value_edge(self._make_value_events())
        for f in findings:
            self.assertGreater(f["CR_math_proof"]["CR_edge"], 0)


# ---------------------------------------------------------------------------
# Sportsbook rankings
# ---------------------------------------------------------------------------
class TestGenerateCRSportsbookRankings(unittest.TestCase):

    def setUp(self):
        self.snapshot = _make_snapshot()
        self.findings = (
            detect_CR_arbitrage(_make_events_with_arb())
            + detect_CR_stale_line(_make_events_with_stale(), CR_stale_threshold_hours=1)
        )

    def test_returns_list(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        self.assertIsInstance(result, list)

    def test_rankings_not_empty(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        self.assertGreater(len(result), 0)

    def test_required_keys_in_each_ranking(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        required = [
            "CR_bookmaker", "CR_avg_vig", "CR_avg_vig_pct", "CR_best_line_count",
            "CR_best_line_pct", "CR_stale_count", "CR_outlier_count",
            "CR_market_count", "CR_quality_score", "CR_verdict", "CR_rank"
        ]
        for ranking in result:
            for key in required:
                self.assertIn(key, ranking, f"Ranking missing key: {key}")

    def test_quality_score_in_range(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        for r in result:
            self.assertGreaterEqual(r["CR_quality_score"], 0.0)
            self.assertLessEqual(r["CR_quality_score"], 100.0)

    def test_verdict_valid_values(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        valid = {"Recommended", "Average", "Avoid"}
        for r in result:
            self.assertIn(r["CR_verdict"], valid)

    def test_ranks_sequential(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        ranks = [r["CR_rank"] for r in result]
        self.assertEqual(ranks, list(range(1, len(result) + 1)))

    def test_sorted_by_quality_score_descending(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        scores = [r["CR_quality_score"] for r in result]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_stale_book_has_stale_count(self):
        result = generate_CR_sportsbook_rankings(self.snapshot, self.findings)
        old_book = next((r for r in result if r["CR_bookmaker"] == "OldBook"), None)
        if old_book:
            self.assertGreater(old_book["CR_stale_count"], 0)

    def test_empty_snapshot_returns_empty(self):
        result = generate_CR_sportsbook_rankings({"CR_events": []}, [])
        self.assertEqual(result, [])


# ---------------------------------------------------------------------------
# Integration: full findings pipeline has math proofs
# ---------------------------------------------------------------------------
class TestFullPipelineMathProofs(unittest.TestCase):

    def test_all_finding_types_carry_math_proof(self):
        """After running all detectors, every finding should have CR_math_proof."""
        from packages.agent.agent import execute_CR_analysis_pipeline
        snapshot = _make_snapshot()
        result = execute_CR_analysis_pipeline(snapshot)

        for f in result["CR_findings"]:
            self.assertIn(
                "CR_math_proof", f,
                f"Finding of type '{f.get('CR_type')}' missing CR_math_proof"
            )

    def test_pipeline_rankings_have_correct_structure(self):
        from packages.agent.agent import execute_CR_analysis_pipeline
        snapshot = _make_snapshot()
        result = execute_CR_analysis_pipeline(snapshot)

        for r in result["CR_sportsbook_rankings"]:
            self.assertIn("CR_quality_score", r)
            self.assertIn("CR_verdict", r)
            self.assertIn("CR_rank", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)

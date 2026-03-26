"""
Signal detectors - detect arbitrage, value edges, stale lines, outliers with CR_ prefix compliance
"""

from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta, timezone
import statistics

from packages.data.contracts import create_CR_finding
from .odds_math import (
    compute_CR_implied_probability,
    compute_CR_expected_value,
    compute_CR_math_explanation,
    compute_CR_vig_explanation,
)
from .consensus import compute_CR_best_lines, compute_CR_consensus_price


def detect_CR_stale_line(CR_events: List[Dict[str, Any]], CR_stale_threshold_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Detect markets that haven't been updated recently

    Args:
        CR_events: List of CR_event dictionaries to analyze
        CR_stale_threshold_hours: Hours since last update to consider stale

    Returns:
        List of CR_finding dictionaries for stale lines
    """
    CR_findings = []
    CR_threshold = timedelta(hours=CR_stale_threshold_hours)
    CR_now = datetime.now(timezone.utc)

    for CR_event in CR_events:
        CR_event_id = CR_event.get("CR_event_id", "")
        CR_markets = CR_event.get("CR_markets", [])

        for CR_market in CR_markets:
            CR_last_update_str = CR_market.get("CR_last_update")
            if CR_last_update_str:
                try:
                    CR_last_update = datetime.fromisoformat(CR_last_update_str.replace('Z', '+00:00'))
                    if (CR_now - CR_last_update) > CR_threshold:
                        CR_market_name = CR_market.get("CR_name", "")
                        CR_bookmaker = CR_market.get("CR_bookmaker", "")
                        CR_hours_stale = (CR_now - CR_last_update).total_seconds() / 3600

                        CR_finding = create_CR_finding(
                            CR_type='stale_line',
                            CR_description=f"Market {CR_market_name} from {CR_bookmaker} last updated {CR_hours_stale:.1f} hours ago",
                            CR_confidence=0.8,
                            CR_event_id=CR_event_id,
                            CR_market_name=CR_market_name,
                            CR_bookmakers=[CR_bookmaker],
                            CR_details={
                                'CR_last_update': CR_last_update_str,
                                'CR_hours_stale': CR_hours_stale
                            }
                        )
                        CR_finding['CR_math_proof'] = {
                            'CR_last_updated': CR_last_update_str,
                            'CR_hours_stale': round(CR_hours_stale, 1),
                            'CR_threshold_hours': CR_stale_threshold_hours,
                            'CR_formula': f"{CR_hours_stale:.1f}h since last update (threshold: {CR_stale_threshold_hours}h)"
                        }
                        CR_findings.append(CR_finding)
                except (ValueError, AttributeError):
                    pass

    return CR_findings


def detect_CR_outlier(CR_events: List[Dict[str, Any]], CR_outlier_threshold: float = 2.0) -> List[Dict[str, Any]]:
    """
    Detect outlier odds using statistical methods

    Args:
        CR_events: List of CR_event dictionaries to analyze
        CR_outlier_threshold: Standard deviations from mean to flag as outlier

    Returns:
        List of CR_finding dictionaries for outliers
    """
    CR_findings = []

    for CR_event in CR_events:
        CR_event_id = CR_event.get("CR_event_id", "")
        CR_markets = CR_event.get("CR_markets", [])

        # Group markets by name for comparison
        CR_market_groups = {}
        for CR_market in CR_markets:
            CR_market_name = CR_market.get("CR_name", "")
            if CR_market_name not in CR_market_groups:
                CR_market_groups[CR_market_name] = []
            CR_market_groups[CR_market_name].append(CR_market)

        for CR_market_name, CR_grouped_markets in CR_market_groups.items():
            if len(CR_grouped_markets) < 3:
                continue

            # Analyze each outcome position
            for CR_outcome_idx in range(2):  # Typically 2 outcomes per market
                CR_prices = []
                CR_outcome_names = []
                CR_bookmakers = []

                for CR_market in CR_grouped_markets:
                    CR_outcomes = CR_market.get("CR_outcomes", [])
                    if CR_outcome_idx < len(CR_outcomes):
                        CR_outcome = CR_outcomes[CR_outcome_idx]
                        CR_price = CR_outcome.get("CR_price")
                        if CR_price is not None:
                            CR_prices.append(CR_price)
                            CR_outcome_names.append(CR_outcome.get("CR_name", ""))
                            CR_bookmakers.append(CR_market.get("CR_bookmaker", ""))

                if len(CR_prices) < 3:
                    continue

                CR_mean_price = statistics.mean(CR_prices)
                CR_std_price = statistics.stdev(CR_prices) if len(CR_prices) > 1 else 0

                # Find outliers
                for CR_idx, CR_price in enumerate(CR_prices):
                    CR_z_score = abs(CR_price - CR_mean_price) / CR_std_price if CR_std_price > 0 else 0

                    if CR_z_score > CR_outlier_threshold:
                        CR_math = compute_CR_math_explanation(CR_price)
                        CR_finding = create_CR_finding(
                            CR_type='outlier',
                            CR_description=f"Outlier odds for {CR_outcome_names[CR_idx]}: {CR_price} (z-score: {CR_z_score:.2f})",
                            CR_confidence=min(0.9, CR_z_score / CR_outlier_threshold * 0.5),
                            CR_event_id=CR_event_id,
                            CR_market_name=CR_market_name,
                            CR_bookmakers=[CR_bookmakers[CR_idx]],
                            CR_details={
                                'CR_outcome_name': CR_outcome_names[CR_idx],
                                'CR_price': CR_price,
                                'CR_z_score': CR_z_score,
                                'CR_mean_price': CR_mean_price,
                                'CR_std_price': CR_std_price
                            }
                        )
                        CR_finding['CR_math_proof'] = {
                            'CR_price': CR_price,
                            'CR_implied_prob': CR_math['CR_result_pct'],
                            'CR_market_prices': CR_prices,
                            'CR_mean': round(CR_mean_price, 1),
                            'CR_std_dev': round(CR_std_price, 2),
                            'CR_z_score': round(CR_z_score, 2),
                            'CR_formula': f"({CR_price} − {CR_mean_price:.1f}) / {CR_std_price:.2f} = {CR_z_score:.2f}σ deviation"
                        }
                        CR_findings.append(CR_finding)

    return CR_findings


def detect_CR_arbitrage(CR_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect arbitrage opportunities across bookmakers

    Args:
        CR_events: List of CR_event dictionaries to analyze

    Returns:
        List of CR_finding dictionaries for arbitrage opportunities
    """
    CR_findings = []

    for CR_event in CR_events:
        CR_event_id = CR_event.get("CR_event_id", "")
        CR_markets = CR_event.get("CR_markets", [])

        # Group markets by name for arbitrage detection
        CR_market_groups = {}
        for CR_market in CR_markets:
            CR_market_name = CR_market.get("CR_name", "")
            if CR_market_name not in CR_market_groups:
                CR_market_groups[CR_market_name] = []
            CR_market_groups[CR_market_name].append(CR_market)

        for CR_market_name, CR_grouped_markets in CR_market_groups.items():
            # Find best lines across all bookmakers
            CR_best_lines = compute_CR_best_lines(CR_grouped_markets)

            if len(CR_best_lines) < 2:
                continue

            # Calculate arbitrage opportunity
            CR_total_implied = sum(
                compute_CR_implied_probability(CR_price)
                for _, CR_price in CR_best_lines.values()
            )

            if CR_total_implied < 1.0:  # Arbitrage opportunity exists
                CR_profit_margin = (1.0 - CR_total_implied) / CR_total_implied
                CR_bookmakers = list(set(CR_bookmaker for CR_bookmaker, _ in CR_best_lines.values()))

                CR_outcome_probs = {
                    CR_outcome: round(compute_CR_implied_probability(CR_price), 4)
                    for CR_outcome, (_, CR_price) in CR_best_lines.items()
                }
                CR_arb_parts = " + ".join(
                    f"{CR_bm}({CR_outcome}) {CR_price} → {CR_outcome_probs[CR_outcome]*100:.1f}%"
                    for CR_outcome, (CR_bm, CR_price) in CR_best_lines.items()
                )
                CR_finding = create_CR_finding(
                    CR_type='arbitrage',
                    CR_description=f"Arbitrage opportunity: {CR_profit_margin:.2%} profit margin",
                    CR_confidence=0.95,
                    CR_event_id=CR_event_id,
                    CR_market_name=CR_market_name,
                    CR_bookmakers=CR_bookmakers,
                    CR_details={
                        'CR_best_lines': {
                            CR_outcome: {
                                'CR_bookmaker': CR_bm,
                                'CR_price': CR_price
                            }
                            for CR_outcome, (CR_bm, CR_price) in CR_best_lines.items()
                        },
                        'CR_total_implied': CR_total_implied,
                        'CR_profit_margin': CR_profit_margin
                    }
                )
                CR_finding['CR_math_proof'] = {
                    'CR_implied_probs': CR_outcome_probs,
                    'CR_total_implied': round(CR_total_implied, 4),
                    'CR_profit_margin': round(CR_profit_margin, 4),
                    'CR_formula': f"{CR_arb_parts} → sum={CR_total_implied*100:.2f}% → margin={CR_profit_margin*100:.2f}%"
                }
                CR_findings.append(CR_finding)

    return CR_findings


def detect_CR_value_edge(CR_events: List[Dict[str, Any]], CR_edge_threshold: float = 0.05) -> List[Dict[str, Any]]:
    """
    Detect value edges where odds are favorable compared to consensus

    Args:
        CR_events: List of CR_event dictionaries to analyze
        CR_edge_threshold: Minimum edge to consider (5% default)

    Returns:
        List of CR_finding dictionaries for value edges
    """
    CR_findings = []

    for CR_event in CR_events:
        CR_event_id = CR_event.get("CR_event_id", "")
        CR_markets = CR_event.get("CR_markets", [])

        # Group markets by name
        CR_market_groups = {}
        for CR_market in CR_markets:
            CR_market_name = CR_market.get("CR_name", "")
            if CR_market_name not in CR_market_groups:
                CR_market_groups[CR_market_name] = []
            CR_market_groups[CR_market_name].append(CR_market)

        for CR_market_name, CR_grouped_markets in CR_market_groups.items():
            # Calculate consensus for each outcome
            for CR_market in CR_grouped_markets:
                CR_bookmaker = CR_market.get("CR_bookmaker", "")
                CR_outcomes = CR_market.get("CR_outcomes", [])

                for CR_outcome in CR_outcomes:
                    CR_outcome_name = CR_outcome.get("CR_name", "")
                    CR_price = CR_outcome.get("CR_price")

                    if CR_price is None:
                        continue

                    CR_consensus_price = compute_CR_consensus_price(CR_grouped_markets, CR_outcome_name)

                    if CR_consensus_price is None or CR_consensus_price == 0:
                        continue

                    # Calculate edge (positive American odds comparison)
                    CR_edge = (CR_price / CR_consensus_price) - 1.0

                    if CR_edge > CR_edge_threshold:
                        CR_book_math = compute_CR_math_explanation(int(CR_price))
                        CR_cons_math = compute_CR_math_explanation(int(CR_consensus_price))
                        CR_finding = create_CR_finding(
                            CR_type='value_edge',
                            CR_description=f"Value edge on {CR_outcome_name}: {CR_edge:.2%} above consensus",
                            CR_confidence=min(0.85, CR_edge / CR_edge_threshold * 0.4),
                            CR_event_id=CR_event_id,
                            CR_market_name=CR_market_name,
                            CR_bookmakers=[CR_bookmaker],
                            CR_details={
                                'CR_outcome_name': CR_outcome_name,
                                'CR_price': CR_price,
                                'CR_consensus_price': CR_consensus_price,
                                'CR_edge': CR_edge
                            }
                        )
                        CR_finding['CR_math_proof'] = {
                            'CR_book_price': CR_price,
                            'CR_book_implied': CR_book_math['CR_result_pct'],
                            'CR_consensus_price': CR_consensus_price,
                            'CR_consensus_implied': CR_cons_math['CR_result_pct'],
                            'CR_edge': round(CR_edge, 4),
                            'CR_formula': f"{CR_bookmaker} {CR_price} → {CR_book_math['CR_result_pct']} vs consensus {CR_consensus_price} → {CR_cons_math['CR_result_pct']} | edge={CR_edge*100:.1f}%"
                        }
                        CR_findings.append(CR_finding)

    return CR_findings

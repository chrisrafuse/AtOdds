"""
Consensus calculations - market aggregation with CR_ prefix compliance
"""

from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import statistics

from .odds_math import compute_CR_implied_probability


def compute_CR_best_lines(CR_markets: List[Dict[str, Any]]) -> Dict[str, Tuple[str, int]]:
    """
    Find best odds for each outcome across all bookmakers

    Args:
        CR_markets: List of CR_market dictionaries from different bookmakers

    Returns:
        Dict mapping CR_outcome_name -> (CR_bookmaker, CR_best_price)
    """
    CR_best_lines = {}

    for CR_market in CR_markets:
        CR_bookmaker = CR_market.get("CR_bookmaker", "Unknown")
        CR_outcomes = CR_market.get("CR_outcomes", [])

        for CR_outcome in CR_outcomes:
            CR_outcome_name = CR_outcome.get("CR_name", "")
            CR_price = CR_outcome.get("CR_price", 0)

            CR_current_best = CR_best_lines.get(CR_outcome_name)

            # Higher American odds = better for bettor
            if CR_current_best is None or CR_price > CR_current_best[1]:
                CR_best_lines[CR_outcome_name] = (CR_bookmaker, CR_price)

    return CR_best_lines


def compute_CR_consensus_price(CR_markets: List[Dict[str, Any]], CR_outcome_name: str) -> Optional[int]:
    """
    Calculate consensus price for an outcome using median

    Args:
        CR_markets: List of CR_market dictionaries
        CR_outcome_name: Name of outcome to analyze

    Returns:
        Consensus American odds or None if not found
    """
    CR_prices = []

    for CR_market in CR_markets:
        CR_outcomes = CR_market.get("CR_outcomes", [])

        for CR_outcome in CR_outcomes:
            if CR_outcome.get("CR_name") == CR_outcome_name:
                CR_price = CR_outcome.get("CR_price")
                if CR_price is not None:
                    CR_prices.append(CR_price)

    if not CR_prices:
        return None

    # Use median for robustness against outliers
    return int(statistics.median(CR_prices))


def compute_CR_weighted_consensus(
    CR_markets: List[Dict[str, Any]],
    CR_outcome_name: str,
    CR_sharp_bookmakers: List[str] = None,
    CR_sharp_weight: float = 2.0
) -> Optional[int]:
    """
    Calculate weighted consensus with sharp bookmaker weighting

    Args:
        CR_markets: List of CR_market dictionaries
        CR_outcome_name: Name of outcome to analyze
        CR_sharp_bookmakers: List of sharp bookmaker names (default: ["Pinnacle"])
        CR_sharp_weight: Weight multiplier for sharp bookmakers

    Returns:
        Weighted consensus American odds or None if not found
    """
    if CR_sharp_bookmakers is None:
        CR_sharp_bookmakers = ["Pinnacle", "pinnacle"]

    CR_weighted_sum = 0.0
    CR_total_weight = 0.0

    for CR_market in CR_markets:
        CR_bookmaker = CR_market.get("CR_bookmaker", "")
        CR_outcomes = CR_market.get("CR_outcomes", [])

        for CR_outcome in CR_outcomes:
            if CR_outcome.get("CR_name") == CR_outcome_name:
                CR_price = CR_outcome.get("CR_price")
                if CR_price is not None:
                    CR_weight = CR_sharp_weight if CR_bookmaker in CR_sharp_bookmakers else 1.0
                    CR_weighted_sum += CR_price * CR_weight
                    CR_total_weight += CR_weight

    if CR_total_weight == 0:
        return None

    return int(CR_weighted_sum / CR_total_weight)


def compute_CR_market_efficiency(CR_markets: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate efficiency metrics for each bookmaker based on vig

    Args:
        CR_markets: List of CR_market dictionaries

    Returns:
        Dict mapping CR_bookmaker -> CR_efficiency_score (0.0 to 1.0)
    """
    CR_bookmaker_vigs = defaultdict(list)

    for CR_market in CR_markets:
        CR_bookmaker = CR_market.get("CR_bookmaker", "Unknown")
        CR_outcomes = CR_market.get("CR_outcomes", [])

        if len(CR_outcomes) == 2:
            # Calculate vig for this market
            CR_total_implied = 0.0
            for CR_outcome in CR_outcomes:
                CR_price = CR_outcome.get("CR_price", 0)
                if CR_price != 0:
                    CR_total_implied += compute_CR_implied_probability(CR_price)

            CR_vig = max(0.0, CR_total_implied - 1.0)
            CR_bookmaker_vigs[CR_bookmaker].append(CR_vig)

    CR_efficiency = {}

    for CR_bookmaker, CR_vigs in CR_bookmaker_vigs.items():
        if not CR_vigs:
            CR_efficiency[CR_bookmaker] = 0.0
            continue

        # Lower average vig = higher efficiency
        CR_avg_vig = statistics.mean(CR_vigs)
        CR_efficiency[CR_bookmaker] = 1.0 / (1.0 + CR_avg_vig * 100)

    return CR_efficiency


def compute_CR_market_depth(CR_markets: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate market depth (number of markets) per bookmaker

    Args:
        CR_markets: List of CR_market dictionaries

    Returns:
        Dict mapping CR_bookmaker -> CR_market_count
    """
    CR_bookmaker_counts = defaultdict(int)

    for CR_market in CR_markets:
        CR_bookmaker = CR_market.get("CR_bookmaker", "Unknown")
        CR_bookmaker_counts[CR_bookmaker] += 1

    return dict(CR_bookmaker_counts)

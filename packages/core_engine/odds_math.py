"""
Odds math - TRUTH layer for all calculations
No LLM dependency EVER
"""

from typing import List, Tuple, Union, Dict, Any
import math


def compute_CR_american_to_decimal(CR_american_odds: int) -> float:
    """
    Convert American odds to decimal odds

    Args:
        CR_american_odds: American odds (e.g., -110, +150)

    Returns:
        Decimal odds (e.g., 1.91, 2.5)
    """
    if CR_american_odds > 0:
        return (CR_american_odds / 100.0) + 1.0
    elif CR_american_odds < 0:
        return (100.0 / abs(CR_american_odds)) + 1.0
    else:
        raise ValueError("American odds cannot be zero")


def compute_CR_decimal_to_american(CR_decimal_odds: float) -> int:
    """
    Convert decimal odds to American odds

    Args:
        CR_decimal_odds: Decimal odds (e.g., 1.91, 2.5)

    Returns:
        American odds (e.g., -110, +150)
    """
    if CR_decimal_odds < 1.0:
        raise ValueError("Decimal odds must be >= 1.0")

    if CR_decimal_odds >= 2.0:
        return int((CR_decimal_odds - 1.0) * 100)
    else:
        return int(-100.0 / (CR_decimal_odds - 1.0))


def compute_CR_implied_probability(CR_price: int) -> float:
    """
    Convert American odds to implied probability

    Args:
        CR_price: American odds (e.g., -111, 196)

    Returns:
        Implied probability (0.0 to 1.0)
    """
    if CR_price > 0:
        # Positive American odds (underdog)
        return 100.0 / (CR_price + 100)
    elif CR_price < 0:
        # Negative American odds (favorite)
        return abs(CR_price) / (abs(CR_price) + 100)
    else:
        raise ValueError("Price cannot be zero")


def compute_CR_vig(CR_outcomes: List[int]) -> float:
    """
    Calculate vigorish (juice) from American odds

    Args:
        CR_outcomes: List of American odds

    Returns:
        Vig as percentage (0.0 to 1.0)
    """
    if not CR_outcomes:
        return 0.0

    total_implied = sum(compute_CR_implied_probability(price) for price in CR_outcomes)
    return max(0.0, total_implied - 1.0)


def compute_CR_true_probability(CR_price: int, CR_market_vig: float) -> float:
    """
    Remove vig from American odds to get true probability

    Args:
        CR_price: American odds with vig
        CR_market_vig: Vig percentage (0.0 to 1.0)

    Returns:
        True implied probability (0.0 to 1.0)
    """
    implied = compute_CR_implied_probability(CR_price)
    true_probability = implied / (1.0 + CR_market_vig)

    if true_probability <= 0:
        return 0.0

    return true_probability


def compute_CR_kelly_fraction(CR_true_prob: float, CR_american_odds: int) -> float:
    """
    Calculate Kelly criterion fraction for American odds

    Args:
        CR_true_prob: True probability (0.0 to 1.0)
        CR_american_odds: American odds offered

    Returns:
        Kelly fraction (0.0 to 1.0)
    """
    if CR_true_prob <= 0:
        return 0.0

    # Convert American odds to decimal odds for Kelly calculation
    if CR_american_odds > 0:
        CR_decimal_odds = (CR_american_odds / 100) + 1
    else:
        CR_decimal_odds = (100 / abs(CR_american_odds)) + 1

    if CR_decimal_odds <= 1:
        return 0.0

    implied_prob = compute_CR_implied_probability(CR_american_odds)
    edge = CR_true_prob - implied_prob

    if edge <= 0:
        return 0.0

    return edge / (CR_decimal_odds - 1)


def compute_CR_expected_value(CR_true_prob: float, CR_american_odds: int, CR_stake: float = 1.0) -> float:
    """
    Calculate expected value of a bet with American odds

    Args:
        CR_true_prob: True probability (0.0 to 1.0)
        CR_american_odds: American odds offered
        CR_stake: Amount staked

    Returns:
        Expected value
    """
    # Convert American odds to decimal payout
    if CR_american_odds > 0:
        CR_payout = CR_stake * (CR_american_odds / 100)
    else:
        CR_payout = CR_stake * (100 / abs(CR_american_odds))

    win_return = CR_stake + CR_payout
    return (CR_true_prob * win_return) - (CR_stake * (1 - CR_true_prob))


def compute_CR_math_explanation(CR_price: int) -> Dict[str, Any]:
    """
    Return a structured breakdown showing the implied probability calculation.

    Returns:
        Dict with formula string, result, and raw values for display
    """
    CR_implied = compute_CR_implied_probability(CR_price)
    if CR_price < 0:
        CR_formula = f"|{CR_price}| / (|{CR_price}| + 100) = {abs(CR_price)} / {abs(CR_price) + 100}"
    else:
        CR_formula = f"100 / ({CR_price} + 100) = 100 / {CR_price + 100}"

    return {
        "CR_price": CR_price,
        "CR_implied_prob": round(CR_implied, 4),
        "CR_formula": CR_formula,
        "CR_result_pct": f"{CR_implied * 100:.1f}%",
    }


def compute_CR_vig_explanation(CR_prices: List[int]) -> Dict[str, Any]:
    """
    Return a structured breakdown showing the vig calculation.

    Returns:
        Dict with per-outcome implied probs, sum, vig, and formula string
    """
    CR_implied_probs = [compute_CR_implied_probability(p) for p in CR_prices]
    CR_total = sum(CR_implied_probs)
    CR_vig = max(0.0, CR_total - 1.0)

    CR_parts = " + ".join(f"{p * 100:.2f}%" for p in CR_implied_probs)
    CR_formula = f"{CR_parts} = {CR_total * 100:.2f}% → vig = {CR_vig * 100:.2f}%"

    return {
        "CR_prices": CR_prices,
        "CR_implied_probs": [round(p, 4) for p in CR_implied_probs],
        "CR_sum": round(CR_total, 4),
        "CR_vig": round(CR_vig, 4),
        "CR_vig_pct": f"{CR_vig * 100:.2f}%",
        "CR_formula": CR_formula,
    }

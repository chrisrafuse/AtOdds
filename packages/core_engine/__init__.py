"""
Core Engine Package
Mathematical and analytical engine for odds analysis
"""

from .odds_math import (
    compute_CR_implied_probability,
    compute_CR_american_to_decimal,
    compute_CR_decimal_to_american,
    compute_CR_vig,
    compute_CR_true_probability,
    compute_CR_expected_value
)

from .consensus import (
    compute_CR_best_lines,
    compute_CR_consensus_price,
    compute_CR_market_efficiency
)

from .detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edge,
    detect_CR_stale_line,
    detect_CR_outlier
)

__all__ = [
    'compute_CR_implied_probability',
    'compute_CR_american_to_decimal',
    'compute_CR_decimal_to_american',
    'compute_CR_vig',
    'compute_CR_true_probability',
    'compute_CR_expected_value',
    'compute_CR_kelly_fraction',
    'compute_CR_best_lines',
    'compute_CR_consensus_price',
    'compute_CR_weighted_consensus',
    'compute_CR_market_efficiency',
    'compute_CR_market_depth',
    'detect_CR_arbitrage',
    'detect_CR_value_edge',
    'detect_CR_stale_line',
    'detect_CR_outlier'
]

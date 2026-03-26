"""
OpenAI-style JSON schemas for all CR_TOOL_REGISTRY tools.
Defined once here; all provider adapters reference this list.
"""

from typing import List, Dict, Any

CR_SNAPSHOT_PARAM = {
    "type": "object",
    "description": "The CR_ odds snapshot containing CR_events list",
    "properties": {
        "CR_events": {
            "type": "array",
            "description": "List of CR_ event objects with markets and outcomes",
            "items": {
                "type": "object",
                "description": "A sports betting event with markets and outcomes"
            }
        }
    },
    "required": ["CR_events"]
}

CR_TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "CR_detect_arbitrage",
        "description": (
            "Detect cross-bookmaker arbitrage opportunities where betting all outcomes "
            "guarantees profit. Returns list of findings with profit margin and bookmakers involved."
        ),
        "parameters": {
            "type": "object",
            "properties": {"CR_snapshot": CR_SNAPSHOT_PARAM},
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_detect_stale_lines",
        "description": (
            "Detect lines that have not been updated recently. "
            "Stale lines indicate a bookmaker may not be tracking market movement."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "CR_snapshot": CR_SNAPSHOT_PARAM,
                "CR_stale_threshold_hours": {
                    "type": "integer",
                    "description": "Hours after which a line is considered stale. Default 24.",
                    "default": 24
                }
            },
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_detect_outliers",
        "description": (
            "Detect statistically unusual odds that deviate significantly from market consensus. "
            "High z-score outliers may indicate pricing errors or sharp money."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "CR_snapshot": CR_SNAPSHOT_PARAM,
                "CR_outlier_threshold": {
                    "type": "number",
                    "description": "Standard deviation threshold for outlier classification. Default 2.0.",
                    "default": 2.0
                }
            },
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_detect_value_edges",
        "description": (
            "Detect outcomes where a bookmaker's implied probability is lower than market consensus, "
            "indicating the bettor has a mathematical edge."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "CR_snapshot": CR_SNAPSHOT_PARAM,
                "CR_edge_threshold": {
                    "type": "number",
                    "description": "Minimum edge (as decimal fraction) to qualify as value. Default 0.05.",
                    "default": 0.05
                }
            },
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_compute_best_lines",
        "description": (
            "Find the best available price for each outcome across all bookmakers. "
            "Returns the bookmaker offering the highest payout (lowest implied probability) per side."
        ),
        "parameters": {
            "type": "object",
            "properties": {"CR_snapshot": CR_SNAPSHOT_PARAM},
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_compute_consensus",
        "description": (
            "Calculate the market consensus price for each outcome by averaging "
            "implied probabilities across all bookmakers."
        ),
        "parameters": {
            "type": "object",
            "properties": {"CR_snapshot": CR_SNAPSHOT_PARAM},
            "required": ["CR_snapshot"]
        }
    },
    {
        "name": "CR_compute_vig",
        "description": (
            "Calculate the bookmaker margin (vigorish) for a set of American odds. "
            "Example: -110/-110 → 52.38% + 52.38% = 104.76% → vig = 4.76%"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "CR_american_odds_list": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "List of American odds integers for both sides of a market"
                }
            },
            "required": ["CR_american_odds_list"]
        }
    },
    {
        "name": "CR_compute_implied_probability",
        "description": (
            "Convert a single American odds value to implied probability. "
            "Negative odds: |odds|/(|odds|+100). Positive: 100/(odds+100)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "CR_american_odds": {
                    "type": "integer",
                    "description": "Single American odds value (e.g. -150 or +200)"
                }
            },
            "required": ["CR_american_odds"]
        }
    },
    {
        "name": "CR_compute_market_efficiency",
        "description": (
            "Compute market efficiency scores for each bookmaker in the snapshot. "
            "Lower vig and tighter spreads indicate a more efficient market."
        ),
        "parameters": {
            "type": "object",
            "properties": {"CR_snapshot": CR_SNAPSHOT_PARAM},
            "required": ["CR_snapshot"]
        }
    },
]

"""
Tool registry - wraps core engine into callable tools with CR_ prefix compliance
Agent must call tools, not raw functions
"""

from typing import Dict, Any, List
from datetime import datetime

from packages.core_engine.odds_math import (
    compute_CR_implied_probability,
    compute_CR_vig,
    compute_CR_true_probability,
    compute_CR_american_to_decimal,
    compute_CR_decimal_to_american
)
from packages.core_engine.consensus import (
    compute_CR_best_lines,
    compute_CR_consensus_price,
    compute_CR_weighted_consensus,
    compute_CR_market_efficiency
)
from packages.core_engine.detectors import (
    detect_CR_stale_line,
    detect_CR_outlier,
    detect_CR_arbitrage,
    detect_CR_value_edge
)


def tool_CR_compute_implied_probability(CR_american_odds: int) -> Dict[str, Any]:
    """Calculate implied probability from American odds"""
    try:
        CR_result = compute_CR_implied_probability(CR_american_odds)
        return {
            'CR_success': True,
            'CR_result': CR_result,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_compute_vig(CR_american_odds_list: List[int]) -> Dict[str, Any]:
    """Calculate vigorish from American odds"""
    try:
        CR_result = compute_CR_vig(CR_american_odds_list)
        return {
            'CR_success': True,
            'CR_result': CR_result,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_convert_odds(CR_odds_value: float, CR_from_format: str, CR_to_format: str) -> Dict[str, Any]:
    """Convert odds between American and decimal formats"""
    try:
        if CR_from_format == 'american' and CR_to_format == 'decimal':
            CR_result = compute_CR_american_to_decimal(int(CR_odds_value))
        elif CR_from_format == 'decimal' and CR_to_format == 'american':
            CR_result = compute_CR_decimal_to_american(CR_odds_value)
        else:
            raise ValueError(f"Unsupported conversion: {CR_from_format} to {CR_to_format}")

        return {
            'CR_success': True,
            'CR_result': CR_result,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_detect_arbitrage(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Detect arbitrage opportunities in the dataset"""
    try:
        CR_events = CR_snapshot.get('CR_events', [])
        CR_findings = detect_CR_arbitrage(CR_events)
        return {
            'CR_success': True,
            'CR_result': CR_findings,
            'CR_count': len(CR_findings),
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_detect_stale_lines(CR_snapshot: Dict[str, Any], CR_stale_threshold_hours: int = 24) -> Dict[str, Any]:
    """Detect stale lines in the dataset"""
    try:
        CR_events = CR_snapshot.get('CR_events', [])
        CR_findings = detect_CR_stale_line(CR_events, CR_stale_threshold_hours)
        return {
            'CR_success': True,
            'CR_result': CR_findings,
            'CR_count': len(CR_findings),
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_detect_outliers(CR_snapshot: Dict[str, Any], CR_outlier_threshold: float = 2.0) -> Dict[str, Any]:
    """Detect outlier odds in the dataset"""
    try:
        CR_events = CR_snapshot.get('CR_events', [])
        CR_findings = detect_CR_outlier(CR_events, CR_outlier_threshold)
        return {
            'CR_success': True,
            'CR_result': CR_findings,
            'CR_count': len(CR_findings),
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_detect_value_edges(CR_snapshot: Dict[str, Any], CR_edge_threshold: float = 0.05) -> Dict[str, Any]:
    """Detect value edges in the dataset"""
    try:
        CR_events = CR_snapshot.get('CR_events', [])
        CR_findings = detect_CR_value_edge(CR_events, CR_edge_threshold)
        return {
            'CR_success': True,
            'CR_result': CR_findings,
            'CR_count': len(CR_findings),
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_compute_best_lines(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Compute best lines across all bookmakers"""
    try:
        CR_all_best_lines = {}
        CR_events = CR_snapshot.get('CR_events', [])

        for CR_event in CR_events:
            CR_event_id = CR_event.get('CR_event_id', '')
            CR_markets = CR_event.get('CR_markets', [])

            # Group markets by name
            CR_market_groups = {}
            for CR_market in CR_markets:
                CR_market_name = CR_market.get('CR_name', '')
                if CR_market_name not in CR_market_groups:
                    CR_market_groups[CR_market_name] = []
                CR_market_groups[CR_market_name].append(CR_market)

            CR_event_best_lines = {}
            for CR_market_name, CR_grouped_markets in CR_market_groups.items():
                CR_best_lines = compute_CR_best_lines(CR_grouped_markets)
                CR_event_best_lines[CR_market_name] = CR_best_lines

            CR_all_best_lines[CR_event_id] = CR_event_best_lines

        return {
            'CR_success': True,
            'CR_result': CR_all_best_lines,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_compute_consensus(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Compute consensus prices across bookmakers"""
    try:
        CR_consensus_data = {}
        CR_events = CR_snapshot.get('CR_events', [])

        for CR_event in CR_events:
            CR_event_id = CR_event.get('CR_event_id', '')
            CR_markets = CR_event.get('CR_markets', [])

            # Group markets by name
            CR_market_groups = {}
            for CR_market in CR_markets:
                CR_market_name = CR_market.get('CR_name', '')
                if CR_market_name not in CR_market_groups:
                    CR_market_groups[CR_market_name] = []
                CR_market_groups[CR_market_name].append(CR_market)

            CR_event_consensus = {}
            for CR_market_name, CR_grouped_markets in CR_market_groups.items():
                CR_market_consensus = {}

                # Get all unique outcome names
                CR_outcome_names = set()
                for CR_market in CR_grouped_markets:
                    for CR_outcome in CR_market.get('CR_outcomes', []):
                        CR_outcome_names.add(CR_outcome.get('CR_name', ''))

                # Compute consensus for each outcome
                for CR_outcome_name in CR_outcome_names:
                    CR_consensus_price = compute_CR_consensus_price(CR_grouped_markets, CR_outcome_name)
                    if CR_consensus_price is not None:
                        CR_market_consensus[CR_outcome_name] = CR_consensus_price

                CR_event_consensus[CR_market_name] = CR_market_consensus

            CR_consensus_data[CR_event_id] = CR_event_consensus

        return {
            'CR_success': True,
            'CR_result': CR_consensus_data,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


def tool_CR_compute_market_efficiency(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Compute market efficiency scores for all bookmakers"""
    try:
        CR_all_efficiency = {}
        CR_events = CR_snapshot.get('CR_events', [])

        for CR_event in CR_events:
            CR_event_id = CR_event.get('CR_event_id', '')
            CR_markets = CR_event.get('CR_markets', [])

            CR_efficiency = compute_CR_market_efficiency(CR_markets)
            CR_all_efficiency[CR_event_id] = CR_efficiency

        return {
            'CR_success': True,
            'CR_result': CR_all_efficiency,
            'CR_timestamp': datetime.now().isoformat()
        }
    except Exception as CR_error:
        return {
            'CR_success': False,
            'CR_error': str(CR_error),
            'CR_timestamp': datetime.now().isoformat()
        }


# Registry of all available tools with CR_ prefix
CR_TOOL_REGISTRY = {
    'CR_compute_implied_probability': tool_CR_compute_implied_probability,
    'CR_compute_vig': tool_CR_compute_vig,
    'CR_convert_odds': tool_CR_convert_odds,
    'CR_detect_arbitrage': tool_CR_detect_arbitrage,
    'CR_detect_stale_lines': tool_CR_detect_stale_lines,
    'CR_detect_outliers': tool_CR_detect_outliers,
    'CR_detect_value_edges': tool_CR_detect_value_edges,
    'CR_compute_best_lines': tool_CR_compute_best_lines,
    'CR_compute_consensus': tool_CR_compute_consensus,
    'CR_compute_market_efficiency': tool_CR_compute_market_efficiency,
}


def get_CR_tool(CR_tool_name: str):
    """Get a tool by name"""
    return CR_TOOL_REGISTRY.get(CR_tool_name)


def list_CR_tools() -> List[str]:
    """List all available tools"""
    return list(CR_TOOL_REGISTRY.keys())

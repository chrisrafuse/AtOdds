"""
CR_ Data Contracts - Dictionary-based schema definitions
Phase 1: Data Structure Alignment - Dictionary schemas with validation
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime


SCHEMA_VERSION = "1.0"


def create_CR_outcome(
    CR_name: str,
    CR_price: Union[int, float],
    CR_implied_probability: Optional[float] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_outcome dictionary structure

    Args:
        CR_name: Outcome name (e.g., "Home +5.5", "Over 215.5")
        CR_price: American odds (e.g., -110, +150)
        CR_implied_probability: Optional implied probability (0.0 to 1.0)

    Returns:
        CR_outcome dictionary
    """
    outcome = {
        "CR_name": str(CR_name),
        "CR_price": int(CR_price) if isinstance(CR_price, int) else float(CR_price)
    }

    if CR_implied_probability is not None:
        outcome["CR_implied_probability"] = float(CR_implied_probability)

    return outcome


def create_CR_market(
    CR_name: str,
    CR_outcomes: List[Dict[str, Any]],
    CR_bookmaker: str,
    CR_last_update: Optional[str] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_market dictionary structure

    Args:
        CR_name: Market name (e.g., "spread", "moneyline", "total")
        CR_outcomes: List of CR_outcome dictionaries (must have exactly 2)
        CR_bookmaker: Bookmaker name
        CR_last_update: Optional ISO datetime string

    Returns:
        CR_market dictionary
    """
    if len(CR_outcomes) != 2:
        raise ValueError(f"CR_market must have exactly 2 outcomes, got {len(CR_outcomes)}")

    market = {
        "CR_name": str(CR_name),
        "CR_outcomes": list(CR_outcomes),
        "CR_bookmaker": str(CR_bookmaker)
    }

    if CR_last_update is not None:
        market["CR_last_update"] = str(CR_last_update)

    return market


def create_CR_event(
    CR_event_id: str,
    CR_event_name: str,
    CR_sport: str,
    CR_markets: List[Dict[str, Any]],
    CR_commence_time: Optional[str] = None,
    CR_home_team: Optional[str] = None,
    CR_away_team: Optional[str] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_event dictionary structure

    Args:
        CR_event_id: Unique event identifier
        CR_event_name: Event name (e.g., "Lakers vs Warriors")
        CR_sport: Sport name (e.g., "NBA", "NFL")
        CR_markets: List of CR_market dictionaries
        CR_commence_time: Optional ISO datetime string
        CR_home_team: Optional home team name
        CR_away_team: Optional away team name

    Returns:
        CR_event dictionary
    """
    event = {
        "CR_event_id": str(CR_event_id),
        "CR_event_name": str(CR_event_name),
        "CR_sport": str(CR_sport),
        "CR_markets": list(CR_markets)
    }

    if CR_commence_time is not None:
        event["CR_commence_time"] = str(CR_commence_time)

    if CR_home_team is not None:
        event["CR_home_team"] = str(CR_home_team)

    if CR_away_team is not None:
        event["CR_away_team"] = str(CR_away_team)

    return event


def create_CR_finding(
    CR_type: str,
    CR_description: str,
    CR_confidence: float,
    CR_event_id: str,
    CR_market_name: str,
    CR_bookmakers: List[str],
    CR_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Factory function for CR_finding dictionary structure

    Args:
        CR_type: Finding type ('arbitrage', 'value_edge', 'stale_line', 'outlier')
        CR_description: Human-readable description
        CR_confidence: Confidence score (0.0 to 1.0)
        CR_event_id: Associated event ID
        CR_market_name: Associated market name
        CR_bookmakers: List of bookmaker names involved
        CR_details: Additional details dictionary

    Returns:
        CR_finding dictionary
    """
    valid_types = ['arbitrage', 'value_edge', 'stale_line', 'outlier']
    if CR_type not in valid_types:
        raise ValueError(f"CR_type must be one of {valid_types}, got '{CR_type}'")

    if not 0.0 <= CR_confidence <= 1.0:
        raise ValueError(f"CR_confidence must be between 0.0 and 1.0, got {CR_confidence}")

    return {
        "CR_type": str(CR_type),
        "CR_description": str(CR_description),
        "CR_confidence": float(CR_confidence),
        "CR_event_id": str(CR_event_id),
        "CR_market_name": str(CR_market_name),
        "CR_bookmakers": list(CR_bookmakers),
        "CR_details": dict(CR_details)
    }


def create_CR_snapshot(
    CR_events: List[Dict[str, Any]],
    CR_timestamp: str,
    CR_source: str,
    CR_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_snapshot dictionary structure

    Args:
        CR_events: List of CR_event dictionaries
        CR_timestamp: ISO datetime string
        CR_source: Data source identifier
        CR_metadata: Optional metadata dictionary

    Returns:
        CR_snapshot dictionary
    """
    snapshot = {
        "CR_events": list(CR_events),
        "CR_timestamp": str(CR_timestamp),
        "CR_source": str(CR_source)
    }

    if CR_metadata is not None:
        snapshot["CR_metadata"] = dict(CR_metadata)

    return snapshot


def create_CR_briefing(
    CR_summary: str,
    CR_total_events: int,
    CR_total_markets: int,
    CR_findings: List[Dict[str, Any]],
    CR_consensus_prices: Dict[str, Any],
    CR_timestamp: str,
    CR_recommendations: Optional[List[Dict[str, Any]]] = None,
    CR_performance_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_briefing dictionary structure

    Args:
        CR_summary: Executive summary text
        CR_total_events: Total number of events analyzed
        CR_total_markets: Total number of markets analyzed
        CR_findings: List of CR_finding dictionaries
        CR_consensus_prices: Dictionary of consensus prices
        CR_timestamp: ISO datetime string
        CR_recommendations: Optional list of recommendations
        CR_performance_metrics: Optional performance metrics

    Returns:
        CR_briefing dictionary
    """
    briefing = {
        "CR_summary": str(CR_summary),
        "CR_total_events": int(CR_total_events),
        "CR_total_markets": int(CR_total_markets),
        "CR_findings": list(CR_findings),
        "CR_consensus_prices": dict(CR_consensus_prices),
        "CR_timestamp": str(CR_timestamp)
    }

    if CR_recommendations is not None:
        briefing["CR_recommendations"] = list(CR_recommendations)

    if CR_performance_metrics is not None:
        briefing["CR_performance_metrics"] = dict(CR_performance_metrics)

    return briefing


def create_CR_step(
    CR_step_name: str,
    CR_timestamp: str,
    CR_duration_ms: int,
    CR_status: str,
    CR_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Factory function for CR_step dictionary structure

    Args:
        CR_step_name: Step name
        CR_timestamp: ISO datetime string
        CR_duration_ms: Duration in milliseconds
        CR_status: Status ('success', 'error', 'pending')
        CR_details: Optional details dictionary

    Returns:
        CR_step dictionary
    """
    valid_statuses = ['success', 'error', 'pending']
    if CR_status not in valid_statuses:
        raise ValueError(f"CR_status must be one of {valid_statuses}, got '{CR_status}'")

    step = {
        "CR_step_name": str(CR_step_name),
        "CR_timestamp": str(CR_timestamp),
        "CR_duration_ms": int(CR_duration_ms),
        "CR_status": str(CR_status)
    }

    if CR_details is not None:
        step["CR_details"] = dict(CR_details)

    return step


def create_CR_tool_call(
    CR_tool_name: str,
    CR_timestamp: str,
    CR_inputs: Dict[str, Any],
    CR_outputs: Dict[str, Any],
    CR_duration_ms: int,
    CR_status: str
) -> Dict[str, Any]:
    """
    Factory function for CR_tool_call dictionary structure

    Args:
        CR_tool_name: Tool name
        CR_timestamp: ISO datetime string
        CR_inputs: Input parameters dictionary
        CR_outputs: Output results dictionary
        CR_duration_ms: Duration in milliseconds
        CR_status: Status ('success', 'error')

    Returns:
        CR_tool_call dictionary
    """
    valid_statuses = ['success', 'error']
    if CR_status not in valid_statuses:
        raise ValueError(f"CR_status must be one of {valid_statuses}, got '{CR_status}'")

    return {
        "CR_tool_name": str(CR_tool_name),
        "CR_timestamp": str(CR_timestamp),
        "CR_inputs": dict(CR_inputs),
        "CR_outputs": dict(CR_outputs),
        "CR_duration_ms": int(CR_duration_ms),
        "CR_status": str(CR_status)
    }


def validate_CR_structure(data: Dict[str, Any], structure_type: str) -> bool:
    """
    Validate a CR_ data structure using the validation framework

    Args:
        data: Dictionary to validate
        structure_type: Type of structure (e.g., "CR_event", "CR_market")

    Returns:
        True if valid, raises ValueError if invalid
    """
    try:
        from packages.validation.structure_validator import StructureValidator

        validator = StructureValidator()
        is_valid, errors = validator.validate_structure(data, structure_type)

        if not is_valid:
            error_msg = f"Validation failed for {structure_type}:\n"
            error_msg += "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)

        return True

    except ImportError:
        return True


def get_schema_version() -> str:
    """Get the current schema version"""
    return SCHEMA_VERSION


def get_supported_structures() -> List[str]:
    """Get list of supported CR_ structure types"""
    return [
        "CR_outcome",
        "CR_market",
        "CR_event",
        "CR_finding",
        "CR_snapshot",
        "CR_briefing",
        "CR_step",
        "CR_tool_call"
    ]

"""
Briefing schema validation - lightweight validation
"""

from typing import Dict, Any, List
import json
from datetime import datetime

from data.contracts import CR_finding


def validate_briefing_structure(briefing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate briefing structure
    
    Args:
        briefing_data: Briefing data to validate
        
    Returns:
        Validation result with errors if any
    """
    errors = []
    warnings = []
    
    # Required top-level fields
    required_fields = ['metadata', 'summary', 'findings']
    for field in required_fields:
        if field not in briefing_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate metadata
    if 'metadata' in briefing_data:
        metadata = briefing_data['metadata']
        if 'generated_at' not in metadata:
            errors.append("Missing metadata.generated_at")
        elif not isinstance(metadata['generated_at'], str):
            errors.append("metadata.generated_at must be a string")
        
        if 'total_findings' not in metadata:
            errors.append("Missing metadata.total_findings")
        elif not isinstance(metadata['total_findings'], int):
            errors.append("metadata.total_findings must be an integer")
    
    # Validate summary
    if 'summary' in briefing_data:
        summary = briefing_data['summary']
        required_summary_fields = ['total_findings', 'by_type', 'by_confidence']
        for field in required_summary_fields:
            if field not in summary:
                errors.append(f"Missing summary.{field}")
        
        # Validate confidence categories
        if 'by_confidence' in summary:
            confidence = summary['by_confidence']
            required_conf_fields = ['high', 'medium', 'low']
            for field in required_conf_fields:
                if field not in confidence:
                    errors.append(f"Missing summary.by_confidence.{field}")
                elif not isinstance(confidence[field], int):
                    errors.append(f"summary.by_confidence.{field} must be an integer")
    
    # Validate findings
    if 'findings' in briefing_data:
        findings = briefing_data['findings']
        if not isinstance(findings, list):
            errors.append("findings must be a list")
        else:
            for i, finding in enumerate(findings):
                finding_errors = validate_finding_structure(finding, f"findings[{i}]")
                errors.extend(finding_errors)
    
    # Check for consistency
    if 'metadata' in briefing_data and 'summary' in briefing_data:
        if briefing_data['metadata'].get('total_findings') != briefing_data['summary'].get('total_findings'):
            warnings.append("Inconsistent total_findings between metadata and summary")
        
        if len(briefing_data.get('findings', [])) != briefing_data['summary'].get('total_findings'):
            warnings.append("Inconsistent findings count with summary total")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_finding_structure(finding: Dict[str, Any], path: str = "finding") -> List[str]:
    """
    Validate individual finding structure
    
    Args:
        finding: Finding data to validate
        path: Path for error reporting
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['type', 'description', 'confidence', 'event_id', 'market_name', 'bookmakers']
    for field in required_fields:
        if field not in finding:
            errors.append(f"Missing {path}.{field}")
    
    # Validate types
    if 'type' in finding and not isinstance(finding['type'], str):
        errors.append(f"{path}.type must be a string")
    
    if 'description' in finding and not isinstance(finding['description'], str):
        errors.append(f"{path}.description must be a string")
    
    if 'confidence' in finding:
        confidence = finding['confidence']
        if not isinstance(confidence, (int, float)):
            errors.append(f"{path}.confidence must be a number")
        elif not (0 <= confidence <= 1):
            errors.append(f"{path}.confidence must be between 0 and 1")
    
    if 'event_id' in finding and not isinstance(finding['event_id'], str):
        errors.append(f"{path}.event_id must be a string")
    
    if 'market_name' in finding and not isinstance(finding['market_name'], str):
        errors.append(f"{path}.market_name must be a string")
    
    if 'bookmakers' in finding:
        if not isinstance(finding['bookmakers'], list):
            errors.append(f"{path}.bookmakers must be a list")
        elif not all(isinstance(b, str) for b in finding['bookmakers']):
            errors.append(f"{path}.bookmakers must contain only strings")
    
    # Validate finding type
    if 'type' in finding:
        valid_types = ['arbitrage', 'value_edge', 'stale_line', 'outlier']
        if finding['type'] not in valid_types:
            errors.append(f"{path}.type must be one of: {', '.join(valid_types)}")
    
    return errors


def validate_snapshot_structure(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate snapshot structure
    
    Args:
        snapshot: Snapshot data to validate
        
    Returns:
        Validation result
    """
    errors = []
    warnings = []
    
    # Required fields
    required_fields = ['events', 'timestamp', 'source']
    for field in required_fields:
        if field not in snapshot:
            errors.append(f"Missing required field: {field}")
    
    # Validate events
    if 'events' in snapshot:
        events = snapshot['events']
        if not isinstance(events, list):
            errors.append("events must be a list")
        elif len(events) == 0:
            warnings.append("No events in snapshot")
        else:
            for i, event in enumerate(events):
                event_errors = validate_event_structure(event, f"events[{i}]")
                errors.extend(event_errors)
    
    # Validate timestamp
    if 'timestamp' in snapshot:
        timestamp = snapshot['timestamp']
        if isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                errors.append("timestamp must be valid ISO format")
        elif not isinstance(timestamp, datetime):
            errors.append("timestamp must be datetime or ISO string")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def validate_event_structure(event: Dict[str, Any], path: str = "event") -> List[str]:
    """
    Validate event structure
    
    Args:
        event: Event data to validate
        path: Path for error reporting
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['id', 'name', 'markets']
    for field in required_fields:
        if field not in event:
            errors.append(f"Missing {path}.{field}")
    
    # Validate markets
    if 'markets' in event:
        markets = event['markets']
        if not isinstance(markets, list):
            errors.append(f"{path}.markets must be a list")
        elif len(markets) == 0:
            errors.append(f"{path}.markets cannot be empty")
        else:
            for i, market in enumerate(markets):
                market_errors = validate_market_structure(market, f"{path}.markets[{i}]")
                errors.extend(market_errors)
    
    return errors


def validate_market_structure(market: Dict[str, Any], path: str = "market") -> List[str]:
    """
    Validate market structure
    
    Args:
        market: Market data to validate
        path: Path for error reporting
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'outcomes', 'bookmaker']
    for field in required_fields:
        if field not in market:
            errors.append(f"Missing {path}.{field}")
    
    # Validate outcomes
    if 'outcomes' in market:
        outcomes = market['outcomes']
        if not isinstance(outcomes, list):
            errors.append(f"{path}.outcomes must be a list")
        elif len(outcomes) < 2:
            errors.append(f"{path}.outcomes must have at least 2 outcomes")
        else:
            for i, outcome in enumerate(outcomes):
                outcome_errors = validate_outcome_structure(outcome, f"{path}.outcomes[{i}]")
                errors.extend(outcome_errors)
    
    return errors


def validate_outcome_structure(outcome: Dict[str, Any], path: str = "outcome") -> List[str]:
    """
    Validate outcome structure
    
    Args:
        outcome: Outcome data to validate
        path: Path for error reporting
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in outcome:
            errors.append(f"Missing {path}.{field}")
    
    # Validate price
    if 'price' in outcome:
        price = outcome['price']
        if not isinstance(price, (int, float)):
            errors.append(f"{path}.price must be a number")
        elif price <= 0:
            errors.append(f"{path}.price must be positive")
        elif price > 1000:  # Reasonable upper limit
            errors.append(f"{path}.price seems unreasonably high")
    
    return errors


def quick_validate(data: Any, schema_type: str) -> bool:
    """
    Quick validation check
    
    Args:
        data: Data to validate
        schema_type: Type of schema ('briefing', 'snapshot', 'finding')
        
    Returns:
        True if valid, False otherwise
    """
    if schema_type == 'briefing':
        result = validate_briefing_structure(data)
    elif schema_type == 'snapshot':
        result = validate_snapshot_structure(data)
    elif schema_type == 'finding':
        result = {'valid': len(validate_finding_structure(data)) == 0, 'errors': [], 'warnings': []}
    else:
        return False
    
    return result['valid']

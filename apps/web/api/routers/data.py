"""
Data Router for AtOdds API
Phase 6: Endpoints for data operations (sample, validate, schema)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import json
import os
from datetime import datetime

from ..models.requests import CR_ValidationRequest
from ..models.responses import CR_SuccessResponse

# Import core engine modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from packages.data.loader import load_data
from packages.data.contracts import validate_CR_structure


router = APIRouter(prefix="/data", tags=["data"])


@router.get("/sample")
async def get_sample_data() -> Dict[str, Any]:
    """
    Get sample odds data for testing

    Returns:
        CR_SuccessResponse with sample CR_snapshot
    """
    try:
        # Load sample data from file
        CR_sample_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..',
            'data',
            'sample_odds.json'
        )

        CR_snapshot = load_data(CR_sample_path)

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_snapshot": CR_snapshot
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "SAMPLE_DATA_ERROR",
                    "CR_message": f"Failed to load sample data: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/validate")
async def validate_data(request: CR_ValidationRequest) -> Dict[str, Any]:
    """
    Validate CR_ data structure

    Args:
        request: CR_ValidationRequest with snapshot to validate

    Returns:
        CR_SuccessResponse with validation results
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_errors = []
        CR_warnings = []

        # Validate snapshot structure
        try:
            validate_CR_structure(CR_snapshot, "CR_snapshot")
            CR_is_valid = True
        except ValueError as e:
            CR_is_valid = False
            CR_errors.append(str(e))

        # Additional validation checks
        if not CR_snapshot.get('CR_events'):
            CR_warnings.append("No CR_events found in snapshot")
        elif len(CR_snapshot['CR_events']) == 0:
            CR_warnings.append("CR_events array is empty")

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_is_valid": CR_is_valid,
                "CR_errors": CR_errors,
                "CR_warnings": CR_warnings,
                "CR_event_count": len(CR_snapshot.get('CR_events', []))
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "VALIDATION_ERROR",
                    "CR_message": f"Validation failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.get("/schema")
async def get_schema() -> Dict[str, Any]:
    """
    Get CR_ schema definitions

    Returns:
        CR_SuccessResponse with schema definitions
    """
    try:
        CR_schemas = {
            "CR_outcome": {
                "CR_name": "string",
                "CR_price": "number (American odds)",
                "CR_implied_probability": "number (0.0-1.0, optional)"
            },
            "CR_market": {
                "CR_name": "string (e.g., 'moneyline_DraftKings')",
                "CR_outcomes": "array of CR_outcome (exactly 2)",
                "CR_bookmaker": "string",
                "CR_last_update": "ISO datetime string (optional)"
            },
            "CR_event": {
                "CR_event_id": "string",
                "CR_event_name": "string",
                "CR_sport": "string",
                "CR_markets": "array of CR_market",
                "CR_commence_time": "ISO datetime string (optional)",
                "CR_home_team": "string (optional)",
                "CR_away_team": "string (optional)"
            },
            "CR_snapshot": {
                "CR_events": "array of CR_event",
                "CR_timestamp": "ISO datetime string",
                "CR_source": "string"
            },
            "CR_finding": {
                "CR_type": "string (arbitrage|value_edge|outlier|stale_line)",
                "CR_event_id": "string",
                "CR_market_name": "string",
                "CR_confidence": "number (0.0-1.0)",
                "CR_description": "string",
                "CR_metadata": "object (type-specific data)"
            }
        }

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_schemas": CR_schemas,
                "CR_version": "1.0"
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "SCHEMA_ERROR",
                    "CR_message": f"Failed to retrieve schemas: {str(e)}",
                    "CR_details": {}
                }
            }
        )

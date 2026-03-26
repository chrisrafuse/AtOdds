"""
Reporting Router for AtOdds API
Phase 6: Endpoints for briefing generation
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from ..models.requests import CR_BriefingRequest

# Import core engine modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from packages.reporting.briefing import generate_CR_briefing, generate_CR_json_briefing


router = APIRouter(prefix="/report", tags=["reporting"])


@router.post("/briefing")
async def generate_briefing(request: CR_BriefingRequest) -> Dict[str, Any]:
    """
    Generate text briefing from CR_ findings

    Args:
        request: CR_BriefingRequest with findings and optional snapshot

    Returns:
        CR_SuccessResponse with text briefing
    """
    try:
        CR_findings = request.CR_findings
        CR_snapshot = request.CR_snapshot

        CR_rankings = getattr(request, 'CR_sportsbook_rankings', None) or []

        # Generate text briefing
        CR_briefing_text = generate_CR_briefing(CR_findings, CR_snapshot, CR_rankings)

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_briefing": CR_briefing_text,
                "CR_format": "text",
                "CR_findings_count": len(CR_findings),
                "CR_sportsbook_rankings": CR_rankings
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
                    "CR_code": "BRIEFING_ERROR",
                    "CR_message": f"Briefing generation failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/json")
async def generate_json_briefing(request: CR_BriefingRequest) -> Dict[str, Any]:
    """
    Generate JSON briefing from CR_ findings

    Args:
        request: CR_BriefingRequest with findings and optional snapshot

    Returns:
        CR_SuccessResponse with structured JSON briefing
    """
    try:
        CR_findings = request.CR_findings
        CR_snapshot = request.CR_snapshot

        # Generate JSON briefing
        CR_briefing_json = generate_CR_json_briefing(CR_findings, CR_snapshot)

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_briefing": CR_briefing_json,
                "CR_format": "json",
                "CR_findings_count": len(CR_findings)
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
                    "CR_code": "JSON_BRIEFING_ERROR",
                    "CR_message": f"JSON briefing generation failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.get("/template")
async def get_briefing_template() -> Dict[str, Any]:
    """
    Get briefing template structure

    Returns:
        CR_SuccessResponse with template information
    """
    try:
        CR_template = {
            "CR_sections": [
                "summary",
                "findings",
                "detailed_breakdown",
                "bookmaker_analysis",
                "recommendations"
            ],
            "CR_fields": {
                "summary": {
                    "CR_total_findings": "number",
                    "CR_by_type": "object (counts by finding type)",
                    "CR_high_confidence_count": "number"
                },
                "findings": {
                    "CR_type": "string",
                    "CR_event_id": "string",
                    "CR_market_name": "string",
                    "CR_confidence": "number",
                    "CR_description": "string",
                    "CR_metadata": "object"
                },
                "recommendations": "array of strings"
            },
            "CR_formats": ["text", "json"]
        }

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_template": CR_template
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
                    "CR_code": "TEMPLATE_ERROR",
                    "CR_message": f"Template retrieval failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )

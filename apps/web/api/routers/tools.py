"""
Tools Router for AtOdds API
Phase 6: Endpoints for individual tool execution
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime

from ..models.requests import CR_ToolRequest

# Import core engine modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from packages.core_engine.detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edge,
    detect_CR_outlier,
    detect_CR_stale_line
)
from packages.core_engine.consensus import compute_CR_best_lines


router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/arbitrage")
async def detect_arbitrage(request: CR_ToolRequest) -> Dict[str, Any]:
    """
    Detect arbitrage opportunities in CR_ snapshot

    Args:
        request: CR_ToolRequest with snapshot

    Returns:
        CR_SuccessResponse with arbitrage findings
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_findings = detect_CR_arbitrage(CR_snapshot.get('CR_events', []))

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_findings": CR_findings,
                "CR_count": len(CR_findings)
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_tool": "detect_CR_arbitrage"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "ARBITRAGE_DETECTION_ERROR",
                    "CR_message": f"Arbitrage detection failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/value")
async def detect_value_edges(request: CR_ToolRequest) -> Dict[str, Any]:
    """
    Detect value edges in CR_ snapshot

    Args:
        request: CR_ToolRequest with snapshot

    Returns:
        CR_SuccessResponse with value edge findings
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_findings = detect_CR_value_edge(CR_snapshot.get('CR_events', []))

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_findings": CR_findings,
                "CR_count": len(CR_findings)
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_tool": "detect_CR_value_edges"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "VALUE_DETECTION_ERROR",
                    "CR_message": f"Value edge detection failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/outliers")
async def detect_outliers(request: CR_ToolRequest) -> Dict[str, Any]:
    """
    Detect statistical outliers in CR_ snapshot

    Args:
        request: CR_ToolRequest with snapshot

    Returns:
        CR_SuccessResponse with outlier findings
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_findings = detect_CR_outlier(CR_snapshot.get('CR_events', []))

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_findings": CR_findings,
                "CR_count": len(CR_findings)
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_tool": "detect_CR_outliers"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "OUTLIER_DETECTION_ERROR",
                    "CR_message": f"Outlier detection failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/stale")
async def detect_stale_lines(request: CR_ToolRequest) -> Dict[str, Any]:
    """
    Detect stale lines in CR_ snapshot

    Args:
        request: CR_ToolRequest with snapshot

    Returns:
        CR_SuccessResponse with stale line findings
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_findings = detect_CR_stale_line(CR_snapshot.get('CR_events', []))

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_findings": CR_findings,
                "CR_count": len(CR_findings)
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_tool": "detect_CR_stale_lines"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "STALE_DETECTION_ERROR",
                    "CR_message": f"Stale line detection failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/consensus")
async def calculate_consensus(request: CR_ToolRequest) -> Dict[str, Any]:
    """
    Calculate consensus pricing for CR_ snapshot

    Args:
        request: CR_ToolRequest with snapshot

    Returns:
        CR_SuccessResponse with consensus data
    """
    try:
        CR_snapshot = request.CR_snapshot
        CR_consensus = compute_CR_best_lines(CR_snapshot.get('CR_events', []))

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_consensus": CR_consensus
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_tool": "compute_CR_best_lines"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "CONSENSUS_ERROR",
                    "CR_message": f"Consensus calculation failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )

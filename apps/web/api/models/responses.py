"""
Response Models for AtOdds API
Phase 6: Pydantic models for API responses with CR_ prefix compliance
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class CR_Metadata(BaseModel):
    """Standard metadata for all responses"""
    CR_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Response timestamp in ISO format"
    )
    CR_version: str = Field(
        default="1.0",
        description="API version"
    )
    CR_execution_time_ms: Optional[int] = Field(
        default=None,
        description="Execution time in milliseconds"
    )


class CR_AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    CR_status: str = Field(
        default="success",
        description="Response status"
    )
    CR_data: Dict[str, Any] = Field(
        ...,
        description="Analysis results including CR_findings and CR_findings_summary"
    )
    CR_metadata: CR_Metadata = Field(
        default_factory=CR_Metadata,
        description="Response metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "CR_status": "success",
                "CR_data": {
                    "CR_findings": [
                        {
                            "CR_type": "arbitrage",
                            "CR_event_id": "nba_20260326_lal_bos",
                            "CR_confidence": 0.95
                        }
                    ],
                    "CR_findings_summary": {
                        "CR_total_findings": 1,
                        "CR_by_type": {"arbitrage": 1}
                    }
                },
                "CR_metadata": {
                    "CR_timestamp": "2026-03-26T15:00:00Z",
                    "CR_version": "1.0",
                    "CR_execution_time_ms": 234
                }
            }
        }


class CR_ValidationResponse(BaseModel):
    """Response model for validation results"""
    CR_status: str = Field(default="success")
    CR_data: Dict[str, Any] = Field(
        ...,
        description="Validation results"
    )
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)


class CR_BriefingResponse(BaseModel):
    """Response model for briefing generation"""
    CR_status: str = Field(default="success")
    CR_data: Dict[str, Any] = Field(
        ...,
        description="Generated briefing (text or JSON)"
    )
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)


class CR_ChatSessionResponse(BaseModel):
    """Response model for chat session creation"""
    CR_status: str = Field(default="success")
    CR_data: Dict[str, Any] = Field(
        ...,
        description="Session information including CR_session_id"
    )
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)


class CR_ChatAnswerResponse(BaseModel):
    """Response model for chat answers"""
    CR_status: str = Field(default="success")
    CR_data: Dict[str, Any] = Field(
        ...,
        description="Chat answer with CR_answer, CR_sources, CR_confidence"
    )
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)


class CR_ErrorDetail(BaseModel):
    """Error detail structure"""
    CR_code: str = Field(..., description="Error code")
    CR_message: str = Field(..., description="Error message")
    CR_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )


class CR_ErrorResponse(BaseModel):
    """Response model for errors"""
    CR_status: str = Field(default="error")
    CR_error: CR_ErrorDetail = Field(..., description="Error information")
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)
    
    class Config:
        json_schema_extra = {
            "example": {
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "VALIDATION_ERROR",
                    "CR_message": "Invalid CR_ snapshot structure",
                    "CR_details": {
                        "CR_field": "CR_events",
                        "CR_reason": "Required field missing"
                    }
                },
                "CR_metadata": {
                    "CR_timestamp": "2026-03-26T15:00:00Z",
                    "CR_version": "1.0"
                }
            }
        }


class CR_HealthResponse(BaseModel):
    """Response model for health check"""
    CR_status: str = Field(default="healthy")
    CR_version: str = Field(default="1.0")
    CR_uptime_seconds: Optional[int] = Field(default=None)
    CR_timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class CR_SuccessResponse(BaseModel):
    """Generic success response"""
    CR_status: str = Field(default="success")
    CR_data: Dict[str, Any] = Field(default_factory=dict)
    CR_metadata: CR_Metadata = Field(default_factory=CR_Metadata)

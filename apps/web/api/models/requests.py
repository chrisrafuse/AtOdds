"""
Request Models for AtOdds API
Phase 6: Pydantic models for API requests with CR_ prefix compliance
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime


class CR_AnalysisRequest(BaseModel):
    """Request model for odds analysis"""
    CR_snapshot: Dict[str, Any] = Field(
        ...,
        description="CR_ snapshot containing events and markets to analyze"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "CR_snapshot": {
                    "CR_events": [
                        {
                            "CR_event_id": "nba_20260326_lal_bos",
                            "CR_event_name": "Lakers vs Celtics",
                            "CR_sport": "NBA",
                            "CR_markets": [],
                            "CR_commence_time": "2026-03-26T19:00:00Z"
                        }
                    ],
                    "CR_timestamp": "2026-03-26T15:00:00Z",
                    "CR_source": "api_request"
                }
            }
        }


class CR_UploadRequest(BaseModel):
    """Request model for file upload (handled by FastAPI UploadFile)"""
    pass  # File upload uses FastAPI's UploadFile directly


class CR_ValidationRequest(BaseModel):
    """Request model for data validation"""
    CR_snapshot: Dict[str, Any] = Field(
        ...,
        description="CR_ snapshot to validate"
    )
    CR_strict: bool = Field(
        default=True,
        description="Whether to use strict validation"
    )


class CR_BriefingRequest(BaseModel):
    """Request model for briefing generation"""
    CR_findings: List[Dict[str, Any]] = Field(
        ...,
        description="List of CR_ findings to include in briefing"
    )
    CR_snapshot: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional CR_ snapshot for additional context"
    )
    CR_format: str = Field(
        default="text",
        description="Output format: 'text' or 'json'"
    )
    CR_sportsbook_rankings: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Pre-computed sportsbook rankings to include in briefing"
    )

    @validator('CR_format')
    def validate_format(cls, v):
        if v not in ['text', 'json']:
            raise ValueError("CR_format must be 'text' or 'json'")
        return v


class CR_ChatSessionRequest(BaseModel):
    """Request model for starting a chat session"""
    CR_snapshot: Dict[str, Any] = Field(
        ...,
        description="CR_ snapshot for chat context"
    )
    CR_findings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="CR_ findings for chat context"
    )
    CR_briefing_text: str = Field(
        default="",
        description="Previously generated briefing text to ground the conversation"
    )


class CR_ChatQuestionRequest(BaseModel):
    """Request model for asking a question in chat"""
    CR_session_id: str = Field(
        ...,
        description="Chat session ID"
    )
    CR_question: str = Field(
        ...,
        description="Question to ask",
        min_length=1,
        max_length=500
    )


class CR_ToolRequest(BaseModel):
    """Generic request model for tool execution"""
    CR_snapshot: Dict[str, Any] = Field(
        ...,
        description="CR_ snapshot to analyze with tool"
    )
    CR_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional tool-specific parameters"
    )

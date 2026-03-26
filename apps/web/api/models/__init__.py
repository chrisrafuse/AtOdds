"""
Pydantic Models for AtOdds API
Phase 6: Request and Response Models
"""

from .requests import (
    CR_AnalysisRequest,
    CR_UploadRequest,
    CR_ValidationRequest,
    CR_BriefingRequest,
    CR_ChatSessionRequest,
    CR_ChatQuestionRequest
)

from .responses import (
    CR_AnalysisResponse,
    CR_ValidationResponse,
    CR_BriefingResponse,
    CR_ChatSessionResponse,
    CR_ChatAnswerResponse,
    CR_ErrorResponse,
    CR_HealthResponse,
    CR_SuccessResponse
)

__all__ = [
    # Requests
    "CR_AnalysisRequest",
    "CR_UploadRequest",
    "CR_ValidationRequest",
    "CR_BriefingRequest",
    "CR_ChatSessionRequest",
    "CR_ChatQuestionRequest",
    # Responses
    "CR_AnalysisResponse",
    "CR_ValidationResponse",
    "CR_BriefingResponse",
    "CR_ChatSessionResponse",
    "CR_ChatAnswerResponse",
    "CR_ErrorResponse",
    "CR_HealthResponse",
    "CR_SuccessResponse",
]

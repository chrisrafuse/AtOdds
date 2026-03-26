"""
Chat Router for AtOdds API
Phase 6: Endpoints for interactive chat sessions
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timedelta
import uuid

from ..models.requests import CR_ChatSessionRequest, CR_ChatQuestionRequest

# Import core engine modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from packages.chat.chat_cr import start_CR_chat_session


router = APIRouter(prefix="/chat", tags=["chat"])


# In-memory session storage (Phase 6 - simple implementation)
CR_chat_sessions = {}


class CR_ChatSession:
    """CR_ compliant chat session"""

    def __init__(self, CR_session_id: str, CR_snapshot: Dict[str, Any], CR_findings: list, CR_briefing_text: str = ""):
        self.CR_session_id = CR_session_id
        self.CR_snapshot = CR_snapshot
        self.CR_findings = CR_findings
        self.CR_chat = start_CR_chat_session(CR_snapshot, CR_findings, CR_briefing_text)
        self.CR_created_at = datetime.now()
        self.CR_expires_at = datetime.now() + timedelta(hours=1)
        self.CR_message_history = []

    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now() > self.CR_expires_at


def cleanup_expired_sessions():
    """Remove expired sessions from storage"""
    CR_expired = [
        CR_sid for CR_sid, CR_session in CR_chat_sessions.items()
        if CR_session.is_expired()
    ]
    for CR_sid in CR_expired:
        del CR_chat_sessions[CR_sid]


@router.post("/session")
async def create_chat_session(request: CR_ChatSessionRequest) -> Dict[str, Any]:
    """
    Start a new chat session

    Args:
        request: CR_ChatSessionRequest with snapshot and findings

    Returns:
        CR_SuccessResponse with session ID and expiration
    """
    try:
        # Clean up expired sessions
        cleanup_expired_sessions()

        # Create new session ID
        CR_session_id = f"session_{uuid.uuid4().hex[:12]}"

        # Create session
        CR_session = CR_ChatSession(
            CR_session_id=CR_session_id,
            CR_snapshot=request.CR_snapshot,
            CR_findings=request.CR_findings,
            CR_briefing_text=request.CR_briefing_text
        )

        # Store session
        CR_chat_sessions[CR_session_id] = CR_session

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_session_id": CR_session_id,
                "CR_created_at": CR_session.CR_created_at.isoformat(),
                "CR_expires_at": CR_session.CR_expires_at.isoformat()
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
                    "CR_code": "SESSION_CREATE_ERROR",
                    "CR_message": f"Failed to create chat session: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/ask")
async def ask_question(request: CR_ChatQuestionRequest) -> Dict[str, Any]:
    """
    Ask a question in an existing chat session

    Args:
        request: CR_ChatQuestionRequest with session ID and question

    Returns:
        CR_SuccessResponse with answer, sources, and confidence
    """
    try:
        CR_session_id = request.CR_session_id
        CR_question = request.CR_question

        # Check if session exists
        if CR_session_id not in CR_chat_sessions:
            raise HTTPException(
                status_code=404,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "SESSION_NOT_FOUND",
                        "CR_message": f"Chat session not found: {CR_session_id}",
                        "CR_details": {"CR_session_id": CR_session_id}
                    }
                }
            )

        CR_session = CR_chat_sessions[CR_session_id]

        # Check if session expired
        if CR_session.is_expired():
            del CR_chat_sessions[CR_session_id]
            raise HTTPException(
                status_code=410,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "SESSION_EXPIRED",
                        "CR_message": "Chat session has expired",
                        "CR_details": {"CR_session_id": CR_session_id}
                    }
                }
            )

        # Get answer from chat
        CR_response = CR_session.CR_chat.answer_CR_question(CR_question)

        # Store in message history
        CR_session.CR_message_history.append({
            "CR_question": CR_question,
            "CR_answer": CR_response.get('CR_answer'),
            "CR_timestamp": datetime.now().isoformat()
        })

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_answer": CR_response.get('CR_answer'),
                "CR_sources": CR_response.get('CR_sources', []),
                "CR_confidence": CR_response.get('CR_confidence', 'medium'),
                "CR_tool_trace": CR_response.get('CR_tool_trace', []),
                "CR_provider": CR_response.get('CR_provider', 'unknown')
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_session_id": CR_session_id
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "CHAT_ERROR",
                    "CR_message": f"Chat failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.delete("/session/{session_id}")
async def end_chat_session(session_id: str) -> Dict[str, Any]:
    """
    End a chat session

    Args:
        session_id: Chat session ID to end

    Returns:
        CR_SuccessResponse with confirmation
    """
    try:
        if session_id not in CR_chat_sessions:
            raise HTTPException(
                status_code=404,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "SESSION_NOT_FOUND",
                        "CR_message": f"Chat session not found: {session_id}",
                        "CR_details": {"CR_session_id": session_id}
                    }
                }
            )

        # Get session info before deleting
        CR_session = CR_chat_sessions[session_id]
        CR_message_count = len(CR_session.CR_message_history)

        # Delete session
        del CR_chat_sessions[session_id]

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_message": "Session ended successfully",
                "CR_session_id": session_id,
                "CR_messages_exchanged": CR_message_count
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "SESSION_DELETE_ERROR",
                    "CR_message": f"Failed to end session: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.get("/sessions")
async def list_active_sessions() -> Dict[str, Any]:
    """
    List all active chat sessions (for debugging/monitoring)

    Returns:
        CR_SuccessResponse with active session count
    """
    try:
        # Clean up expired sessions first
        cleanup_expired_sessions()

        CR_active_count = len(CR_chat_sessions)
        CR_session_ids = list(CR_chat_sessions.keys())

        return {
            "CR_status": "success",
            "CR_data": {
                "CR_active_sessions": CR_active_count,
                "CR_session_ids": CR_session_ids
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
                    "CR_code": "SESSION_LIST_ERROR",
                    "CR_message": f"Failed to list sessions: {str(e)}",
                    "CR_details": {}
                }
            }
        )

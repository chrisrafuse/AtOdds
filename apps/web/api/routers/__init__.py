"""
API Routers for AtOdds Web API
Phase 6: FastAPI router modules
"""

from .analysis import router as analysis_router
from .data import router as data_router
from .tools import router as tools_router
from .reporting import router as reporting_router
from .chat import router as chat_router

__all__ = [
    "analysis_router",
    "data_router",
    "tools_router",
    "reporting_router",
    "chat_router",
]

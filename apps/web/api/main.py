"""
AtOdds FastAPI Application
Phase 6: Main API application with CR_ prefix compliance
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import time
import logging
from datetime import datetime
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; env vars still load from system environment

from .config import CR_settings
from .routers import (
    analysis_router,
    data_router,
    tools_router,
    reporting_router,
    chat_router
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, CR_settings.CR_log_level),
    format=CR_settings.CR_log_format
)
logger = logging.getLogger("atodds.api")

# Create FastAPI application
app = FastAPI(
    title=CR_settings.CR_api_title,
    version=CR_settings.CR_api_version,
    description=CR_settings.CR_api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS middleware — merge static defaults with any CORS_ORIGINS from env
_CR_extra_origins = [
    o.strip() for o in (CR_settings.CORS_ORIGINS or "").split(",") if o.strip()
]
_CR_all_origins = list(set(CR_settings.CR_cors_origins + _CR_extra_origins))
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CR_all_origins,
    allow_credentials=CR_settings.CR_cors_allow_credentials,
    allow_methods=CR_settings.CR_cors_allow_methods,
    allow_headers=CR_settings.CR_cors_allow_headers,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    CR_start_time = time.time()

    # Log request
    logger.info(f"CR_request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    CR_duration = time.time() - CR_start_time

    # Log response
    logger.info(
        f"CR_response: {response.status_code} "
        f"({CR_duration:.3f}s) {request.method} {request.url.path}"
    )

    return response

# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    logger.error(f"CR_unhandled_error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "CR_status": "error",
            "CR_error": {
                "CR_code": "INTERNAL_ERROR",
                "CR_message": "An internal error occurred",
                "CR_details": {}
            },
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": CR_settings.CR_api_version
            }
        }
    )

# Include routers
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(data_router, prefix="/api/v1")
app.include_router(tools_router, prefix="/api/v1")
app.include_router(reporting_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Health status with version and timestamp
    """
    return {
        "CR_status": "healthy",
        "CR_version": CR_settings.CR_api_version,
        "CR_timestamp": datetime.now().isoformat()
    }

# Mount static files (for Phase 7 frontend)
CR_static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(CR_static_path):
    app.mount("/static", StaticFiles(directory=CR_static_path), name="static")

    # Serve index.html at root
    @app.get("/")
    async def serve_frontend():
        """Serve the web frontend"""
        index_path = os.path.join(CR_static_path, "index.html")
        return FileResponse(index_path)
else:
    # Fallback API info if no frontend
    @app.get("/")
    async def root():
        """
        Root endpoint with API information

        Returns:
            API information and available endpoints
        """
        return {
            "CR_api": "AtOdds Odds Analysis API",
            "CR_version": CR_settings.CR_api_version,
            "CR_status": "operational",
            "CR_endpoints": {
                "CR_docs": "/docs",
                "CR_redoc": "/redoc",
                "CR_openapi": "/api/v1/openapi.json",
                "CR_health": "/health"
            },
            "CR_timestamp": datetime.now().isoformat()
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"CR_startup: AtOdds API v{CR_settings.CR_api_version}")
    logger.info(f"CR_config: Host={CR_settings.CR_api_host}, Port={CR_settings.CR_api_port}")
    logger.info(f"CR_cors: Origins={CR_settings.CR_cors_origins}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("CR_shutdown: AtOdds API shutting down")

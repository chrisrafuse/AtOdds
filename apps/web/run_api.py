#!/usr/bin/env python3
"""
AtOdds API Server Startup Script
Phase 6: Uvicorn server configuration for FastAPI application
"""

import uvicorn
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from apps.web.api.config import CR_settings


def main():
    """Start the AtOdds API server"""

    # PORT from env takes priority (set by Railway/Fly.io automatically)
    CR_port = int(os.environ.get("PORT", CR_settings.CR_api_port))
    CR_host = os.environ.get("HOST", CR_settings.CR_api_host)

    # Server configuration
    CR_config = {
        "app": "apps.web.api.main:app",
        "host": CR_host,
        "port": CR_port,
        "reload": CR_settings.CR_reload_on_change,
        "log_level": CR_settings.CR_log_level.lower(),
        "access_log": True,
        "workers": 1,  # Single worker for Windows compatibility
    }

    # Development settings
    if CR_settings.CR_debug_mode:
        CR_config["reload"] = True

    from packages.llm.factory import get_CR_provider_name
    print(f"🚀 Starting AtOdds API v{CR_settings.CR_api_version}")
    print(f"📍 Server: http://{CR_host}:{CR_port}")
    print(f"📚 Docs: http://{CR_host}:{CR_port}/docs")
    print(f"🔧 Mode: {'Development' if CR_settings.CR_debug_mode else 'Production'}")
    print(f"🤖 LLM Provider: {get_CR_provider_name()}")
    print(f"💻 Workers: 1 (Windows compatible)")

    # Start server
    uvicorn.run(**CR_config)


if __name__ == "__main__":
    main()

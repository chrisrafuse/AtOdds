"""
Analysis Router for AtOdds API
Phase 6: Endpoints for running odds analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any
import json
import time
from datetime import datetime

from ..models.requests import CR_AnalysisRequest
from ..models.responses import CR_AnalysisResponse, CR_ErrorResponse, CR_ErrorDetail, CR_Metadata

# Import core engine modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from packages.data.loader import load_data, DataLoadError, DataQualityError
from packages.agent.agent import execute_CR_analysis_pipeline


router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post("", response_model=CR_AnalysisResponse)
async def analyze_odds(request: CR_AnalysisRequest) -> Dict[str, Any]:
    """
    Run complete odds analysis pipeline on provided CR_ snapshot
    
    Args:
        request: CR_AnalysisRequest containing CR_snapshot
        
    Returns:
        CR_AnalysisResponse with findings and summary
        
    Raises:
        HTTPException: If analysis fails
    """
    CR_start_time = time.time()
    
    try:
        # Extract snapshot from request
        CR_snapshot = request.CR_snapshot
        
        # Validate snapshot has required fields
        if not CR_snapshot.get('CR_events'):
            raise HTTPException(
                status_code=400,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "INVALID_SNAPSHOT",
                        "CR_message": "CR_snapshot must contain CR_events",
                        "CR_details": {"CR_field": "CR_events"}
                    }
                }
            )
        
        # Run analysis pipeline
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        
        # Calculate execution time
        CR_execution_time = int((time.time() - CR_start_time) * 1000)
        
        # Return response
        return {
            "CR_status": "success",
            "CR_data": CR_results,
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0",
                "CR_execution_time_ms": CR_execution_time
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
                    "CR_code": "ANALYSIS_ERROR",
                    "CR_message": f"Analysis failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )


@router.post("/upload", response_model=CR_AnalysisResponse)
async def upload_and_analyze(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload JSON file and run analysis
    
    Args:
        file: Uploaded JSON file containing odds data
        
    Returns:
        CR_AnalysisResponse with findings and summary
        
    Raises:
        HTTPException: If file is invalid or analysis fails
    """
    CR_start_time = time.time()
    
    try:
        # Validate file extension
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "INVALID_FILE",
                        "CR_message": "File must be a JSON file",
                        "CR_details": {"CR_filename": file.filename}
                    }
                }
            )
        
        # Read file content
        CR_content = await file.read()
        
        # Check file size (10MB limit)
        CR_max_size = 10 * 1024 * 1024  # 10MB
        if len(CR_content) > CR_max_size:
            raise HTTPException(
                status_code=413,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "FILE_TOO_LARGE",
                        "CR_message": "File exceeds 10MB limit",
                        "CR_details": {"CR_size_bytes": len(CR_content)}
                    }
                }
            )
        
        # Parse JSON
        try:
            CR_data = json.loads(CR_content)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "CR_status": "error",
                    "CR_error": {
                        "CR_code": "INVALID_JSON",
                        "CR_message": f"Invalid JSON format: {str(e)}",
                        "CR_details": {}
                    }
                }
            )
        
        # Save to temporary file and load with data loader
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as CR_temp_file:
            json.dump(CR_data, CR_temp_file)
            CR_temp_path = CR_temp_file.name
        
        try:
            # Load and validate data
            CR_snapshot = load_data(CR_temp_path)
            
            # Run analysis
            CR_results = execute_CR_analysis_pipeline(CR_snapshot)
            
            # Calculate execution time
            CR_execution_time = int((time.time() - CR_start_time) * 1000)
            
            return {
                "CR_status": "success",
                "CR_data": CR_results,
                "CR_metadata": {
                    "CR_timestamp": datetime.now().isoformat(),
                    "CR_version": "1.0",
                    "CR_execution_time_ms": CR_execution_time
                }
            }
        finally:
            # Clean up temp file
            os.unlink(CR_temp_path)
            
    except HTTPException:
        raise
    except DataLoadError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "DATA_LOAD_ERROR",
                    "CR_message": str(e),
                    "CR_details": {}
                }
            }
        )
    except DataQualityError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "DATA_QUALITY_ERROR",
                    "CR_message": str(e),
                    "CR_details": {}
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "CR_status": "error",
                "CR_error": {
                    "CR_code": "UPLOAD_ERROR",
                    "CR_message": f"Upload failed: {str(e)}",
                    "CR_details": {}
                }
            }
        )

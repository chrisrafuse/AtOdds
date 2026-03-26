# PHASE_PLAN_6_WEB_API_LAYER.md
## Author: Chris Rafuse
## Duration: Week 6 (5-7 days)
## Purpose: Implement FastAPI REST API layer for web access
## Entry Criteria: Phase 5 completed, CLI fully functional
## Exit Criteria: RESTful API operational with CR_ compliance

---

# 🎯 PHASE OBJECTIVES

Implement a production-ready REST API layer using FastAPI:
- Create RESTful endpoints for all core functionality
- Maintain CR_ prefix compliance throughout API layer
- Enable real-time analysis via HTTP requests
- Support JSON request/response with CR_ structures
- Implement CORS for frontend integration
- Add comprehensive API documentation
- Ensure zero breaking changes to existing modules

---

# 📋 TASK CHECKLIST

## Day 1-2: FastAPI Core Setup

### API Server Foundation
- [ ] **FastAPI Application** (`apps/web/api/main.py`)
  - [ ] Initialize FastAPI app with CR_ metadata
  - [ ] Configure CORS middleware for frontend access
  - [ ] Set up CR_ request/response models
  - [ ] Add health check endpoint
  - [ ] Configure logging with CR_ prefix
  - [ ] Add error handling middleware
  - [ ] Create API versioning structure

- [ ] **API Configuration** (`apps/web/api/config.py`)
  - [ ] Define CR_ API settings
  - [ ] Configure CORS origins
  - [ ] Set up rate limiting parameters
  - [ ] Define API version constants
  - [ ] Add environment variable handling
  - [ ] Create CR_ configuration validation

- [ ] **Dependencies Setup** (`requirements-web.txt`)
  - [ ] Add FastAPI dependency
  - [ ] Add Uvicorn ASGI server
  - [ ] Add Pydantic for validation
  - [ ] Add python-multipart for file uploads
  - [ ] Add python-jose for JWT (optional)
  - [ ] Document all web dependencies

## Day 3-4: Core API Endpoints

### Analysis Endpoints
- [ ] **Analysis Router** (`apps/web/api/routers/analysis.py`)
  - [ ] `POST /api/v1/analyze` - Run complete analysis pipeline
    - [ ] Accept CR_ snapshot JSON in request body
    - [ ] Validate input with CR_ schemas
    - [ ] Execute `execute_CR_analysis_pipeline()`
    - [ ] Return CR_ findings and summary
    - [ ] Add execution time metadata
    - [ ] Handle errors with CR_ error structure
  
  - [ ] `POST /api/v1/analyze/upload` - Upload and analyze data file
    - [ ] Accept JSON file upload
    - [ ] Validate file with `load_data()`
    - [ ] Run analysis pipeline
    - [ ] Return CR_ results
    - [ ] Add file size limits
    - [ ] Handle upload errors

  - [ ] `GET /api/v1/analyze/status/{job_id}` - Check analysis status
    - [ ] Return CR_ job status
    - [ ] Include progress percentage
    - [ ] Return partial results if available
    - [ ] Add job expiration handling

### Data Endpoints
- [ ] **Data Router** (`apps/web/api/routers/data.py`)
  - [ ] `GET /api/v1/data/sample` - Get sample data
    - [ ] Return sample CR_ snapshot
    - [ ] Include metadata
    - [ ] Add caching headers
  
  - [ ] `POST /api/v1/data/validate` - Validate CR_ data structure
    - [ ] Accept CR_ snapshot JSON
    - [ ] Run `validate_CR_structure()`
    - [ ] Return validation results
    - [ ] Include detailed error messages

  - [ ] `GET /api/v1/data/schema` - Get CR_ schema definitions
    - [ ] Return all CR_ schemas
    - [ ] Include field descriptions
    - [ ] Add examples for each schema

### Tools Endpoints
- [ ] **Tools Router** (`apps/web/api/routers/tools.py`)
  - [ ] `POST /api/v1/tools/arbitrage` - Detect arbitrage
    - [ ] Accept CR_ snapshot
    - [ ] Run `detect_CR_arbitrage()`
    - [ ] Return CR_ findings
  
  - [ ] `POST /api/v1/tools/value` - Detect value edges
    - [ ] Accept CR_ snapshot
    - [ ] Run `detect_CR_value_edges()`
    - [ ] Return CR_ findings
  
  - [ ] `POST /api/v1/tools/outliers` - Detect outliers
    - [ ] Accept CR_ snapshot
    - [ ] Run `detect_CR_outliers()`
    - [ ] Return CR_ findings
  
  - [ ] `POST /api/v1/tools/stale` - Detect stale lines
    - [ ] Accept CR_ snapshot
    - [ ] Run `detect_CR_stale_lines()`
    - [ ] Return CR_ findings
  
  - [ ] `POST /api/v1/tools/consensus` - Calculate consensus
    - [ ] Accept CR_ snapshot
    - [ ] Run `compute_CR_best_lines()`
    - [ ] Return CR_ consensus data

## Day 5: Reporting & Chat Endpoints

### Reporting Endpoints
- [ ] **Reporting Router** (`apps/web/api/routers/reporting.py`)
  - [ ] `POST /api/v1/report/briefing` - Generate briefing
    - [ ] Accept CR_ findings array
    - [ ] Run `generate_CR_briefing()`
    - [ ] Return formatted text briefing
  
  - [ ] `POST /api/v1/report/json` - Generate JSON briefing
    - [ ] Accept CR_ findings array
    - [ ] Run `generate_CR_json_briefing()`
    - [ ] Return structured JSON briefing
  
  - [ ] `GET /api/v1/report/template` - Get briefing template
    - [ ] Return CR_ briefing template structure
    - [ ] Include field descriptions

### Chat Endpoints
- [ ] **Chat Router** (`apps/web/api/routers/chat.py`)
  - [ ] `POST /api/v1/chat/session` - Start chat session
    - [ ] Accept CR_ snapshot and findings
    - [ ] Create `CR_OddsChat` instance
    - [ ] Return session ID
    - [ ] Store session in memory/cache
  
  - [ ] `POST /api/v1/chat/ask` - Ask question
    - [ ] Accept session ID and question
    - [ ] Run `answer_CR_question()`
    - [ ] Return CR_ answer with sources
    - [ ] Update session history
  
  - [ ] `DELETE /api/v1/chat/session/{session_id}` - End session
    - [ ] Clean up session data
    - [ ] Return confirmation

## Day 6: API Models & Documentation

### Pydantic Models
- [ ] **Request Models** (`apps/web/api/models/requests.py`)
  - [ ] `CR_AnalysisRequest` - Analysis request model
  - [ ] `CR_ValidationRequest` - Validation request model
  - [ ] `CR_BriefingRequest` - Briefing generation request
  - [ ] `CR_ChatRequest` - Chat question request
  - [ ] Add field validation for all models
  - [ ] Include examples in docstrings

- [ ] **Response Models** (`apps/web/api/models/responses.py`)
  - [ ] `CR_AnalysisResponse` - Analysis results
  - [ ] `CR_ValidationResponse` - Validation results
  - [ ] `CR_BriefingResponse` - Briefing output
  - [ ] `CR_ChatResponse` - Chat answer
  - [ ] `CR_ErrorResponse` - Error structure
  - [ ] `CR_HealthResponse` - Health check
  - [ ] Add response examples

### API Documentation
- [ ] **OpenAPI Configuration** (`apps/web/api/main.py`)
  - [ ] Configure OpenAPI metadata
  - [ ] Add API description
  - [ ] Set up tags for endpoint groups
  - [ ] Add contact information
  - [ ] Configure Swagger UI
  - [ ] Configure ReDoc UI

- [ ] **API Documentation** (`docs/API.md`)
  - [ ] Document all endpoints
  - [ ] Include request/response examples
  - [ ] Add authentication guide (if applicable)
  - [ ] Document error codes
  - [ ] Add rate limiting information
  - [ ] Include cURL examples

## Day 7: Testing & Deployment

### API Testing
- [ ] **API Tests** (`tests/test_api_endpoints.py`)
  - [ ] Test all analysis endpoints
  - [ ] Test all data endpoints
  - [ ] Test all tools endpoints
  - [ ] Test reporting endpoints
  - [ ] Test chat endpoints
  - [ ] Test error handling
  - [ ] Test CORS configuration
  - [ ] Test rate limiting
  - [ ] Test file uploads
  - [ ] Test concurrent requests

- [ ] **Integration Tests** (`tests/test_api_integration.py`)
  - [ ] Test complete analysis workflow via API
  - [ ] Test data upload and analysis
  - [ ] Test chat session lifecycle
  - [ ] Test API with real sample data
  - [ ] Verify CR_ compliance in all responses

### Deployment Setup
- [ ] **Server Configuration** (`apps/web/run_api.py`)
  - [ ] Create Uvicorn server script
  - [ ] Configure host and port
  - [ ] Set up reload for development
  - [ ] Add production settings
  - [ ] Configure workers for production

- [ ] **Docker Support** (`apps/web/Dockerfile`)
  - [ ] Create Dockerfile for API
  - [ ] Set up multi-stage build
  - [ ] Configure environment variables
  - [ ] Add health check
  - [ ] Optimize image size

- [ ] **Deployment Guide** (`docs/DEPLOYMENT_API.md`)
  - [ ] Document local development setup
  - [ ] Add production deployment steps
  - [ ] Include Docker deployment
  - [ ] Add monitoring recommendations
  - [ ] Document scaling strategies

---

# 🔧 TECHNICAL REQUIREMENTS

## API Design Principles
- **RESTful**: Follow REST conventions
- **CR_ Compliance**: All data uses CR_ prefix
- **Versioned**: API versioning (v1)
- **Documented**: OpenAPI/Swagger docs
- **Validated**: Pydantic models for all I/O
- **Secure**: CORS, rate limiting, input validation
- **Observable**: Logging and tracing
- **Performant**: Async where beneficial

## Endpoint Structure
```
/api/v1/
  /analyze
    POST /              - Run analysis
    POST /upload        - Upload and analyze
    GET /status/{id}    - Check status
  /data
    GET /sample         - Get sample data
    POST /validate      - Validate data
    GET /schema         - Get schemas
  /tools
    POST /arbitrage     - Detect arbitrage
    POST /value         - Detect value
    POST /outliers      - Detect outliers
    POST /stale         - Detect stale lines
    POST /consensus     - Calculate consensus
  /report
    POST /briefing      - Generate text briefing
    POST /json          - Generate JSON briefing
    GET /template       - Get template
  /chat
    POST /session       - Start session
    POST /ask           - Ask question
    DELETE /session/{id} - End session
  /health             - Health check
```

## CR_ Data Flow
```
HTTP Request (JSON)
  → Pydantic Validation
  → CR_ Structure Conversion
  → Core Engine Processing
  → CR_ Results Generation
  → Response Model Serialization
  → HTTP Response (JSON)
```

## Performance Targets
- **Response Time**: < 100ms for simple endpoints
- **Analysis Time**: < 5s for typical dataset
- **Concurrent Users**: Support 100+ simultaneous requests
- **File Upload**: Support up to 10MB JSON files
- **Rate Limit**: 100 requests/minute per IP

---

# 📊 SUCCESS CRITERIA

## Functional Requirements
- ✅ All core functionality accessible via API
- ✅ Complete CRUD operations for analysis
- ✅ Real-time analysis execution
- ✅ File upload and processing
- ✅ Chat session management
- ✅ Comprehensive error handling

## Quality Requirements
- ✅ 100% CR_ prefix compliance in API layer
- ✅ OpenAPI documentation complete
- ✅ All endpoints tested (unit + integration)
- ✅ Response times meet targets
- ✅ CORS properly configured
- ✅ Input validation on all endpoints

## Documentation Requirements
- ✅ API documentation complete
- ✅ Deployment guide created
- ✅ Example requests/responses documented
- ✅ Error codes documented
- ✅ Swagger UI accessible

---

# 🚀 DELIVERABLES

## Code Artifacts
1. `apps/web/api/main.py` - FastAPI application
2. `apps/web/api/config.py` - API configuration
3. `apps/web/api/routers/` - All endpoint routers (5 files)
4. `apps/web/api/models/` - Pydantic models (2 files)
5. `apps/web/run_api.py` - Server startup script
6. `requirements-web.txt` - Web dependencies
7. `apps/web/Dockerfile` - Docker configuration

## Test Artifacts
1. `tests/test_api_endpoints.py` - Endpoint tests
2. `tests/test_api_integration.py` - Integration tests

## Documentation
1. `docs/API.md` - API documentation
2. `docs/DEPLOYMENT_API.md` - Deployment guide
3. `plans/PHASE_6_COMPLETION_REPORT.md` - Completion report

## Total Files
- **New Files**: ~15
- **Modified Files**: 1 (requirements)
- **Test Files**: 2
- **Documentation**: 3

---

# 🔄 INTEGRATION POINTS

## Existing Modules Used
- `packages.data.loader.load_data()` - Data loading
- `packages.agent.agent.execute_CR_analysis_pipeline()` - Analysis
- `packages.reporting.briefing.generate_CR_briefing()` - Reporting
- `packages.reporting.briefing.generate_CR_json_briefing()` - JSON reports
- `packages.chat.chat_cr.CR_OddsChat` - Chat interface
- `packages.tools.registry.CR_TOOL_REGISTRY` - Tool access
- `packages.data.contracts.validate_CR_structure()` - Validation

## No Breaking Changes
- All existing CLI functionality preserved
- All existing modules unchanged
- API is additive layer only
- CR_ compliance maintained

---

# ⚠️ RISKS & MITIGATIONS

## Risk: Performance with Large Datasets
**Mitigation**: 
- Implement async processing for large files
- Add job queue for long-running analyses
- Set file size limits
- Add timeout configurations

## Risk: CORS Security Issues
**Mitigation**:
- Configure specific allowed origins
- Implement proper CORS headers
- Add rate limiting
- Validate all inputs

## Risk: Session Management Complexity
**Mitigation**:
- Use simple in-memory storage for MVP
- Add session expiration
- Implement cleanup jobs
- Document scaling path (Redis, etc.)

---

# 📝 NOTES

- FastAPI chosen for async support and automatic OpenAPI docs
- Pydantic ensures type safety and validation
- All endpoints return CR_ compliant JSON
- API designed to be stateless where possible
- Chat sessions are temporary (in-memory)
- Ready for horizontal scaling
- Docker support for easy deployment

---

**Phase 6 Status**: Ready to implement
**Dependencies**: Phase 5 complete
**Next Phase**: Phase 7 (Web Frontend)

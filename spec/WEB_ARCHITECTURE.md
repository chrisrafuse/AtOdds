# WEB_ARCHITECTURE.md
## AtOdds Web Application Architecture
Version: 1.0  
Author: Chris Rafuse  
Last Updated: March 26, 2026

---

# 1. SYSTEM OVERVIEW

## 1.1 Architecture Goal
Extend the AtOdds deterministic analysis engine with a modern web interface, maintaining separation of concerns between the core engine, API layer, and presentation layer while ensuring CR_ prefix compliance throughout.

## 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Vanilla JavaScript Application                   │  │
│  │  (HTML/CSS/JS - No Frameworks)                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Server                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  REST API Layer (Python)                          │  │
│  │  - Request validation (Pydantic)                  │  │
│  │  - CORS handling                                  │  │
│  │  - Rate limiting                                  │  │
│  │  - Error handling                                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ Function Calls
┌─────────────────────────────────────────────────────────┐
│              Core Analysis Engine                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Phases 1-5 (Existing CR_ Modules)               │  │
│  │  - Data Layer (contracts, loader, validation)    │  │
│  │  - Core Engine (math, consensus, detectors)      │  │
│  │  - Tools & Agent (registry, orchestration)       │  │
│  │  - Interface (prompts, briefing, chat, trace)    │  │
│  │  - CLI (command-line interface)                  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 1.3 Technology Stack

### Frontend (Phase 7)
- **HTML5**: Semantic markup, accessibility
- **CSS3**: Custom properties, flexbox, grid, animations
- **Vanilla JavaScript**: ES6+ modules, async/await, fetch API
- **No Build Tools**: Direct browser execution (optional minification)
- **No Frameworks**: Zero dependencies on React/Vue/Angular

### Backend (Phase 6)
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization
- **Python 3.9+**: Async support, type hints

### Core Engine (Phases 1-5)
- **Python 3.9+**: Standard library only
- **No External Dependencies**: Self-contained analysis engine

---

# 2. DETAILED ARCHITECTURE

## 2.1 Frontend Layer

### 2.1.1 File Structure
```
apps/web/static/
├── index.html                 # Main dashboard page
├── styles.css                 # Complete stylesheet
├── js/
│   ├── app.js                # Application controller
│   ├── api.js                # API client
│   ├── state.js              # State management
│   ├── results.js            # Results rendering
│   ├── charts.js             # Data visualization
│   ├── upload.js             # File upload handling
│   ├── chat.js               # Chat interface
│   └── utils.js              # Utility functions
└── assets/
    ├── icons/                # SVG icons
    └── images/               # Images
```

### 2.1.2 Module Responsibilities

**app.js** - Main Application Controller
- Initialize application
- Set up event listeners
- Coordinate between modules
- Handle routing (if applicable)
- Manage global state

**api.js** - API Client
```javascript
class CR_APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  async analyzeData(CR_snapshot) {
    // POST /api/v1/analyze
  }
  
  async uploadFile(CR_file) {
    // POST /api/v1/analyze/upload
  }
  
  async startChatSession(CR_data) {
    // POST /api/v1/chat/session
  }
  
  // ... other methods
}
```

**state.js** - State Management
```javascript
class CR_AppState {
  constructor() {
    this.CR_snapshot = null;
    this.CR_findings = [];
    this.CR_analysis_results = null;
    this.CR_chat_session = null;
    this.CR_loading = false;
    this.CR_error = null;
    this.observers = [];
  }
  
  setState(updates) {
    // Update state and notify observers
  }
  
  subscribe(observer) {
    // Add state observer
  }
}
```

**results.js** - Results Rendering
- Render summary cards
- Display findings table
- Show detailed views
- Handle sorting/filtering
- Export functionality

**charts.js** - Data Visualization
- Canvas-based charts (no libraries)
- Bar charts, pie charts, line charts
- Interactive tooltips
- Responsive sizing

**upload.js** - File Upload
- Drag-and-drop handling
- File validation
- Progress tracking
- Preview functionality

**chat.js** - Chat Interface
- Message rendering
- Input handling
- Session management
- Quick questions

**utils.js** - Utilities
- Toast notifications
- Modal dialogs
- Date/time formatting
- Number formatting
- Debounce/throttle

### 2.1.3 Data Flow

```
User Action
  ↓
Event Handler (app.js)
  ↓
State Update (state.js)
  ↓
API Call (api.js)
  ↓
Response Processing
  ↓
State Update
  ↓
Observer Notification
  ↓
UI Re-render (results.js, charts.js, etc.)
```

---

## 2.2 API Layer

### 2.2.1 File Structure
```
apps/web/api/
├── main.py                   # FastAPI application
├── config.py                 # Configuration
├── models/
│   ├── requests.py          # Request models
│   └── responses.py         # Response models
├── routers/
│   ├── analysis.py          # Analysis endpoints
│   ├── data.py              # Data endpoints
│   ├── tools.py             # Tools endpoints
│   ├── reporting.py         # Reporting endpoints
│   └── chat.py              # Chat endpoints
└── middleware/
    ├── cors.py              # CORS handling
    ├── rate_limit.py        # Rate limiting
    └── error_handler.py     # Error handling
```

### 2.2.2 FastAPI Application

**main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="AtOdds API",
    version="1.0",
    description="CR_ compliant odds analysis API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="apps/web/static"), name="static")

# Include routers
from .routers import analysis, data, tools, reporting, chat
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(reporting.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"CR_status": "healthy"}
```

### 2.2.3 Request/Response Models

**models/requests.py**
```python
from pydantic import BaseModel
from typing import List, Dict, Any

class CR_AnalysisRequest(BaseModel):
    CR_snapshot: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "CR_snapshot": {
                    "CR_events": [...],
                    "CR_timestamp": "2026-03-26T13:22:00Z"
                }
            }
        }

class CR_ChatRequest(BaseModel):
    CR_session_id: str
    CR_question: str
```

**models/responses.py**
```python
from pydantic import BaseModel
from typing import List, Dict, Any

class CR_AnalysisResponse(BaseModel):
    CR_status: str
    CR_data: Dict[str, Any]
    CR_metadata: Dict[str, Any]

class CR_ErrorResponse(BaseModel):
    CR_status: str = "error"
    CR_error: Dict[str, Any]
    CR_metadata: Dict[str, Any]
```

### 2.2.4 Router Example

**routers/analysis.py**
```python
from fastapi import APIRouter, HTTPException
from ..models.requests import CR_AnalysisRequest
from ..models.responses import CR_AnalysisResponse
from packages.data.loader import load_data
from packages.agent.agent import execute_CR_analysis_pipeline

router = APIRouter(tags=["analysis"])

@router.post("/analyze", response_model=CR_AnalysisResponse)
async def analyze_odds(request: CR_AnalysisRequest):
    try:
        CR_snapshot = request.CR_snapshot
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        
        return {
            "CR_status": "success",
            "CR_data": CR_results,
            "CR_metadata": {
                "CR_timestamp": datetime.now().isoformat(),
                "CR_version": "1.0"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 2.3 Integration with Core Engine

### 2.3.1 Module Imports
```python
# Data Layer
from packages.data.loader import load_data
from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_snapshot,
    validate_CR_structure
)

# Core Engine
from packages.core_engine.odds_math import (
    compute_CR_implied_probability,
    compute_CR_vig,
    convert_CR_american_to_decimal
)
from packages.core_engine.consensus import compute_CR_best_lines
from packages.core_engine.detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edges,
    detect_CR_outliers,
    detect_CR_stale_lines
)

# Tools & Agent
from packages.tools.registry import CR_TOOL_REGISTRY
from packages.agent.agent import (
    execute_CR_analysis_pipeline,
    run_CR_agent
)

# Interface
from packages.reporting.briefing import (
    generate_CR_briefing,
    generate_CR_json_briefing
)
from packages.chat.chat_cr import CR_OddsChat, start_CR_chat_session
from packages.observability.trace_cr import CR_Tracer, get_CR_tracer
```

### 2.3.2 Data Flow Through Layers

```
Frontend Upload
  ↓
POST /api/v1/analyze/upload
  ↓
FastAPI Endpoint (routers/analysis.py)
  ↓
load_data() - Data Layer
  ↓
execute_CR_analysis_pipeline() - Agent Layer
  ↓
CR_TOOL_REGISTRY tools - Tools Layer
  ↓
Core Engine Functions - Core Layer
  ↓
CR_ Findings Generation
  ↓
Response Model Serialization
  ↓
JSON Response to Frontend
  ↓
State Update & UI Render
```

---

## 2.4 State Management

### 2.4.1 Frontend State
```javascript
const CR_appState = {
  // Data
  CR_snapshot: null,
  CR_findings: [],
  CR_analysis_results: null,
  CR_briefing: null,
  
  // UI State
  CR_loading: false,
  CR_error: null,
  CR_current_view: 'upload',
  CR_selected_finding: null,
  
  // Chat State
  CR_chat_session_id: null,
  CR_chat_messages: [],
  
  // Filters
  CR_filter_type: 'all',
  CR_sort_by: 'confidence',
  CR_sort_order: 'desc'
};
```

### 2.4.2 Backend State (Session Management)
```python
# In-memory session storage (Phase 6)
CR_chat_sessions = {}

class CR_ChatSession:
    def __init__(self, CR_session_id, CR_snapshot, CR_findings):
        self.CR_session_id = CR_session_id
        self.CR_snapshot = CR_snapshot
        self.CR_findings = CR_findings
        self.CR_chat = start_CR_chat_session(CR_snapshot, CR_findings)
        self.CR_created_at = datetime.now()
        self.CR_expires_at = datetime.now() + timedelta(hours=1)
```

---

## 2.5 Security Architecture

### 2.5.1 CORS Configuration
```python
# Development
allow_origins = ["http://localhost:*", "http://127.0.0.1:*"]

# Production
allow_origins = ["https://atodds.com", "https://www.atodds.com"]
```

### 2.5.2 Input Validation
- **Pydantic Models**: Type validation on all inputs
- **File Size Limits**: 10MB max for uploads
- **JSON Schema Validation**: CR_ structure validation
- **Sanitization**: No user input in system commands

### 2.5.3 Rate Limiting
```python
# Per-IP rate limits
limits = {
    "default": "100/minute",
    "analyze": "10/minute",
    "upload": "5/minute"
}
```

### 2.5.4 Error Handling
- **No Stack Traces**: Generic error messages to users
- **Logging**: Detailed errors logged server-side
- **Validation Errors**: Specific field-level feedback
- **HTTP Status Codes**: Proper status code usage

---

## 2.6 Performance Architecture

### 2.6.1 Frontend Optimizations
- **Code Splitting**: Load modules on demand
- **Lazy Loading**: Images and charts below fold
- **Debouncing**: Search and filter inputs
- **Virtual Scrolling**: Large tables
- **Caching**: LocalStorage for recent analyses

### 2.6.2 Backend Optimizations
- **Async Endpoints**: FastAPI async/await
- **Connection Pooling**: Database connections (future)
- **Response Compression**: Gzip compression
- **Caching**: Redis for session storage (future)

### 2.6.3 Network Optimizations
- **Minification**: CSS and JS minified
- **Compression**: Gzip/Brotli for static assets
- **CDN**: Static assets served from CDN (future)
- **HTTP/2**: Server push for critical resources

---

## 2.7 Deployment Architecture

### 2.7.1 Development Environment
```
┌─────────────────────────────────┐
│  Frontend Development Server    │
│  (Live Server / Python HTTP)    │
│  Port: 3000                     │
└─────────────────────────────────┘
           ↕
┌─────────────────────────────────┐
│  FastAPI Development Server     │
│  (Uvicorn with reload)          │
│  Port: 8000                     │
└─────────────────────────────────┘
```

### 2.7.2 Production Environment
```
┌─────────────────────────────────┐
│  Nginx Reverse Proxy            │
│  - SSL Termination              │
│  - Static file serving          │
│  - Load balancing               │
└─────────────────────────────────┘
           ↕
┌─────────────────────────────────┐
│  Uvicorn Workers (4x)           │
│  - FastAPI application          │
│  - Process pool                 │
└─────────────────────────────────┘
           ↕
┌─────────────────────────────────┐
│  Core Analysis Engine           │
│  - Phases 1-5 modules           │
└─────────────────────────────────┘
```

### 2.7.3 Docker Architecture
```dockerfile
# Multi-stage build
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . .
CMD ["uvicorn", "apps.web.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 2.8 Monitoring & Observability

### 2.8.1 Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("atodds.api")

# Log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"CR_request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"CR_response: {response.status_code}")
    return response
```

### 2.8.2 Metrics
- **Request Count**: Total API requests
- **Response Time**: P50, P95, P99 latencies
- **Error Rate**: 4xx and 5xx responses
- **Analysis Time**: Pipeline execution duration
- **Active Sessions**: Chat sessions count

### 2.8.3 Tracing
```python
# Integrate with CR_Tracer
from packages.observability.trace_cr import get_CR_tracer

@router.post("/analyze")
async def analyze_odds(request: CR_AnalysisRequest):
    CR_tracer = get_CR_tracer()
    CR_session_id = CR_tracer.start_CR_session()
    
    try:
        # ... analysis logic
        CR_tracer.log_CR_step("analysis_complete", "Analysis finished")
    finally:
        CR_tracer.end_CR_session()
```

---

## 2.9 Testing Architecture

### 2.9.1 Frontend Testing
```javascript
// Unit tests for utilities
test('formatCR_Odds formats American odds correctly', () => {
  expect(formatCR_Odds(-110)).toBe('-110');
  expect(formatCR_Odds(150)).toBe('+150');
});

// Integration tests for API client
test('CR_APIClient.analyzeData sends correct request', async () => {
  const client = new CR_APIClient('http://localhost:8000');
  const result = await client.analyzeData(mockSnapshot);
  expect(result.CR_status).toBe('success');
});
```

### 2.9.2 Backend Testing
```python
from fastapi.testclient import TestClient
from apps.web.api.main import app

client = TestClient(app)

def test_analyze_endpoint():
    response = client.post(
        "/api/v1/analyze",
        json={"CR_snapshot": mock_snapshot}
    )
    assert response.status_code == 200
    assert response.json()["CR_status"] == "success"
```

### 2.9.3 End-to-End Testing
- **Manual Testing**: Browser-based testing
- **Automated Testing**: Playwright/Selenium (future)
- **Load Testing**: Locust for API load testing
- **Security Testing**: OWASP ZAP scanning

---

## 2.10 Scalability Considerations

### 2.10.1 Horizontal Scaling
- **Stateless API**: No server-side session state
- **Load Balancer**: Nginx/HAProxy
- **Multiple Workers**: Uvicorn worker processes
- **Container Orchestration**: Kubernetes (future)

### 2.10.2 Vertical Scaling
- **CPU**: Multi-core processing for analysis
- **Memory**: Efficient data structures
- **Storage**: SSD for fast I/O

### 2.10.3 Caching Strategy
- **Browser Cache**: Static assets (1 year)
- **API Cache**: Redis for frequent queries (future)
- **CDN Cache**: Global edge caching (future)

---

## 2.11 Migration Path

### 2.11.1 Phase 6 → Phase 7
1. Implement FastAPI backend (Phase 6)
2. Test API endpoints independently
3. Develop frontend against API (Phase 7)
4. Integration testing
5. Deployment

### 2.11.2 Future Enhancements
- **Phase 8**: Authentication & user accounts
- **Phase 9**: Real-time data feeds
- **Phase 10**: Advanced analytics dashboard
- **Phase 11**: Mobile applications
- **Phase 12**: Multi-tenant support

---

## 2.12 Dependency Graph

```
Frontend (Phase 7)
  ↓ depends on
API Layer (Phase 6)
  ↓ depends on
Core Engine (Phases 1-5)
  ↓ depends on
Python Standard Library
```

**No circular dependencies**  
**Clear separation of concerns**  
**Unidirectional data flow**

---

# 3. DESIGN PATTERNS

## 3.1 Frontend Patterns

### Observer Pattern (State Management)
```javascript
class CR_AppState {
  subscribe(observer) {
    this.observers.push(observer);
  }
  
  notify() {
    this.observers.forEach(observer => observer(this));
  }
}
```

### Module Pattern (Encapsulation)
```javascript
const CR_ResultsModule = (() => {
  // Private
  const renderCard = (data) => { ... };
  
  // Public
  return {
    render: (findings) => { ... }
  };
})();
```

### Singleton Pattern (API Client)
```javascript
const CR_apiClient = new CR_APIClient(API_BASE_URL);
export default CR_apiClient;
```

## 3.2 Backend Patterns

### Dependency Injection (FastAPI)
```python
from fastapi import Depends

def get_CR_tracer():
    return CR_Tracer()

@router.post("/analyze")
async def analyze(
    request: CR_AnalysisRequest,
    tracer: CR_Tracer = Depends(get_CR_tracer)
):
    # Use injected tracer
```

### Repository Pattern (Data Access)
```python
class CR_DataRepository:
    def load_snapshot(self, file_path: str):
        return load_data(file_path)
    
    def validate_snapshot(self, snapshot: dict):
        return validate_CR_structure(snapshot, "CR_snapshot")
```

### Factory Pattern (Response Creation)
```python
def create_CR_success_response(data: dict):
    return {
        "CR_status": "success",
        "CR_data": data,
        "CR_metadata": {
            "CR_timestamp": datetime.now().isoformat()
        }
    }
```

---

# 4. CONFIGURATION MANAGEMENT

## 4.1 Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# CORS
CORS_ORIGINS=http://localhost:3000,https://atodds.com

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_ANALYZE=10/minute

# Session
SESSION_TIMEOUT_HOURS=1

# Logging
LOG_LEVEL=INFO
```

## 4.2 Configuration Files
```python
# apps/web/api/config.py
from pydantic import BaseSettings

class CR_Settings(BaseSettings):
    CR_api_host: str = "0.0.0.0"
    CR_api_port: int = 8000
    CR_cors_origins: list = ["*"]
    CR_log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

CR_settings = CR_Settings()
```

---

**Document Version**: 1.0  
**Last Updated**: March 26, 2026  
**Maintained By**: AtOdds Architecture Team

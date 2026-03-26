# API_SPECIFICATION.md
## AtOdds REST API Specification
Version: 1.0  
Author: Chris Rafuse  
Last Updated: March 26, 2026

---

# 1. OVERVIEW

## 1.1 Purpose
The AtOdds REST API provides programmatic access to the odds analysis engine, enabling web and mobile applications to perform real-time betting odds analysis, detect arbitrage opportunities, calculate consensus pricing, and generate analytical briefings.

## 1.2 Design Principles
- **RESTful**: Standard HTTP methods and status codes
- **CR_ Compliant**: All data structures use CR_ prefix
- **Versioned**: API versioning in URL path (/api/v1/)
- **Stateless**: Each request contains all necessary information
- **JSON-Only**: All requests and responses use JSON
- **Documented**: OpenAPI 3.0 specification available
- **Secure**: Input validation, CORS, rate limiting

## 1.3 Base URL
```
Development: http://localhost:8000
Production:  https://api.atodds.com
```

## 1.4 API Version
Current version: `v1`  
All endpoints prefixed with: `/api/v1/`

---

# 2. AUTHENTICATION

## 2.1 Current Implementation
**Phase 6**: No authentication required (open API)

## 2.2 Future Implementation
**Phase 8+**: JWT-based authentication
```http
Authorization: Bearer <token>
```

---

# 3. COMMON PATTERNS

## 3.1 Request Headers
```http
Content-Type: application/json
Accept: application/json
```

## 3.2 Response Format
All responses follow this structure:
```json
{
  "CR_status": "success|error",
  "CR_data": { ... },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T13:22:00Z",
    "CR_version": "1.0",
    "CR_execution_time_ms": 123
  }
}
```

## 3.3 Error Format
```json
{
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
    "CR_timestamp": "2026-03-26T13:22:00Z"
  }
}
```

## 3.4 HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

---

# 4. ENDPOINTS

## 4.1 Health Check

### GET /health
Check API health status

**Request:**
```http
GET /health HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "healthy",
  "CR_version": "1.0",
  "CR_uptime_seconds": 3600,
  "CR_timestamp": "2026-03-26T13:22:00Z"
}
```

**Status Codes:**
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service unhealthy

---

## 4.2 Analysis Endpoints

### POST /api/v1/analyze
Run complete odds analysis pipeline

**Request:**
```http
POST /api/v1/analyze HTTP/1.1
Content-Type: application/json

{
  "CR_snapshot": {
    "CR_events": [...],
    "CR_timestamp": "2026-03-26T13:22:00Z",
    "CR_source": "api_request"
  }
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_findings": [
      {
        "CR_type": "arbitrage",
        "CR_event_id": "nba_20260326_lal_bos",
        "CR_market_name": "moneyline_Pinnacle",
        "CR_confidence": 0.95,
        "CR_description": "Arbitrage opportunity: 0.43% profit margin",
        "CR_metadata": {
          "CR_profit_margin": 0.0043,
          "CR_bookmakers": ["Pinnacle", "DraftKings"]
        }
      }
    ],
    "CR_findings_summary": {
      "CR_total_findings": 1,
      "CR_by_type": {
        "arbitrage": 1,
        "value_edge": 0,
        "outlier": 0,
        "stale_line": 0
      },
      "CR_high_confidence_count": 1
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T13:22:00Z",
    "CR_execution_time_ms": 234,
    "CR_events_analyzed": 10
  }
}
```

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: Invalid snapshot structure
- `422 Unprocessable Entity`: Validation failed

---

### POST /api/v1/analyze/upload
Upload JSON file and run analysis

**Request:**
```http
POST /api/v1/analyze/upload HTTP/1.1
Content-Type: multipart/form-data

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="odds.json"
Content-Type: application/json

{...file content...}
------WebKitFormBoundary--
```

**Response:**
Same as `/api/v1/analyze`

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: Invalid file format
- `413 Payload Too Large`: File exceeds size limit (10MB)

---

### GET /api/v1/analyze/status/{job_id}
Check analysis job status (async operations)

**Request:**
```http
GET /api/v1/analyze/status/job_abc123 HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_job_id": "job_abc123",
    "CR_job_status": "completed|running|failed",
    "CR_progress_percent": 100,
    "CR_result": {...}
  }
}
```

**Status Codes:**
- `200 OK`: Job status retrieved
- `404 Not Found`: Job not found

---

## 4.3 Data Endpoints

### GET /api/v1/data/sample
Get sample odds data

**Request:**
```http
GET /api/v1/data/sample HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_snapshot": {
      "CR_events": [...],
      "CR_timestamp": "2026-03-26T13:22:00Z",
      "CR_source": "sample_data"
    }
  }
}
```

**Status Codes:**
- `200 OK`: Sample data retrieved

---

### POST /api/v1/data/validate
Validate CR_ data structure

**Request:**
```http
POST /api/v1/data/validate HTTP/1.1
Content-Type: application/json

{
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_is_valid": true,
    "CR_errors": [],
    "CR_warnings": []
  }
}
```

**Status Codes:**
- `200 OK`: Validation completed
- `400 Bad Request`: Invalid request format

---

### GET /api/v1/data/schema
Get CR_ schema definitions

**Request:**
```http
GET /api/v1/data/schema HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_schemas": {
      "CR_outcome": {...},
      "CR_market": {...},
      "CR_event": {...},
      "CR_snapshot": {...}
    }
  }
}
```

**Status Codes:**
- `200 OK`: Schemas retrieved

---

## 4.4 Tools Endpoints

### POST /api/v1/tools/arbitrage
Detect arbitrage opportunities

**Request:**
```http
POST /api/v1/tools/arbitrage HTTP/1.1
Content-Type: application/json

{
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_findings": [...]
  }
}
```

---

### POST /api/v1/tools/value
Detect value edges

**Request/Response:** Same pattern as arbitrage

---

### POST /api/v1/tools/outliers
Detect statistical outliers

**Request/Response:** Same pattern as arbitrage

---

### POST /api/v1/tools/stale
Detect stale lines

**Request/Response:** Same pattern as arbitrage

---

### POST /api/v1/tools/consensus
Calculate consensus pricing

**Request:**
```http
POST /api/v1/tools/consensus HTTP/1.1
Content-Type: application/json

{
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_consensus": {
      "CR_event_id": "nba_20260326_lal_bos",
      "CR_best_lines": [...],
      "CR_median_prices": {...}
    }
  }
}
```

---

## 4.5 Reporting Endpoints

### POST /api/v1/report/briefing
Generate text briefing

**Request:**
```http
POST /api/v1/report/briefing HTTP/1.1
Content-Type: application/json

{
  "CR_findings": [...],
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_briefing": "=== CR_ ODDS ANALYSIS BRIEFING ===\n..."
  }
}
```

---

### POST /api/v1/report/json
Generate JSON briefing

**Request:**
```http
POST /api/v1/report/json HTTP/1.1
Content-Type: application/json

{
  "CR_findings": [...],
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_briefing": {
      "CR_metadata": {...},
      "CR_summary": {...},
      "CR_findings": [...],
      "CR_recommendations": [...]
    }
  }
}
```

---

### GET /api/v1/report/template
Get briefing template structure

**Request:**
```http
GET /api/v1/report/template HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_template": {
      "CR_sections": ["summary", "findings", "recommendations"],
      "CR_fields": {...}
    }
  }
}
```

---

## 4.6 Chat Endpoints

### POST /api/v1/chat/session
Start chat session

**Request:**
```http
POST /api/v1/chat/session HTTP/1.1
Content-Type: application/json

{
  "CR_snapshot": {...},
  "CR_findings": [...]
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_session_id": "session_abc123",
    "CR_expires_at": "2026-03-26T14:22:00Z"
  }
}
```

---

### POST /api/v1/chat/ask
Ask question in chat session

**Request:**
```http
POST /api/v1/chat/ask HTTP/1.1
Content-Type: application/json

{
  "CR_session_id": "session_abc123",
  "CR_question": "What arbitrage opportunities exist?"
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_answer": "There is 1 arbitrage opportunity...",
    "CR_sources": ["CR_findings", "CR_arbitrage_tool"],
    "CR_confidence": "high"
  }
}
```

---

### DELETE /api/v1/chat/session/{session_id}
End chat session

**Request:**
```http
DELETE /api/v1/chat/session/session_abc123 HTTP/1.1
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_message": "Session ended successfully"
  }
}
```

---

# 5. DATA MODELS

## 5.1 CR_Snapshot
```json
{
  "CR_events": [
    {
      "CR_event_id": "string",
      "CR_event_name": "string",
      "CR_sport": "string",
      "CR_markets": [...],
      "CR_commence_time": "ISO8601",
      "CR_home_team": "string",
      "CR_away_team": "string"
    }
  ],
  "CR_timestamp": "ISO8601",
  "CR_source": "string"
}
```

## 5.2 CR_Finding
```json
{
  "CR_type": "arbitrage|value_edge|outlier|stale_line",
  "CR_event_id": "string",
  "CR_market_name": "string",
  "CR_confidence": 0.0-1.0,
  "CR_description": "string",
  "CR_metadata": {
    "CR_profit_margin": "number",
    "CR_bookmakers": ["string"]
  }
}
```

## 5.3 CR_Market
```json
{
  "CR_name": "string",
  "CR_outcomes": [
    {
      "CR_name": "string",
      "CR_price": "number",
      "CR_implied_probability": "number"
    }
  ],
  "CR_bookmaker": "string",
  "CR_last_update": "ISO8601"
}
```

---

# 6. RATE LIMITING

## 6.1 Limits
- **Default**: 100 requests per minute per IP
- **Analysis**: 10 requests per minute per IP
- **Upload**: 5 requests per minute per IP

## 6.2 Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1711468920
```

## 6.3 Rate Limit Response
```json
{
  "CR_status": "error",
  "CR_error": {
    "CR_code": "RATE_LIMIT_EXCEEDED",
    "CR_message": "Rate limit exceeded",
    "CR_details": {
      "CR_retry_after_seconds": 60
    }
  }
}
```

---

# 7. CORS CONFIGURATION

## 7.1 Allowed Origins
```
Development: http://localhost:*
Production: https://atodds.com, https://www.atodds.com
```

## 7.2 Allowed Methods
```
GET, POST, PUT, DELETE, OPTIONS
```

## 7.3 Allowed Headers
```
Content-Type, Authorization, X-Requested-With
```

---

# 8. ERROR CODES

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `INVALID_SNAPSHOT` | Invalid CR_ snapshot structure |
| `INVALID_FILE` | Invalid file format or size |
| `SESSION_NOT_FOUND` | Chat session not found |
| `SESSION_EXPIRED` | Chat session expired |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

---

# 9. EXAMPLES

## 9.1 Complete Analysis Workflow

```bash
# 1. Get sample data
curl -X GET http://localhost:8000/api/v1/data/sample

# 2. Validate data
curl -X POST http://localhost:8000/api/v1/data/validate \
  -H "Content-Type: application/json" \
  -d @snapshot.json

# 3. Run analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d @snapshot.json

# 4. Generate briefing
curl -X POST http://localhost:8000/api/v1/report/briefing \
  -H "Content-Type: application/json" \
  -d @findings.json

# 5. Start chat session
curl -X POST http://localhost:8000/api/v1/chat/session \
  -H "Content-Type: application/json" \
  -d @session_data.json

# 6. Ask question
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"CR_session_id":"session_abc123","CR_question":"summary"}'
```

---

# 10. VERSIONING

## 10.1 Current Version
- **Version**: v1
- **Release Date**: March 2026
- **Status**: Stable

## 10.2 Version Strategy
- URL-based versioning: `/api/v1/`, `/api/v2/`
- Backward compatibility maintained for 1 year
- Deprecation warnings in headers
- Migration guides provided

---

# 11. PERFORMANCE

## 11.1 Response Time Targets
- **Health Check**: < 10ms
- **Data Endpoints**: < 100ms
- **Analysis**: < 5s for typical dataset
- **Tools**: < 1s per tool
- **Reporting**: < 500ms
- **Chat**: < 200ms

## 11.2 Payload Limits
- **Request Body**: 10MB max
- **File Upload**: 10MB max
- **Response Body**: 50MB max

---

# 12. OPENAPI SPECIFICATION

Full OpenAPI 3.0 specification available at:
```
GET /api/v1/openapi.json
```

Interactive documentation:
```
Swagger UI: /docs
ReDoc: /redoc
```

---

**Document Version**: 1.0  
**Last Updated**: March 26, 2026  
**Maintained By**: AtOdds Development Team

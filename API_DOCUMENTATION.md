# AtOdds API Documentation

**Version:** 2.0 (Phase 8-10 Complete)
**Base URL:** `http://localhost:8000/api/v1`
**Status:** Production Ready with AI Integration

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- AtOdds API server running
- HTTP client (curl, requests, fetch, etc.)

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Should return:
{"CR_status":"healthy","CR_version":"1.0","CR_timestamp":"2026-03-26T16:35:42.111027"}
```

---

## 📋 API Overview

The AtOdds API provides programmatic access to all odds analysis functionality with 18 endpoints organized into 5 main categories:

- **Analysis** (2 endpoints) - Complete odds analysis
- **Data** (3 endpoints) - Data management and validation
- **Tools** (5 endpoints) - Individual detection tools
- **Reporting** (3 endpoints) - Briefing generation
- **Chat** (4 endpoints) - Interactive Q&A sessions

All requests and responses use the `CR_` prefix convention for consistency.

---

## 🔐 Authentication

**Current Status:** Open (no authentication required)

**LLM Authentication:** Configure via environment variables
- `LLM_PROVIDER=openai|anthropic|gemini|mock`
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`

---

## 📊 Data Format

### CR_ Prefix Convention

All data fields use the `CR_` prefix:

```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_events": [...],
    "CR_findings": [...]
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

### Event Structure

```json
{
  "CR_event_id": "nba_20260320_lal_bos",
  "CR_event_name": "Boston Celtics vs Los Angeles Lakers",
  "CR_sport": "NBA",
  "CR_markets": [
    {
      "CR_name": "moneyline_DraftKings",
      "CR_bookmaker": "DraftKings",
      "CR_outcomes": [
        {
          "CR_name": "Boston Celtics",
          "CR_odds": -110,
          "CR_is_main": true
        },
        {
          "CR_name": "Los Angeles Lakers",
          "CR_odds": -110,
          "CR_is_main": true
        }
      ]
    }
  ]
}
```

---

## 🛠️ Endpoints

### Health & Information

#### GET /health

Check API health status.

**Response:**
```json
{
  "CR_status": "healthy",
  "CR_version": "1.0",
  "CR_timestamp": "2026-03-26T16:35:42.111027"
}
```

#### GET /

Get API information and available endpoints.

**Response:**
```json
{
  "CR_api": "AtOdds Odds Analysis API",
  "CR_version": "1.0",
  "CR_status": "operational",
  "CR_endpoints": {
    "CR_docs": "/docs",
    "CR_redoc": "/redoc",
    "CR_openapi": "/api/v1/openapi.json",
    "CR_health": "/health"
  },
  "CR_timestamp": "2026-03-26T16:35:42.111027"
}
```

---

### Analysis Endpoints

#### POST /api/v1/analyze

Run complete analysis pipeline on odds data.

**Request:**
```json
{
  "CR_snapshot": {
    "CR_events": [...],
    "CR_metadata": {
      "CR_source": "user_upload",
      "CR_timestamp": "2026-03-26T16:35:42.111027"
    }
  }
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_findings": [...],
    "CR_count": 7,
    "CR_summary": {
      "CR_arbitrage": 2,
      "CR_value_edges": 4,
      "CR_outliers": 1
    },
    "CR_llm_provider": "openai",
    "CR_llm_summary": "## Market Overview\nI found 2 arbitrage opportunities...",
    "CR_tool_trace": [
      {"tool": "CR_detect_arbitrage", "result": "2 findings"},
      {"tool": "CR_detect_value_edges", "result": "4 findings"},
      {"tool": "CR_detect_outliers", "result": "1 findings"}
    ],
    "CR_sportsbook_rankings": {
      "DraftKings": {"score": 85.2, "verdict": "Recommended"},
      "FanDuel": {"score": 78.9, "verdict": "Cautious"}
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "2.0",
    "CR_pipeline": "llm_enhanced_analysis"
  }
}
```

#### POST /api/v1/analyze/upload

Upload JSON file and run analysis.

**Request:** Multipart form data with file field

**Response:** Same as `/analyze` endpoint

---

### Data Endpoints

#### GET /api/v1/data/sample

Get sample odds data for testing.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_snapshot": {
      "CR_events": [...],
      "CR_metadata": {...}
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

#### POST /api/v1/data/validate

Validate CR_ structure compliance.

**Request:**
```json
{
  "CR_snapshot": {...}
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_valid": true,
    "CR_errors": [],
    "CR_warnings": []
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

#### GET /api/v1/data/schema

Get data structure definitions.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_schemas": {
      "CR_event": {...},
      "CR_market": {...},
      "CR_outcome": {...}
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

---

### Tools Endpoints

#### POST /api/v1/tools/arbitrage

Detect arbitrage opportunities.

**Request:**
```json
{
  "CR_snapshot": {...}
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
        "CR_event_id": "nba_20260320_lal_bos",
        "CR_market": "moneyline",
        "CR_confidence": 0.95,
        "CR_profit_margin": 0.0235,
        "CR_bookmakers": ["DraftKings", "FanDuel"],
        "CR_description": "Arbitrage opportunity: 2.35% profit margin"
      }
    ],
    "CR_count": 2
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0",
    "CR_tool": "detect_CR_arbitrage"
  }
}
```

#### POST /api/v1/tools/value

Detect value edges.

**Response Structure:** Same as arbitrage, with `CR_type: "value_edge"`

#### POST /api/v1/tools/outliers

Detect statistical outliers.

**Response Structure:** Same as arbitrage, with `CR_type: "outlier"`

#### POST /api/v1/tools/stale

Detect stale lines.

**Response Structure:** Same as arbitrage, with `CR_type: "stale_line"`

#### POST /api/v1/tools/consensus

Calculate consensus pricing.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_consensus": {
      "CR_events": [...],
      "CR_summary": {
        "CR_total_markets": 50,
        "CR_consensus_prices": 45
      }
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0",
    "CR_tool": "compute_CR_best_lines"
  }
}
```

---

### Reporting Endpoints

#### POST /api/v1/report/briefing

Generate text briefing.

**Request:**
```json
{
  "CR_findings": [...],
  "CR_format": "text",
  "CR_include_recommendations": true
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_briefing": "============================================================\nODDS ANALYSIS BRIEFING\n============================================================\n...",
    "CR_word_count": 1250
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

#### POST /api/v1/report/json

Generate JSON briefing.

**Response:** Structured JSON with sections, findings, and recommendations

#### GET /api/v1/report/template

Get briefing template structure.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_template": {
      "CR_sections": ["summary", "findings", "recommendations"],
      "CR_fields": [...]
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

---

### Chat Endpoints

#### POST /api/v1/chat/session

Start new chat session.

**Request:**
```json
{
  "CR_context": "odds_analysis",
  "CR_persistence": true,
  "CR_briefing_text": "## Market Overview\nFound 2 arbitrage opportunities..."
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_session_id": "session_abc123",
    "CR_created_at": "2026-03-26T16:35:42.111027",
    "CR_expires_at": "2026-03-26T17:35:42.111027",
    "CR_llm_provider": "openai"
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "2.0"
  }
}
```

#### POST /api/v1/chat/ask

Ask question in chat session.

**Request:**
```json
{
  "CR_session_id": "session_abc123",
  "CR_question": "What are the best arbitrage opportunities?"
}
```

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_answer": "Based on the current analysis, I found 2 arbitrage opportunities...",
    "CR_sources": [...],
    "CR_confidence": 0.92,
    "CR_tool_trace": [
      {"tool": "CR_arbitrage_finder", "result": "Found 2 opportunities"}
    ]
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "2.0"
  }
}
```

#### DELETE /api/v1/chat/session/{id}

End chat session.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_message": "Session terminated successfully"
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

#### GET /api/v1/chat/sessions

List active chat sessions.

**Response:**
```json
{
  "CR_status": "success",
  "CR_data": {
    "CR_sessions": [
      {
        "CR_session_id": "session_abc123",
        "CR_created_at": "2026-03-26T16:35:42.111027",
        "CR_expires_at": "2026-03-26T17:35:42.111027"
      }
    ],
    "CR_count": 1
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

---

## ❌ Error Handling

### Error Response Format

```json
{
  "CR_status": "error",
  "CR_error": {
    "CR_code": "VALIDATION_ERROR",
    "CR_message": "Invalid input data",
    "CR_details": {
      "CR_field": "CR_events",
      "CR_issue": "Array cannot be empty"
    }
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR` - Invalid request data
- `PROCESSING_ERROR` - Analysis failed
- `FILE_ERROR` - File upload issues
- `SESSION_ERROR` - Chat session problems
- `RATE_LIMIT_ERROR` - Too many requests (future)

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## 📝 Usage Examples

### Python Client

```python
import requests
import json

class AtOddsClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def get_sample_data(self):
        response = requests.get(f"{self.base_url}/api/v1/data/sample")
        return response.json()

    def analyze(self, snapshot):
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            json={"CR_snapshot": snapshot}
        )
        return response.json()

    def detect_arbitrage(self, snapshot):
        response = requests.post(
            f"{self.base_url}/api/v1/tools/arbitrage",
            json={"CR_snapshot": snapshot}
        )
        return response.json()

    def generate_briefing(self, findings):
        response = requests.post(
            f"{self.base_url}/api/v1/report/briefing",
            json={
                "CR_findings": findings,
                "CR_format": "text",
                "CR_include_recommendations": True
            }
        )
        return response.json()

# Usage
client = AtOddsClient()

# Health check
print(client.health_check())

# Get sample data and analyze
sample = client.get_sample_data()
results = client.analyze(sample["CR_data"]["CR_snapshot"])
print(f"Found {results['CR_data']['CR_count']} opportunities")

# Generate briefing
briefing = client.generate_briefing(results["CR_data"]["CR_findings"])
print(briefing["CR_data"]["CR_briefing"])
```

### JavaScript Client

```javascript
class AtOddsClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }

    async getSampleData() {
        const response = await fetch(`${this.baseUrl}/api/v1/data/sample`);
        return await response.json();
    }

    async analyze(snapshot) {
        const response = await fetch(`${this.baseUrl}/api/v1/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ CR_snapshot: snapshot })
        });
        return await response.json();
    }

    async detectArbitrage(snapshot) {
        const response = await fetch(`${this.baseUrl}/api/v1/tools/arbitrage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ CR_snapshot: snapshot })
        });
        return await response.json();
    }

    async generateBriefing(findings) {
        const response = await fetch(`${this.baseUrl}/api/v1/report/briefing`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                CR_findings: findings,
                CR_format: 'text',
                CR_include_recommendations: true
            })
        });
        return await response.json();
    }
}

// Usage
const client = new AtOddsClient();

// Health check
client.healthCheck().then(console.log);

// Get sample data and analyze
client.getSampleData().then(sample => {
    return client.analyze(sample.CR_data.CR_snapshot);
}).then(results => {
    console.log(`Found ${results.CR_data.CR_count} opportunities`);

    // Generate briefing
    return client.generateBriefing(results.CR_data.CR_findings);
}).then(briefing => {
    console.log(briefing.CR_data.CR_briefing);
});
```

### Shell Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Health check
echo "Health Check:"
curl -s $BASE_URL/health | jq .

echo -e "\nSample Data:"
curl -s $BASE_URL/api/v1/data/sample | jq '.CR_data.CR_snapshot' > sample.json

echo -e "\nRunning Analysis:"
curl -s -X POST $BASE_URL/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d @sample.json | jq .

echo -e "\nDetecting Arbitrage:"
curl -s -X POST $BASE_URL/api/v1/tools/arbitrage \
  -H "Content-Type: application/json" \
  -d @sample.json | jq '.CR_data.CR_findings'
```

---

## 🔧 Configuration

### Environment Variables

```env
CR_api_host=0.0.0.0
CR_api_port=8000
CR_api_version=1.0
CR_debug_mode=false
CR_cors_origins=["http://localhost:3000","http://localhost:8000"]
CR_rate_limit_requests=100
CR_rate_limit_window=60
CR_max_file_size=10485760
CR_log_level=info
CR_request_logging=true
```

### Rate Limiting

Currently disabled, but configurable for future use.

### CORS

Configured for localhost origins in development. Production should restrict to specific domains.

---

## 📊 Performance

### Response Times

- Health check: < 5ms
- Data endpoints: < 50ms
- Analysis (Mock): < 1s
- Analysis (OpenAI): ~20-30s
- Tools: < 1s each
- Reporting: < 500ms
- Chat (Mock): < 200ms
- Chat (OpenAI): 1-4s

### Throughput

- Concurrent requests: 100+
- File uploads: 10MB max
- Memory usage: < 512MB
- CPU usage: < 25% (typical load)

---

## 🧪 Testing

### Unit Tests

```bash
python -m pytest tests/test_api_endpoints.py -v
```

### Integration Tests

```bash
# Test all endpoints
python test_integration.py

# Load testing
python load_test.py
```

### Manual Testing

Use the interactive Swagger UI at `http://localhost:8000/docs`

---

## 📚 Additional Resources

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Spec:** http://localhost:8000/api/v1/openapi.json
- **Main README:** ../README.md
- **Phase 6 Report:** ../plans/PHASE_6_COMPLETION_REPORT.md

---

## 🤝 Support

For API issues:

1. Check server logs
2. Verify request format
3. Test with sample data
4. Review error responses
5. Check this documentation

---

**API Version:** 1.0
**Last Updated:** March 26, 2026
**Status:** Production Ready

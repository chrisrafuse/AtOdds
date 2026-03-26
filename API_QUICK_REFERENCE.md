# AtOdds API Quick Reference

**Base URL:** `http://localhost:8000/api/v1`
**Version:** 2.0 (AI-Enhanced)
**LLM Support:** OpenAI, Anthropic, Gemini, Mock

---

## 🚀 Quick Start

```bash
# Start server
python -m apps.web.run_api

# Health check
curl http://localhost:8000/health

# Interactive docs
# http://localhost:8000/docs
```

---

## 📋 All Endpoints (18 Total)

### Health & Info (2)
```
GET  /health                    # Health check
GET  /                          # API info
```

### Analysis (2)
```
POST /api/v1/analyze           # Run analysis
POST /api/v1/analyze/upload    # Upload & analyze
```

### Data (3)
```
GET  /api/v1/data/sample       # Sample data
POST /api/v1/data/validate     # Validate data
GET  /api/v1/data/schema       # Get schema
```

### Tools (5)
```
POST /api/v1/tools/arbitrage   # Arbitrage detection
POST /api/v1/tools/value       # Value edge detection
POST /api/v1/tools/outliers    # Outlier detection
POST /api/v1/tools/stale       # Stale line detection
POST /api/v1/tools/consensus   # Consensus pricing
```

### Reporting (3)
```
POST /api/v1/report/briefing   # Text briefing
POST /api/v1/report/json       # JSON briefing
GET  /api/v1/report/template   # Briefing template
```

### Chat (4)
```
POST /api/v1/chat/session      # Start session
POST /api/v1/chat/ask          # Ask question
DELETE /api/v1/chat/session/{id} # End session
GET  /api/v1/chat/sessions     # List sessions
```

---

## 🔥 Common Workflows

### 1. Complete Analysis

```bash
# Get sample data
curl http://localhost:8000/api/v1/data/sample > sample.json

# Run analysis
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d @sample.json

# Generate briefing
curl -X POST http://localhost:8000/api/v1/report/briefing \
  -H "Content-Type: application/json" \
  -d '{"CR_findings":[...],"CR_format":"text"}'
```

### 2. Individual Tools

```bash
# Arbitrage
curl -X POST http://localhost:8000/api/v1/tools/arbitrage \
  -H "Content-Type: application/json" \
  -d @sample.json

# Value edges
curl -X POST http://localhost:8000/api/v1/tools/value \
  -H "Content-Type: application/json" \
  -d @sample.json

# Consensus
curl -X POST http://localhost:8000/api/v1/tools/consensus \
  -H "Content-Type: application/json" \
  -d @sample.json
```

### 3. File Upload

```bash
# Upload and analyze
curl -X POST http://localhost:8000/api/v1/analyze/upload \
  -F "file=@my_odds_data.json"
```

### 4. Chat Session

```bash
# Start session
curl -X POST http://localhost:8000/api/v1/chat/session \
  -H "Content-Type: application/json" \
  -d '{"CR_context":"odds_analysis"}'

# Ask question (use session_id from response)
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"CR_session_id":"session_abc123","CR_question":"summary"}'
```

---

## 📊 Response Format

### Success Response
```json
{
  "CR_status": "success",
  "CR_data": {...},
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

### Error Response
```json
{
  "CR_status": "error",
  "CR_error": {
    "CR_code": "VALIDATION_ERROR",
    "CR_message": "Invalid input data"
  },
  "CR_metadata": {
    "CR_timestamp": "2026-03-26T16:35:42.111027",
    "CR_version": "1.0"
  }
}
```

---

## 🔧 Request Examples

### Analysis Request
```json
{
  "CR_snapshot": {
    "CR_events": [
      {
        "CR_event_id": "nba_20260320_lal_bos",
        "CR_event_name": "Boston Celtics vs Los Angeles Lakers",
        "CR_sport": "NBA",
        "CR_markets": [
          {
            "CR_name": "moneyline_DraftKings",
            "CR_bookmaker": "DraftKings",
            "CR_outcomes": [
              {"CR_name": "Boston Celtics", "CR_odds": -110},
              {"CR_name": "Los Angeles Lakers", "CR_odds": -110}
            ]
          }
        ]
      }
    ]
  }
}
```

### Tool Request
```json
{
  "CR_snapshot": {...}
}
```

### Briefing Request
```json
{
  "CR_findings": [...],
  "CR_format": "text",
  "CR_include_recommendations": true
}
```

### Chat Request
```json
{
  "CR_session_id": "session_abc123",
  "CR_question": "What are the best arbitrage opportunities?"
}
```

---

## 🎯 Finding Types

### Arbitrage
```json
{
  "CR_type": "arbitrage",
  "CR_profit_margin": 0.0235,
  "CR_bookmakers": ["DraftKings", "FanDuel"],
  "CR_description": "2.35% profit margin"
}
```

### Value Edge
```json
{
  "CR_type": "value_edge",
  "CR_edge_size": 0.05,
  "CR_confidence": 0.85,
  "CR_description": "5% value edge detected"
}
```

### Outlier
```json
{
  "CR_type": "outlier",
  "CR_z_score": 2.5,
  "CR_deviation": "statistical",
  "CR_description": "Odds statistically unusual"
}
```

### Stale Line
```json
{
  "CR_type": "stale_line",
  "CR_hours_old": 48,
  "CR_last_updated": "2026-03-24T16:35:42.111027",
  "CR_description": "Line not updated in 48 hours"
}
```

---

## 🚨 Common Errors

### 400 Bad Request
- Invalid JSON format
- Missing required fields
- Empty events array

### 404 Not Found
- Invalid endpoint URL
- Resource not found

### 422 Validation Error
- Data structure validation failed
- Invalid field values
- CR_ prefix missing

### 500 Internal Error
- Processing failure
- Data analysis error
- Server issue

---

## 📝 Tips & Tricks

### 1. Always Use Sample Data First
```bash
curl http://localhost:8000/api/v1/data/sample
```

### 2. Validate Before Analysis
```bash
curl -X POST http://localhost:8000/api/v1/data/validate \
  -H "Content-Type: application/json" \
  -d @your_data.json
```

### 3. Use Interactive Docs
Visit `http://localhost:8000/docs` for:
- Try-it-out functionality
- Schema validation
- Example requests

### 4. Check Health Regularly
```bash
curl http://localhost:8000/health
```

### 5. Monitor Response Times
- Analysis: < 5s
- Tools: < 1s
- Data: < 50ms

---

## 🔍 Debugging

### Enable Debug Mode
```env
CR_debug_mode=true
```

### Check Logs
Server logs show:
- Request timestamps
- Response times
- Error details

### Validate Data Structure
```bash
curl -X POST http://localhost:8000/api/v1/data/validate \
  -H "Content-Type: application/json" \
  -d @your_data.json
```

---

## 📚 More Documentation

- **Full API Docs:** API_DOCUMENTATION.md
- **Main README:** README.md
- **Interactive:** http://localhost:8000/docs
- **Phase 6 Report:** plans/PHASE_6_COMPLETION_REPORT.md

---

**Need help? Check the server logs or visit the interactive docs!**

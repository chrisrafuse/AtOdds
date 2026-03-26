# AtOdds Web API

FastAPI-based REST API for the AtOdds odds analysis system.

## Overview

The AtOdds Web API provides programmatic access to the complete odds analysis engine through a RESTful interface. All endpoints use CR_ prefix compliance and return JSON responses.

## Quick Start

### Installation

1. Install dependencies:
```bash
pip install -r requirements-web.txt
```

2. Configure environment (optional):
```bash
cp apps/web/.env.example apps/web/.env
# Edit .env with your settings
```

3. Start the server:
```bash
python apps/web/run_api.py
```

The API will be available at `http://localhost:8000`

### Development Mode

For development with auto-reload:
```bash
# Set in .env or environment
export CR_debug_mode=true
export CR_reload_on_change=true

python apps/web/run_api.py
```

## API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Endpoints

#### Health Check
```bash
GET /health
```

#### Analysis
```bash
POST /api/v1/analyze              # Run analysis on snapshot
POST /api/v1/analyze/upload       # Upload file and analyze
```

#### Data
```bash
GET  /api/v1/data/sample          # Get sample data
POST /api/v1/data/validate        # Validate snapshot
GET  /api/v1/data/schema          # Get schema definitions
```

#### Tools
```bash
POST /api/v1/tools/arbitrage      # Detect arbitrage
POST /api/v1/tools/value          # Detect value edges
POST /api/v1/tools/outliers       # Detect outliers
POST /api/v1/tools/stale          # Detect stale lines
POST /api/v1/tools/consensus      # Calculate consensus
```

#### Reporting
```bash
POST /api/v1/report/briefing      # Generate text briefing
POST /api/v1/report/json          # Generate JSON briefing
GET  /api/v1/report/template      # Get template structure
```

#### Chat
```bash
POST   /api/v1/chat/session       # Start chat session
POST   /api/v1/chat/ask           # Ask question
DELETE /api/v1/chat/session/{id}  # End session
GET    /api/v1/chat/sessions      # List active sessions
```

## Usage Examples

### Analyze Odds Data

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "CR_snapshot": {
      "CR_events": [...],
      "CR_timestamp": "2026-03-26T15:00:00Z",
      "CR_source": "api_request"
    }
  }'
```

### Upload File

```bash
curl -X POST http://localhost:8000/api/v1/analyze/upload \
  -F "file=@data/sample_odds.json"
```

### Get Sample Data

```bash
curl http://localhost:8000/api/v1/data/sample
```

### Start Chat Session

```bash
# Create session
curl -X POST http://localhost:8000/api/v1/chat/session \
  -H "Content-Type: application/json" \
  -d '{
    "CR_snapshot": {...},
    "CR_findings": [...]
  }'

# Ask question
curl -X POST http://localhost:8000/api/v1/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "CR_session_id": "session_abc123",
    "CR_question": "What arbitrage opportunities exist?"
  }'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CR_api_host` | 0.0.0.0 | Server host |
| `CR_api_port` | 8000 | Server port |
| `CR_api_workers` | 4 | Number of workers (production) |
| `CR_cors_origins` | localhost | Allowed CORS origins |
| `CR_log_level` | INFO | Logging level |
| `CR_debug_mode` | false | Enable debug mode |
| `CR_reload_on_change` | false | Auto-reload on code changes |

### CORS Configuration

By default, CORS is configured for local development. For production, update `CR_cors_origins` in your environment:

```bash
CR_cors_origins=https://yourdomain.com,https://www.yourdomain.com
```

## Docker Deployment

### Build Image

```bash
docker build -t atodds-api -f apps/web/Dockerfile .
```

### Run Container

```bash
docker run -p 8000:8000 atodds-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build:
      context: .
      dockerfile: apps/web/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CR_api_host=0.0.0.0
      - CR_api_port=8000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Testing

### Run API Tests

```bash
pytest tests/test_api_endpoints.py -v
```

### Test Coverage

```bash
pytest tests/test_api_endpoints.py --cov=apps.web.api --cov-report=html
```

## Performance

### Response Time Targets

- Health check: < 10ms
- Data endpoints: < 100ms
- Analysis: < 5s for typical dataset
- Tools: < 1s per tool
- Reporting: < 500ms
- Chat: < 200ms

### Rate Limits

- Default: 100 requests/minute per IP
- Analysis: 10 requests/minute per IP
- Upload: 5 requests/minute per IP

### File Upload Limits

- Maximum file size: 10MB
- Allowed formats: .json

## Production Deployment

### Recommended Setup

1. **Reverse Proxy**: Use Nginx or Traefik
2. **SSL/TLS**: Enable HTTPS with Let's Encrypt
3. **Workers**: Set `CR_api_workers` based on CPU cores
4. **Monitoring**: Use Prometheus + Grafana
5. **Logging**: Centralized logging with ELK stack

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name api.atodds.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=AtOdds API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/atodds
ExecStart=/usr/bin/python3 apps/web/run_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Metrics Endpoint (Future)

```bash
GET /metrics  # Prometheus metrics
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### CORS Errors

Ensure your frontend origin is in `CR_cors_origins`:

```bash
export CR_cors_origins=http://localhost:3000
```

### Import Errors

Ensure project root is in Python path:

```bash
export PYTHONPATH=/path/to/AtOdds:$PYTHONPATH
```

## Development

### Project Structure

```
apps/web/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── models/              # Pydantic models
│   │   ├── requests.py
│   │   └── responses.py
│   └── routers/             # API endpoints
│       ├── analysis.py
│       ├── data.py
│       ├── tools.py
│       ├── reporting.py
│       └── chat.py
├── run_api.py               # Server startup
├── Dockerfile               # Docker configuration
└── README.md                # This file
```

### Adding New Endpoints

1. Create router in `apps/web/api/routers/`
2. Define request/response models in `apps/web/api/models/`
3. Include router in `apps/web/api/main.py`
4. Add tests in `tests/test_api_endpoints.py`
5. Update API documentation

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/atodds/issues
- Documentation: See `docs/API.md`

---

**Version**: 1.0  
**Phase**: 6 (Web API Layer)  
**Status**: Production Ready

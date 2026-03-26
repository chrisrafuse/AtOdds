#!/usr/bin/env python3
"""
API Endpoint Tests for AtOdds Web API
Phase 6: Comprehensive tests for all API endpoints
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.web.api.main import app
from packages.data.contracts import create_CR_outcome, create_CR_market, create_CR_event, create_CR_snapshot


# Create test client
client = TestClient(app)


# Test fixtures
@pytest.fixture
def CR_sample_snapshot():
    """Create a sample CR_ snapshot for testing"""
    CR_outcome1 = create_CR_outcome("Lakers", -110)
    CR_outcome2 = create_CR_outcome("Celtics", -110)
    CR_market = create_CR_market("moneyline_DraftKings", [CR_outcome1, CR_outcome2], "DraftKings")
    CR_event = create_CR_event("test_game_1", "Lakers vs Celtics", "NBA", [CR_market])
    CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
    return CR_snapshot


@pytest.fixture
def CR_sample_findings():
    """Create sample CR_ findings for testing"""
    return [
        {
            "CR_type": "arbitrage",
            "CR_event_id": "test_game_1",
            "CR_market_name": "moneyline_DraftKings",
            "CR_confidence": 0.95,
            "CR_description": "Test arbitrage opportunity",
            "CR_metadata": {"CR_profit_margin": 0.02}
        }
    ]


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "healthy"
        assert "CR_version" in data
        assert "CR_timestamp" in data


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_api"] == "AtOdds Odds Analysis API"
        assert "CR_version" in data
        assert "CR_endpoints" in data


class TestAnalysisEndpoints:
    """Test analysis endpoints"""

    def test_analyze_endpoint(self, CR_sample_snapshot):
        """Test POST /api/v1/analyze"""
        response = client.post(
            "/api/v1/analyze",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_data" in data
        assert "CR_findings" in data["CR_data"]
        assert "CR_metadata" in data

    def test_analyze_invalid_snapshot(self):
        """Test analyze with invalid snapshot"""
        response = client.post(
            "/api/v1/analyze",
            json={"CR_snapshot": {"CR_events": []}}
        )
        # Should return 400 for empty events (invalid)
        assert response.status_code == 400

    def test_analyze_missing_snapshot(self):
        """Test analyze with missing snapshot"""
        response = client.post(
            "/api/v1/analyze",
            json={}
        )
        assert response.status_code == 422  # Validation error


class TestDataEndpoints:
    """Test data endpoints"""

    def test_get_sample_data(self):
        """Test GET /api/v1/data/sample"""
        response = client.get("/api/v1/data/sample")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_snapshot" in data["CR_data"]

    def test_validate_data(self, CR_sample_snapshot):
        """Test POST /api/v1/data/validate"""
        response = client.post(
            "/api/v1/data/validate",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_is_valid" in data["CR_data"]
        assert "CR_errors" in data["CR_data"]

    def test_get_schema(self):
        """Test GET /api/v1/data/schema"""
        response = client.get("/api/v1/data/schema")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_schemas" in data["CR_data"]
        assert "CR_outcome" in data["CR_data"]["CR_schemas"]
        assert "CR_market" in data["CR_data"]["CR_schemas"]


class TestToolsEndpoints:
    """Test tools endpoints"""

    def test_arbitrage_tool(self, CR_sample_snapshot):
        """Test POST /api/v1/tools/arbitrage"""
        response = client.post(
            "/api/v1/tools/arbitrage",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_findings" in data["CR_data"]
        assert "CR_count" in data["CR_data"]

    def test_value_tool(self, CR_sample_snapshot):
        """Test POST /api/v1/tools/value"""
        response = client.post(
            "/api/v1/tools/value",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_findings" in data["CR_data"]

    def test_outliers_tool(self, CR_sample_snapshot):
        """Test POST /api/v1/tools/outliers"""
        response = client.post(
            "/api/v1/tools/outliers",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

    def test_stale_tool(self, CR_sample_snapshot):
        """Test POST /api/v1/tools/stale"""
        response = client.post(
            "/api/v1/tools/stale",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

    def test_consensus_tool(self, CR_sample_snapshot):
        """Test POST /api/v1/tools/consensus"""
        response = client.post(
            "/api/v1/tools/consensus",
            json={"CR_snapshot": CR_sample_snapshot}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_consensus" in data["CR_data"]


class TestReportingEndpoints:
    """Test reporting endpoints"""

    def test_generate_briefing(self, CR_sample_findings, CR_sample_snapshot):
        """Test POST /api/v1/report/briefing"""
        response = client.post(
            "/api/v1/report/briefing",
            json={
                "CR_findings": CR_sample_findings,
                "CR_snapshot": CR_sample_snapshot,
                "CR_format": "text"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_briefing" in data["CR_data"]
        assert isinstance(data["CR_data"]["CR_briefing"], str)

    def test_generate_json_briefing(self, CR_sample_findings, CR_sample_snapshot):
        """Test POST /api/v1/report/json"""
        response = client.post(
            "/api/v1/report/json",
            json={
                "CR_findings": CR_sample_findings,
                "CR_snapshot": CR_sample_snapshot
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_briefing" in data["CR_data"]
        assert isinstance(data["CR_data"]["CR_briefing"], dict)

    def test_get_template(self):
        """Test GET /api/v1/report/template"""
        response = client.get("/api/v1/report/template")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_template" in data["CR_data"]


class TestChatEndpoints:
    """Test chat endpoints"""

    def test_create_session(self, CR_sample_snapshot, CR_sample_findings):
        """Test POST /api/v1/chat/session"""
        response = client.post(
            "/api/v1/chat/session",
            json={
                "CR_snapshot": CR_sample_snapshot,
                "CR_findings": CR_sample_findings
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_session_id" in data["CR_data"]
        assert "CR_expires_at" in data["CR_data"]

        return data["CR_data"]["CR_session_id"]

    def test_ask_question(self, CR_sample_snapshot, CR_sample_findings):
        """Test POST /api/v1/chat/ask"""
        # First create a session
        session_response = client.post(
            "/api/v1/chat/session",
            json={
                "CR_snapshot": CR_sample_snapshot,
                "CR_findings": CR_sample_findings
            }
        )
        CR_session_id = session_response.json()["CR_data"]["CR_session_id"]

        # Ask a question
        response = client.post(
            "/api/v1/chat/ask",
            json={
                "CR_session_id": CR_session_id,
                "CR_question": "What arbitrage opportunities exist?"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_answer" in data["CR_data"]
        assert "CR_sources" in data["CR_data"]

    def test_ask_invalid_session(self):
        """Test asking question with invalid session"""
        response = client.post(
            "/api/v1/chat/ask",
            json={
                "CR_session_id": "invalid_session",
                "CR_question": "test"
            }
        )
        assert response.status_code == 404

    def test_delete_session(self, CR_sample_snapshot, CR_sample_findings):
        """Test DELETE /api/v1/chat/session/{session_id}"""
        # Create session
        session_response = client.post(
            "/api/v1/chat/session",
            json={
                "CR_snapshot": CR_sample_snapshot,
                "CR_findings": CR_sample_findings
            }
        )
        CR_session_id = session_response.json()["CR_data"]["CR_session_id"]

        # Delete session
        response = client.delete(f"/api/v1/chat/session/{CR_session_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"

    def test_list_sessions(self):
        """Test GET /api/v1/chat/sessions"""
        response = client.get("/api/v1/chat/sessions")
        assert response.status_code == 200

        data = response.json()
        assert data["CR_status"] == "success"
        assert "CR_active_sessions" in data["CR_data"]


class TestErrorHandling:
    """Test error handling"""

    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self):
        """Test invalid JSON in request"""
        response = client.post(
            "/api/v1/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


def run_tests():
    """Run all API tests"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()

#!/usr/bin/env python3
"""
Minimal test server without pydantic for Python 3.14 compatibility.
Run with: python run_minimal.py
Then visit http://localhost:8000
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Use built-in http.server instead of FastAPI for Python 3.14 testing
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

# Load core engine (no pydantic dependency)
from packages.core_engine.odds_math import (
    compute_CR_implied_probability,
    compute_CR_vig,
    compute_CR_math_explanation,
    compute_CR_vig_explanation
)
from packages.core_engine.detectors import (
    detect_CR_arbitrage,
    detect_CR_value_edge,
    detect_CR_outlier,
    detect_CR_stale_line
)
from packages.reporting.rankings import generate_CR_sportsbook_rankings
from packages.chat.chat_cr import CR_OddsChat
from packages.agent.agent import execute_CR_analysis_pipeline

# In-memory chat sessions
_CR_CHAT_SESSIONS: dict = {}

# Load sample data
def load_sample_data():
    with open(PROJECT_ROOT / "data" / "sample_odds.json", "r") as f:
        return json.load(f)

class AtOddsHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.serve_file("apps/web/static/index.html", "text/html")
        elif parsed.path.startswith("/static/"):
            # Remove /static/ prefix to get actual file path
            file_path = parsed.path[8:]  # Remove /static/ prefix
            full_path = PROJECT_ROOT / "apps" / "web" / "static" / file_path
            print(f"Serving static file: {parsed.path} -> {full_path}")
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-type', self.guess_content_type(file_path))
                self.send_header('Content-length', str(len(content)))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
            else:
                print(f"File not found: {full_path}")
                self.send_error(404)
        elif parsed.path == "/api/v1/health":
            self.send_json({
                "CR_status": "healthy",
                "CR_version": "2.0",
                "CR_timestamp": datetime.now().isoformat()
            })
        elif parsed.path == "/api/v1/data/sample":
            try:
                snapshot = load_sample_data()
                self.send_json({
                    "CR_status": "success",
                    "CR_data": {"CR_snapshot": snapshot},
                    "CR_metadata": {"CR_timestamp": datetime.now().isoformat(), "CR_version": "2.0"}
                })
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if parsed.path == "/api/v1/analyze":
            self.handle_analyze(data)
        elif parsed.path == "/api/v1/report/briefing":
            self.handle_briefing(data)
        elif parsed.path == "/api/v1/chat/session":
            self.handle_chat_session(data)
        elif parsed.path == "/api/v1/chat/ask":
            self.handle_chat_ask(data)
        else:
            self.send_error(404)

    def handle_analyze(self, data):
        """Run analysis pipeline via execute_CR_analysis_pipeline (mock LLM, no pydantic needed)"""
        import time
        try:
            snapshot = data.get("CR_snapshot")
            if not snapshot:
                self.send_error(400, "Missing CR_snapshot")
                return

            CR_start = time.time()
            results = execute_CR_analysis_pipeline(snapshot)
            CR_ms = int((time.time() - CR_start) * 1000)

            self.send_json({
                "CR_status": "success",
                "CR_data": results,
                "CR_metadata": {
                    "CR_timestamp": datetime.now().isoformat(),
                    "CR_version": "2.0",
                    "CR_execution_time_ms": CR_ms
                }
            })

        except Exception as e:
            self.send_error(500, f"Analysis failed: {str(e)}")

    def handle_briefing(self, data):
        """Generate briefing from findings"""
        try:
            findings = data.get("CR_findings", [])
            snapshot = data.get("CR_snapshot")
            rankings = data.get("CR_sportsbook_rankings", [])

            # Simple text briefing
            lines = [
                "=" * 60,
                "CR_ ODDS ANALYSIS BRIEFING",
                "=" * 60,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "📊 CR_ SUMMARY",
                "-" * 30,
                f"Total Findings: {len(findings)}",
                ""
            ]

            # Add top findings
            lines.append("🔍 TOP CR_ FINDINGS")
            lines.append("-" * 30)
            for i, finding in enumerate(findings[:5], 1):
                lines.append(f"{i}. {finding.get('CR_type', 'unknown').upper()}")
                lines.append(f"   Event: {finding.get('CR_event_id', 'N/A')}")
                lines.append(f"   Description: {finding.get('CR_description', 'N/A')}")

                # Add math proof if available
                math_proof = finding.get('CR_math_proof')
                if math_proof and 'CR_formula' in math_proof:
                    lines.append(f"   Math: {math_proof['CR_formula']}")
                lines.append("")

            # Add rankings if available
            if rankings:
                lines.append("📊 SPORTSBOOK QUALITY RANKINGS")
                lines.append("-" * 30)
                for r in rankings[:5]:
                    lines.append(f"  {r['CR_rank']}. {r['CR_bookmaker']}: {r['CR_quality_score']} ({r['CR_verdict']})")
                lines.append("")

            lines.extend([
                "=" * 60,
                "END OF CR_ BRIEFING",
                "=" * 60
            ])

            response = {
                "CR_status": "success",
                "CR_data": {
                    "CR_briefing": "\n".join(lines),
                    "CR_format": "text",
                    "CR_findings_count": len(findings),
                    "CR_sportsbook_rankings": rankings
                },
                "CR_metadata": {
                    "CR_timestamp": datetime.now().isoformat(),
                    "CR_version": "2.0"
                }
            }
            self.send_json(response)

        except Exception as e:
            self.send_error(500, f"Briefing failed: {str(e)}")

    def handle_chat_session(self, data):
        """Create a chat session backed by CR_OddsChat"""
        try:
            import uuid
            snapshot = data.get("CR_snapshot") or {}
            findings = data.get("CR_findings") or []

            chat = CR_OddsChat(CR_snapshot=snapshot, CR_findings=findings)
            session_id = str(uuid.uuid4())
            _CR_CHAT_SESSIONS[session_id] = chat

            self.send_json({
                "CR_status": "success",
                "CR_data": {
                    "CR_session_id": session_id,
                    "CR_provider": "deterministic",
                    "CR_message": "Session ready"
                },
                "CR_metadata": {"CR_timestamp": datetime.now().isoformat(), "CR_version": "2.0"}
            })
        except Exception as e:
            self.send_json({
                "CR_status": "error",
                "CR_error": {"CR_code": "CHAT_SESSION_ERROR", "CR_message": str(e)}
            })

    def handle_chat_ask(self, data):
        """Answer a question from the chat session"""
        try:
            session_id = data.get("CR_session_id", "")
            question = data.get("CR_question", "").strip()

            if not question:
                self.send_error(400, "Missing CR_question")
                return

            chat = _CR_CHAT_SESSIONS.get(session_id)
            if not chat:
                self.send_json({
                    "CR_status": "error",
                    "CR_error": {"CR_code": "SESSION_NOT_FOUND", "CR_message": "Session expired or invalid"}
                })
                return

            result = chat.answer_CR_question(question)
            self.send_json({
                "CR_status": "success",
                "CR_data": {
                    "CR_answer": result.get("CR_answer", "No answer available."),
                    "CR_confidence": result.get("CR_confidence", 0.0),
                    "CR_sources": result.get("CR_sources", []),
                    "CR_tool_trace": []
                },
                "CR_metadata": {"CR_timestamp": datetime.now().isoformat(), "CR_version": "2.0"}
            })
        except Exception as e:
            self.send_json({
                "CR_status": "error",
                "CR_error": {"CR_code": "CHAT_ASK_ERROR", "CR_message": str(e)}
            })

    def serve_file(self, file_path, content_type):
        """Serve a static file"""
        try:
            full_path = PROJECT_ROOT / file_path
            with open(full_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404)

    def send_json(self, data):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data)

    def guess_content_type(self, file_path):
        """Guess content type from file extension"""
        if file_path.endswith('.html'):
            return 'text/html'
        elif file_path.endswith('.css'):
            return 'text/css'
        elif file_path.endswith('.js'):
            return 'application/javascript'
        else:
            return 'text/plain'

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    port = int(os.environ.get("PORT", 8000))

    print(f"🚀 AtOdds Minimal Server (Python 3.14 compatible)")
    print(f"📍 Running on http://localhost:{port}")
    print(f"📊 Open your browser and upload data/sample_odds.json")
    print(f"🔧 Note: This is minimal mode without LLM features")
    print(f"   For full features, use Python 3.11/3.12 and pip install -r requirements-web.txt")

    server = HTTPServer(('localhost', port), AtOddsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()

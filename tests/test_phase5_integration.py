#!/usr/bin/env python3
"""
Test Suite for Phase 5: CR Signature Migration - Complete System Integration
Tests for CLI entry point and full system integration with CR_ prefix compliance
"""

import unittest
import sys
import os
import subprocess
import tempfile
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_snapshot
)

from packages.data.loader import load_data
from packages.agent.agent import execute_CR_analysis_pipeline
from packages.reporting.briefing import generate_CR_briefing, generate_CR_json_briefing
from packages.chat.chat_cr import start_CR_chat_session
from packages.observability.trace_cr import CR_Tracer


class TestCLIEntryPoint(unittest.TestCase):
    """Test CLI entry point with CR_ prefix"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.CR_cli_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'apps', 
            'cli', 
            'main.py'
        )
        self.CR_test_data_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.CR_test_data_dir):
            shutil.rmtree(self.CR_test_data_dir)
    
    def test_cli_help(self):
        """Test CLI help output"""
        CR_result = subprocess.run(
            [sys.executable, self.CR_cli_path, '--help'],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(CR_result.returncode, 0)
        self.assertIn('AtOdds', CR_result.stdout)
        self.assertIn('CR_', CR_result.stdout)
        self.assertIn('--data-file', CR_result.stdout)
        self.assertIn('--output-format', CR_result.stdout)
        self.assertIn('--trace', CR_result.stdout)
        self.assertIn('--verbose', CR_result.stdout)
    
    def test_cli_with_test_data(self):
        """Test CLI with test data file"""
        # Create test data file
        CR_test_data = {
            "odds": [
                {
                    "id": "test_game_1",
                    "sport_key": "basketball_nba",
                    "sport_title": "NBA",
                    "commence_time": datetime.now().isoformat(),
                    "home_team": "Lakers",
                    "away_team": "Warriors",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Lakers", "price": -110},
                                        {"name": "Warriors", "price": -110}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        CR_test_file = os.path.join(self.CR_test_data_dir, 'test_odds.json')
        with open(CR_test_file, 'w') as CR_f:
            json.dump(CR_test_data, CR_f)
        
        # Run CLI with test data
        CR_result = subprocess.run(
            [sys.executable, self.CR_cli_path, '--data-file', CR_test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should complete successfully
        self.assertEqual(CR_result.returncode, 0)
        self.assertIn('CR_', CR_result.stdout)
        self.assertIn('BRIEFING', CR_result.stdout)
    
    def test_cli_json_output(self):
        """Test CLI with JSON output format"""
        # Create minimal test data
        CR_test_data = {
            "odds": [
                {
                    "id": "test_game_2",
                    "sport_key": "basketball_nba",
                    "sport_title": "NBA",
                    "commence_time": datetime.now().isoformat(),
                    "home_team": "Lakers",
                    "away_team": "Warriors",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Lakers", "price": -110},
                                        {"name": "Warriors", "price": -110}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        CR_test_file = os.path.join(self.CR_test_data_dir, 'test_odds_json.json')
        with open(CR_test_file, 'w') as CR_f:
            json.dump(CR_test_data, CR_f)
        
        # Run CLI with JSON output
        CR_result = subprocess.run(
            [sys.executable, self.CR_cli_path, '--data-file', CR_test_file, '--output-format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        self.assertEqual(CR_result.returncode, 0)
        
        # Parse JSON output
        CR_output = json.loads(CR_result.stdout)
        self.assertIn('CR_metadata', CR_output)
        self.assertIn('CR_summary', CR_output)
        self.assertIn('CR_findings', CR_output)


class TestCompleteSystemIntegration(unittest.TestCase):
    """Test complete system integration across all phases"""
    
    def test_phase1_to_phase5_integration(self):
        """Test integration from Phase 1 (data) through Phase 5 (CLI)"""
        # Phase 1: Create CR_ data structures
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")
        CR_event = create_CR_event("game_1", "Lakers vs Warriors", "NBA", [CR_market])
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        # Phase 2 & 3: Run analysis pipeline
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        
        # Phase 4: Generate briefing and chat
        CR_findings = CR_results['CR_findings']
        CR_briefing = generate_CR_briefing(CR_findings, CR_snapshot)
        CR_chat = start_CR_chat_session(CR_snapshot, CR_findings)
        CR_response = CR_chat.answer_CR_question("summary")
        
        # Verify all phases work together
        self.assertIsInstance(CR_snapshot, dict)
        self.assertIsInstance(CR_results, dict)
        self.assertIsInstance(CR_briefing, str)
        self.assertIsInstance(CR_response, dict)
        
        self.assertIn('CR_', CR_briefing)
        self.assertIn('CR_answer', CR_response)
    
    def test_end_to_end_with_tracing(self):
        """Test complete end-to-end workflow with tracing"""
        # Create tracer
        CR_tracer = CR_Tracer(CR_log_dir=tempfile.mkdtemp())
        CR_tracer.start_CR_session()
        
        # Create data
        CR_outcome1 = create_CR_outcome("Lakers +5.5", -110)
        CR_outcome2 = create_CR_outcome("Warriors -5.5", -110)
        CR_market = create_CR_market("spread", [CR_outcome1, CR_outcome2], "FanDuel")
        CR_event = create_CR_event("game_2", "Lakers vs Warriors", "NBA", [CR_market])
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        # Run pipeline
        CR_tracer.log_CR_step("data_creation", "Created CR_ snapshot")
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        CR_tracer.log_CR_step("analysis", "Completed CR_ analysis")
        
        # Generate outputs
        CR_findings = CR_results['CR_findings']
        CR_briefing = generate_CR_briefing(CR_findings, CR_snapshot)
        CR_json_briefing = generate_CR_json_briefing(CR_findings, CR_snapshot)
        CR_tracer.log_CR_step("reporting", "Generated CR_ briefings")
        
        # End tracing
        CR_summary = CR_tracer.end_CR_session()
        
        # Verify tracing captured everything
        self.assertIn('CR_session_id', CR_summary)
        self.assertIn('CR_total_steps', CR_summary)
        self.assertGreater(CR_summary['CR_total_steps'], 0)
    
    def test_all_modules_cr_compliant(self):
        """Test that all modules use CR_ prefix consistently"""
        # Import all modules
        from packages.data.contracts import create_CR_outcome
        from packages.data.loader import load_data
        from packages.core_engine.odds_math import compute_CR_implied_probability
        from packages.core_engine.consensus import compute_CR_best_lines
        from packages.core_engine.detectors import detect_CR_arbitrage
        from packages.tools.registry import CR_TOOL_REGISTRY
        from packages.agent.agent import run_CR_agent
        from packages.agent.prompts import get_CR_system_prompt
        from packages.reporting.briefing import generate_CR_briefing
        from packages.chat.chat_cr import CR_OddsChat
        from packages.observability.trace_cr import CR_Tracer
        
        # Verify all imports work
        self.assertTrue(callable(create_CR_outcome))
        self.assertTrue(callable(load_data))
        self.assertTrue(callable(compute_CR_implied_probability))
        self.assertTrue(callable(compute_CR_best_lines))
        self.assertTrue(callable(detect_CR_arbitrage))
        self.assertIsInstance(CR_TOOL_REGISTRY, dict)
        self.assertTrue(callable(run_CR_agent))
        self.assertTrue(callable(get_CR_system_prompt))
        self.assertTrue(callable(generate_CR_briefing))
        self.assertTrue(callable(CR_OddsChat))
        self.assertTrue(callable(CR_Tracer))


class TestSystemPerformance(unittest.TestCase):
    """Test system performance with CR_ prefix"""
    
    def test_pipeline_performance(self):
        """Test that CR_ pipeline completes in reasonable time"""
        import time
        
        # Create test data
        CR_markets = []
        for CR_i in range(10):  # 10 markets
            CR_outcome1 = create_CR_outcome(f"Team A {CR_i}", -110)
            CR_outcome2 = create_CR_outcome(f"Team B {CR_i}", -110)
            CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")
            CR_markets.append(CR_market)
        
        CR_event = create_CR_event("perf_test", "Performance Test", "NBA", CR_markets)
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        # Time the pipeline
        CR_start = time.time()
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        CR_duration = time.time() - CR_start
        
        # Should complete in under 5 seconds
        self.assertLess(CR_duration, 5.0)
        self.assertIsInstance(CR_results, dict)
        self.assertIn('CR_findings', CR_results)


class TestErrorHandling(unittest.TestCase):
    """Test error handling across the system"""
    
    def test_invalid_data_handling(self):
        """Test that system handles invalid data gracefully"""
        # Create invalid snapshot (empty events)
        CR_snapshot = create_CR_snapshot([], datetime.now().isoformat(), "test")
        
        # Should not crash
        CR_results = execute_CR_analysis_pipeline(CR_snapshot)
        
        self.assertIsInstance(CR_results, dict)
        self.assertIn('CR_findings', CR_results)
        self.assertEqual(len(CR_results['CR_findings']), 0)
    
    def test_missing_data_file(self):
        """Test CLI with missing data file"""
        CR_result = subprocess.run(
            [sys.executable, 
             os.path.join(os.path.dirname(__file__), '..', 'apps', 'cli', 'main.py'),
             '--data-file', '/nonexistent/file.json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should exit with error code
        self.assertEqual(CR_result.returncode, 1)
        self.assertIn('Error', CR_result.stdout)


def run_tests():
    """Run all tests and generate report"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

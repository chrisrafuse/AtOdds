#!/usr/bin/env python3
"""
Test Suite for Phase 4: CR Signature Migration - Interface Modules
Tests for prompts, briefing, chat, and observability with CR_ prefix compliance
"""

import unittest
import sys
import os
from datetime import datetime
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.agent.prompts import (
    get_CR_system_prompt,
    format_CR_user_prompt,
    CR_SYSTEM_PROMPT
)

from packages.reporting.briefing import (
    generate_CR_briefing,
    generate_CR_json_briefing,
    generate_CR_recommendations
)

from packages.chat.chat_cr import (
    CR_OddsChat,
    start_CR_chat_session
)

from packages.observability.trace_cr import (
    CR_Tracer,
    get_CR_tracer,
    create_CR_trace_session,
    trace_CR_tool_call,
    trace_CR_step
)

from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_snapshot,
    create_CR_finding
)

from packages.agent.agent import (
    run_CR_agent,
    generate_CR_analysis_summary
)


class TestPromptsModule(unittest.TestCase):
    """Test prompts module with CR_ prefix"""
    
    def test_get_system_prompt(self):
        """Test getting CR_ system prompt"""
        CR_prompt = get_CR_system_prompt()
        
        self.assertIsInstance(CR_prompt, str)
        self.assertIn('CR_', CR_prompt)
        self.assertIn('odds analysis', CR_prompt.lower())
        self.assertGreater(len(CR_prompt), 100)
    
    def test_system_prompt_constant(self):
        """Test CR_SYSTEM_PROMPT constant exists"""
        self.assertIsInstance(CR_SYSTEM_PROMPT, str)
        self.assertIn('CR_', CR_SYSTEM_PROMPT)
    
    def test_format_user_prompt(self):
        """Test formatting CR_ user prompt with snapshot data"""
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")
        CR_event = create_CR_event("game_1", "Lakers vs Warriors", "NBA", [CR_market])
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        CR_prompt = format_CR_user_prompt(CR_snapshot)
        
        self.assertIsInstance(CR_prompt, str)
        self.assertIn('CR_', CR_prompt)
        self.assertIn('1', CR_prompt)  # Event count
        self.assertIn('DraftKings', CR_prompt)
    
    def test_format_user_prompt_empty_snapshot(self):
        """Test formatting prompt with empty snapshot"""
        CR_snapshot = create_CR_snapshot([], datetime.now().isoformat(), "test")
        CR_prompt = format_CR_user_prompt(CR_snapshot)
        
        self.assertIsInstance(CR_prompt, str)
        self.assertIn('0', CR_prompt)  # Zero events


class TestBriefingModule(unittest.TestCase):
    """Test briefing module with CR_ prefix"""
    
    def setUp(self):
        """Set up test fixtures"""
        CR_finding1 = create_CR_finding(
            CR_type='arbitrage',
            CR_description='Test arbitrage opportunity',
            CR_confidence=0.9,
            CR_event_id='game_1',
            CR_market_name='moneyline',
            CR_bookmakers=['DraftKings', 'FanDuel'],
            CR_details={'CR_profit_margin': 0.05}
        )
        
        CR_finding2 = create_CR_finding(
            CR_type='value_edge',
            CR_description='Test value edge',
            CR_confidence=0.7,
            CR_event_id='game_1',
            CR_market_name='spread',
            CR_bookmakers=['DraftKings'],
            CR_details={'CR_edge': 0.08}
        )
        
        self.CR_findings = [CR_finding1, CR_finding2]
    
    def test_generate_briefing(self):
        """Test generating CR_ text briefing"""
        CR_briefing = generate_CR_briefing(self.CR_findings)
        
        self.assertIsInstance(CR_briefing, str)
        self.assertIn('CR_', CR_briefing)
        self.assertIn('BRIEFING', CR_briefing)
        self.assertIn('arbitrage', CR_briefing.lower())
        self.assertIn('value_edge', CR_briefing.lower())
        self.assertGreater(len(CR_briefing), 100)
    
    def test_generate_json_briefing(self):
        """Test generating CR_ JSON briefing"""
        CR_json_briefing = generate_CR_json_briefing(self.CR_findings)
        
        self.assertIsInstance(CR_json_briefing, dict)
        self.assertIn('CR_metadata', CR_json_briefing)
        self.assertIn('CR_summary', CR_json_briefing)
        self.assertIn('CR_findings', CR_json_briefing)
        self.assertIn('CR_recommendations', CR_json_briefing)
        
        self.assertEqual(CR_json_briefing['CR_metadata']['CR_total_findings'], 2)
    
    def test_generate_recommendations(self):
        """Test generating CR_ recommendations"""
        CR_summary = generate_CR_analysis_summary(self.CR_findings)
        CR_recommendations = generate_CR_recommendations(CR_summary)
        
        self.assertIsInstance(CR_recommendations, list)
        self.assertGreater(len(CR_recommendations), 0)
        
        # Should recommend arbitrage execution
        CR_has_arbitrage_rec = any('arbitrage' in CR_rec.lower() for CR_rec in CR_recommendations)
        self.assertTrue(CR_has_arbitrage_rec)
    
    def test_briefing_with_empty_findings(self):
        """Test briefing generation with no findings"""
        CR_briefing = generate_CR_briefing([])
        
        self.assertIsInstance(CR_briefing, str)
        self.assertIn('0', CR_briefing)  # Zero findings


class TestChatModule(unittest.TestCase):
    """Test chat module with CR_ prefix"""
    
    def setUp(self):
        """Set up test fixtures"""
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")
        CR_event = create_CR_event("game_1", "Lakers vs Warriors", "NBA", [CR_market])
        self.CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        self.CR_chat = CR_OddsChat(self.CR_snapshot)
    
    def test_create_chat_session(self):
        """Test creating CR_ chat session"""
        self.assertIsNotNone(self.CR_chat)
        self.assertIsNotNone(self.CR_chat.CR_snapshot)
        self.assertIsNotNone(self.CR_chat.CR_tools)
    
    def test_start_chat_session_function(self):
        """Test start_CR_chat_session function"""
        CR_chat = start_CR_chat_session(self.CR_snapshot)
        
        self.assertIsInstance(CR_chat, CR_OddsChat)
        self.assertEqual(CR_chat.CR_snapshot, self.CR_snapshot)
    
    def test_answer_summary_question(self):
        """Test answering summary question"""
        CR_response = self.CR_chat.answer_CR_question("Give me a summary")
        
        self.assertIsInstance(CR_response, dict)
        self.assertIn('CR_answer', CR_response)
        self.assertIn('CR_sources', CR_response)
        self.assertIn('CR_confidence', CR_response)
        
        self.assertIn('Events', CR_response['CR_answer'])
    
    def test_answer_arbitrage_question(self):
        """Test answering arbitrage question"""
        CR_response = self.CR_chat.answer_CR_question("Are there any arbitrage opportunities?")
        
        self.assertIsInstance(CR_response, dict)
        self.assertIn('CR_answer', CR_response)
        self.assertIn('arbitrage', CR_response['CR_answer'].lower())
    
    def test_answer_value_question(self):
        """Test answering value edge question"""
        CR_response = self.CR_chat.answer_CR_question("Show me value edges")
        
        self.assertIsInstance(CR_response, dict)
        self.assertIn('CR_answer', CR_response)
        self.assertIn('value', CR_response['CR_answer'].lower())
    
    def test_answer_general_question(self):
        """Test answering general question"""
        CR_response = self.CR_chat.answer_CR_question("What can you do?")
        
        self.assertIsInstance(CR_response, dict)
        self.assertIn('CR_answer', CR_response)
        self.assertIn('CR_', CR_response['CR_answer'])
    
    def test_chat_with_findings(self):
        """Test chat with previous findings"""
        CR_finding = create_CR_finding(
            CR_type='arbitrage',
            CR_description='Test',
            CR_confidence=0.9,
            CR_event_id='game_1',
            CR_market_name='moneyline',
            CR_bookmakers=['DraftKings'],
            CR_details={}
        )
        
        CR_chat = CR_OddsChat(self.CR_snapshot, [CR_finding])
        CR_response = CR_chat.answer_CR_question("summary")
        
        self.assertIn('findings', CR_response['CR_answer'].lower())


class TestObservabilityModule(unittest.TestCase):
    """Test observability/trace module with CR_ prefix"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.CR_temp_dir = tempfile.mkdtemp()
        self.CR_tracer = CR_Tracer(CR_log_dir=self.CR_temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.CR_temp_dir):
            shutil.rmtree(self.CR_temp_dir)
    
    def test_create_trace_session(self):
        """Test creating CR_ trace session"""
        CR_session = create_CR_trace_session(
            CR_session_id="test_session",
            CR_start_time=datetime.now()
        )
        
        self.assertIsInstance(CR_session, dict)
        self.assertIn('CR_session_id', CR_session)
        self.assertIn('CR_start_time', CR_session)
        self.assertIn('CR_steps', CR_session)
        self.assertIn('CR_tool_calls', CR_session)
        self.assertIn('CR_errors', CR_session)
    
    def test_start_and_end_session(self):
        """Test starting and ending CR_ trace session"""
        CR_session_id = self.CR_tracer.start_CR_session("test_session")
        
        self.assertEqual(CR_session_id, "test_session")
        self.assertIsNotNone(self.CR_tracer.CR_current_session)
        
        CR_summary = self.CR_tracer.end_CR_session()
        
        self.assertIsInstance(CR_summary, dict)
        self.assertIn('CR_session_id', CR_summary)
        self.assertIn('CR_duration_seconds', CR_summary)
        self.assertIsNone(self.CR_tracer.CR_current_session)
    
    def test_log_step(self):
        """Test logging CR_ step"""
        self.CR_tracer.start_CR_session()
        self.CR_tracer.log_CR_step("test_step", "Test step description")
        
        CR_steps = self.CR_tracer.CR_current_session['CR_steps']
        self.assertEqual(len(CR_steps), 2)  # session_start + test_step
        
        CR_test_step = CR_steps[1]
        self.assertEqual(CR_test_step['CR_name'], "test_step")
        self.assertEqual(CR_test_step['CR_description'], "Test step description")
    
    def test_log_tool_call(self):
        """Test logging CR_ tool call"""
        self.CR_tracer.start_CR_session()
        self.CR_tracer.log_CR_tool_call(
            CR_tool_name="CR_test_tool",
            CR_inputs={'CR_param': 'value'},
            CR_outputs={'CR_result': 'success'},
            CR_duration_ms=100,
            CR_status="success"
        )
        
        CR_tool_calls = self.CR_tracer.CR_current_session['CR_tool_calls']
        self.assertEqual(len(CR_tool_calls), 1)
        
        CR_call = CR_tool_calls[0]
        self.assertEqual(CR_call['CR_tool_name'], "CR_test_tool")
        self.assertEqual(CR_call['CR_duration_ms'], 100)
        self.assertEqual(CR_call['CR_status'], "success")
    
    def test_log_error(self):
        """Test logging CR_ error"""
        self.CR_tracer.start_CR_session()
        
        try:
            raise ValueError("Test error")
        except ValueError as CR_error:
            self.CR_tracer.log_CR_error(CR_error, {'CR_context': 'test'})
        
        CR_errors = self.CR_tracer.CR_current_session['CR_errors']
        self.assertEqual(len(CR_errors), 1)
        
        CR_error_data = CR_errors[0]
        self.assertEqual(CR_error_data['CR_error_type'], 'ValueError')
        self.assertIn('Test error', CR_error_data['CR_error_message'])
    
    def test_get_global_tracer(self):
        """Test getting global CR_ tracer"""
        CR_tracer1 = get_CR_tracer()
        CR_tracer2 = get_CR_tracer()
        
        self.assertIsInstance(CR_tracer1, CR_Tracer)
        self.assertIs(CR_tracer1, CR_tracer2)  # Should be same instance
    
    def test_trace_decorator_success(self):
        """Test CR_ trace decorator with successful function"""
        CR_tracer = get_CR_tracer()
        CR_tracer.start_CR_session()
        
        @trace_CR_tool_call("CR_test_function")
        def CR_test_func(CR_x, CR_y):
            return CR_x + CR_y
        
        CR_result = CR_test_func(2, 3)
        
        self.assertEqual(CR_result, 5)
        
        CR_tool_calls = CR_tracer.CR_current_session['CR_tool_calls']
        self.assertGreater(len(CR_tool_calls), 0)
    
    def test_trace_decorator_error(self):
        """Test CR_ trace decorator with error"""
        CR_tracer = get_CR_tracer()
        CR_tracer.start_CR_session()
        
        @trace_CR_tool_call("CR_error_function")
        def CR_error_func():
            raise RuntimeError("Test error")
        
        with self.assertRaises(RuntimeError):
            CR_error_func()
        
        CR_errors = CR_tracer.CR_current_session['CR_errors']
        self.assertGreater(len(CR_errors), 0)
    
    def test_session_summary_generation(self):
        """Test CR_ session summary generation"""
        self.CR_tracer.start_CR_session()
        self.CR_tracer.log_CR_step("step1", "Step 1")
        self.CR_tracer.log_CR_step("step2", "Step 2")
        self.CR_tracer.log_CR_tool_call("tool1", {}, {}, 50, "success")
        self.CR_tracer.log_CR_tool_call("tool1", {}, {}, 75, "success")
        
        CR_summary = self.CR_tracer.end_CR_session()
        
        self.assertIn('CR_total_steps', CR_summary)
        self.assertIn('CR_total_tool_calls', CR_summary)
        self.assertIn('CR_average_tool_durations_ms', CR_summary)
        
        self.assertEqual(CR_summary['CR_total_tool_calls'], 2)
        self.assertIn('tool1', CR_summary['CR_average_tool_durations_ms'])


class TestIntegration(unittest.TestCase):
    """Integration tests for Phase 4 modules"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow with all Phase 4 modules"""
        # 1. Create test data
        CR_outcome1 = create_CR_outcome("Lakers", -110)
        CR_outcome2 = create_CR_outcome("Warriors", -110)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "DraftKings")
        CR_event = create_CR_event("game_1", "Lakers vs Warriors", "NBA", [CR_market])
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        # 2. Start tracing
        CR_tracer = CR_Tracer(CR_log_dir=tempfile.mkdtemp())
        CR_tracer.start_CR_session()
        
        # 3. Run analysis
        CR_findings = run_CR_agent(CR_snapshot)
        
        # 4. Generate briefing
        CR_briefing = generate_CR_briefing(CR_findings, CR_snapshot)
        
        # 5. Start chat session
        CR_chat = start_CR_chat_session(CR_snapshot, CR_findings)
        CR_response = CR_chat.answer_CR_question("summary")
        
        # 6. End tracing
        CR_summary = CR_tracer.end_CR_session()
        
        # Verify all components worked
        self.assertIsInstance(CR_findings, list)
        self.assertIsInstance(CR_briefing, str)
        self.assertIsInstance(CR_response, dict)
        self.assertIsInstance(CR_summary, dict)
        
        self.assertIn('CR_', CR_briefing)
        self.assertIn('CR_answer', CR_response)
        self.assertIn('CR_session_id', CR_summary)
    
    def test_prompts_with_snapshot(self):
        """Test prompts module with real snapshot data"""
        CR_outcome1 = create_CR_outcome("Lakers", 150)
        CR_outcome2 = create_CR_outcome("Warriors", -170)
        CR_market = create_CR_market("moneyline", [CR_outcome1, CR_outcome2], "FanDuel")
        CR_event = create_CR_event("game_2", "Lakers vs Warriors", "NBA", [CR_market])
        CR_snapshot = create_CR_snapshot([CR_event], datetime.now().isoformat(), "test")
        
        CR_prompt = format_CR_user_prompt(CR_snapshot)
        
        self.assertIn('1', CR_prompt)  # 1 event
        self.assertIn('FanDuel', CR_prompt)


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

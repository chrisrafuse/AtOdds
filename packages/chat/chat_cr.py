"""
Grounded Q&A with CR_ prefix compliance - answer follow-up questions based on briefing
NO hallucination
"""

from typing import Dict, Any, List, Optional

from packages.tools.registry import CR_TOOL_REGISTRY


class CR_OddsChat:
    """
    Chat interface for answering questions about odds analysis with CR_ prefix
    Grounded in data and tools only
    """

    def __init__(self, CR_snapshot: Dict[str, Any], CR_findings: List[Dict[str, Any]] = None):
        """
        Initialize chat with CR_ context

        Args:
            CR_snapshot: CR_ data snapshot dictionary for context
            CR_findings: Previous CR_ analysis findings
        """
        self.CR_snapshot = CR_snapshot
        self.CR_findings = CR_findings or []
        self.CR_tools = CR_TOOL_REGISTRY

    def answer_CR_question(self, CR_question: str) -> Dict[str, Any]:
        """
        Answer a question using available CR_ tools and data

        Args:
            CR_question: User question

        Returns:
            Grounded answer with CR_ sources
        """
        CR_question_lower = CR_question.lower()

        # Handle different types of questions
        if 'arbitrage' in CR_question_lower:
            return self._handle_CR_arbitrage_question(CR_question)
        elif 'value' in CR_question_lower or 'edge' in CR_question_lower:
            return self._handle_CR_value_question(CR_question)
        elif 'stale' in CR_question_lower:
            return self._handle_CR_stale_question(CR_question)
        elif 'outlier' in CR_question_lower:
            return self._handle_CR_outlier_question(CR_question)
        elif 'best' in CR_question_lower and 'line' in CR_question_lower:
            return self._handle_CR_best_lines_question(CR_question)
        elif 'consensus' in CR_question_lower:
            return self._handle_CR_consensus_question(CR_question)
        elif 'vig' in CR_question_lower or 'juice' in CR_question_lower:
            return self._handle_CR_vig_question(CR_question)
        elif 'probability' in CR_question_lower:
            return self._handle_CR_probability_question(CR_question)
        elif 'summary' in CR_question_lower or 'overview' in CR_question_lower:
            return self._handle_CR_summary_question(CR_question)
        else:
            return self._handle_CR_general_question(CR_question)

    def _handle_CR_arbitrage_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle arbitrage-related questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_detect_arbitrage'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_findings = CR_result.get('CR_result', [])

                CR_answer = f"Found {len(CR_findings)} arbitrage opportunities."

                if CR_findings:
                    CR_answer += "\n\nTop opportunities:"
                    for CR_i, CR_finding in enumerate(CR_findings[:3], 1):
                        CR_profit_margin = CR_finding.get('CR_details', {}).get('CR_profit_margin', 0)
                        CR_desc = CR_finding.get('CR_description', '')[:100]
                        CR_confidence = CR_finding.get('CR_confidence', 0)
                        CR_answer += f"\n{CR_i}. {CR_desc}..."
                        CR_answer += f"\n   Profit margin: {CR_profit_margin:.2%}"
                        CR_answer += f"\n   Confidence: {CR_confidence:.1%}"

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_arbitrage_detection'],
                    'CR_data_count': len(CR_findings),
                    'CR_confidence': 'high' if CR_findings else 'medium'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error detecting arbitrage: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing arbitrage question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_value_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle value edge questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_detect_value_edges'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_findings = CR_result.get('CR_result', [])

                CR_answer = f"Found {len(CR_findings)} value edges."

                if CR_findings:
                    # Group by edge size
                    CR_large_edges = [CR_f for CR_f in CR_findings if CR_f.get('CR_details', {}).get('CR_edge', 0) > 0.1]
                    CR_medium_edges = [CR_f for CR_f in CR_findings if 0.05 < CR_f.get('CR_details', {}).get('CR_edge', 0) <= 0.1]
                    CR_small_edges = [CR_f for CR_f in CR_findings if CR_f.get('CR_details', {}).get('CR_edge', 0) <= 0.05]

                    CR_answer += f"\n\nBy edge size:"
                    CR_answer += f"\n• Large (>10%): {len(CR_large_edges)}"
                    CR_answer += f"\n• Medium (5-10%): {len(CR_medium_edges)}"
                    CR_answer += f"\n• Small (<5%): {len(CR_small_edges)}"

                    if CR_large_edges:
                        CR_answer += "\n\nLargest edges:"
                        for CR_finding in CR_large_edges[:3]:
                            CR_edge = CR_finding.get('CR_details', {}).get('CR_edge', 0)
                            CR_desc = CR_finding.get('CR_description', '')[:80]
                            CR_answer += f"\n• {CR_desc}... ({CR_edge:.1%})"

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_value_edge_detection'],
                    'CR_data_count': len(CR_findings),
                    'CR_confidence': 'high'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error detecting value edges: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing value question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_stale_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle stale line questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_detect_stale_lines'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_findings = CR_result.get('CR_result', [])

                CR_answer = f"Found {len(CR_findings)} stale lines."

                if CR_findings:
                    # Group by hours stale
                    CR_very_stale = [CR_f for CR_f in CR_findings if CR_f.get('CR_details', {}).get('CR_hours_stale', 0) > 48]
                    CR_moderately_stale = [CR_f for CR_f in CR_findings if 24 < CR_f.get('CR_details', {}).get('CR_hours_stale', 0) <= 48]

                    CR_answer += f"\n\nBy freshness:"
                    CR_answer += f"\n• Very stale (>48h): {len(CR_very_stale)}"
                    CR_answer += f"\n• Moderately stale (24-48h): {len(CR_moderately_stale)}"

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_stale_line_detection'],
                    'CR_data_count': len(CR_findings),
                    'CR_confidence': 'high'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error detecting stale lines: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing stale line question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_outlier_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle outlier questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_detect_outliers'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_findings = CR_result.get('CR_result', [])

                CR_answer = f"Found {len(CR_findings)} outlier odds."

                if CR_findings:
                    # Group by z-score
                    CR_high_outliers = [CR_f for CR_f in CR_findings if CR_f.get('CR_details', {}).get('CR_z_score', 0) > 3]
                    CR_medium_outliers = [CR_f for CR_f in CR_findings if 2 < CR_f.get('CR_details', {}).get('CR_z_score', 0) <= 3]

                    CR_answer += f"\n\nBy deviation:"
                    CR_answer += f"\n• High (>3σ): {len(CR_high_outliers)}"
                    CR_answer += f"\n• Medium (2-3σ): {len(CR_medium_outliers)}"

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_outlier_detection'],
                    'CR_data_count': len(CR_findings),
                    'CR_confidence': 'high'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error detecting outliers: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing outlier question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_best_lines_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle best lines questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_compute_best_lines'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_best_lines = CR_result.get('CR_result', {})

                CR_answer = f"Computed best lines across all bookmakers."

                # Show some examples
                CR_event_count = 0
                for CR_event_id, CR_event_lines in CR_best_lines.items():
                    if CR_event_count >= 2:  # Limit to 2 events
                        break

                    CR_answer += f"\n\nEvent {CR_event_id}:"
                    for CR_market_name, CR_market_lines in CR_event_lines.items():
                        CR_answer += f"\n  {CR_market_name}:"
                        for CR_outcome, (CR_bookmaker, CR_price) in CR_market_lines.items():
                            CR_answer += f"\n    {CR_outcome}: {CR_bookmaker} @ {CR_price}"

                    CR_event_count += 1

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_best_lines_computation'],
                    'CR_confidence': 'high'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error computing best lines: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing best lines question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_consensus_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle consensus questions with CR_ prefix"""
        try:
            CR_result = self.CR_tools['CR_compute_consensus'](self.CR_snapshot)

            if CR_result.get('CR_success'):
                CR_consensus = CR_result.get('CR_result', {})

                CR_answer = f"Computed consensus prices across bookmakers."

                # Show examples
                CR_event_count = 0
                for CR_event_id, CR_event_consensus in CR_consensus.items():
                    if CR_event_count >= 2:  # Limit to 2 events
                        break

                    CR_answer += f"\n\nEvent {CR_event_id}:"
                    for CR_market_name, CR_market_consensus in CR_event_consensus.items():
                        CR_answer += f"\n  {CR_market_name}:"
                        for CR_outcome, CR_price in CR_market_consensus.items():
                            CR_answer += f"\n    {CR_outcome}: {CR_price:.3f}"

                    CR_event_count += 1

                return {
                    'CR_answer': CR_answer,
                    'CR_sources': ['CR_consensus_computation'],
                    'CR_confidence': 'high'
                }
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                return {
                    'CR_answer': f"Error computing consensus: {CR_error}",
                    'CR_sources': [],
                    'CR_confidence': 'low'
                }
        except Exception as CR_exception:
            return {
                'CR_answer': f"Error processing consensus question: {CR_exception}",
                'CR_sources': [],
                'CR_confidence': 'low'
            }

    def _handle_CR_vig_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle vigorish questions with CR_ prefix"""
        from packages.core_engine.odds_math import compute_CR_vig

        CR_answer = "Vigorish (vig) analysis:\n\n"

        # Calculate average vig across markets
        CR_total_vig = 0
        CR_market_count = 0

        CR_events = self.CR_snapshot.get('CR_events', [])
        for CR_event in CR_events:
            CR_markets = CR_event.get('CR_markets', [])
            for CR_market in CR_markets:
                CR_outcomes = CR_market.get('CR_outcomes', [])
                CR_prices = [CR_outcome.get('CR_price', 0) for CR_outcome in CR_outcomes]
                if len(CR_prices) >= 2:  # Need at least 2 outcomes
                    try:
                        CR_vig = compute_CR_vig(CR_prices)
                        CR_total_vig += CR_vig
                        CR_market_count += 1
                    except:
                        pass

        if CR_market_count > 0:
            CR_avg_vig = CR_total_vig / CR_market_count
            CR_answer += f"Average vig across {CR_market_count} markets: {CR_avg_vig:.2%}\n\n"

            if CR_avg_vig > 0.05:
                CR_answer += "This is relatively high vig - look for value opportunities."
            elif CR_avg_vig > 0.03:
                CR_answer += "This is typical vig range."
            else:
                CR_answer += "This is low vig - good for bettors."
        else:
            CR_answer += "Could not calculate vig - insufficient data."

        return {
            'CR_answer': CR_answer,
            'CR_sources': ['CR_vig_calculation'],
            'CR_confidence': 'medium'
        }

    def _handle_CR_probability_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle probability questions with CR_ prefix"""
        from packages.core_engine.odds_math import compute_CR_implied_probability

        CR_answer = "Implied probability analysis:\n\n"

        # Show some examples
        CR_example_count = 0
        CR_events = self.CR_snapshot.get('CR_events', [])
        for CR_event in CR_events:
            if CR_example_count >= 3:  # Limit examples
                break

            CR_event_id = CR_event.get('CR_event_id', 'N/A')
            CR_answer += f"Event {CR_event_id}:\n"
            CR_markets = CR_event.get('CR_markets', [])
            for CR_market in CR_markets[:1]:  # One market per event
                CR_market_name = CR_market.get('CR_name', 'N/A')
                CR_answer += f"  {CR_market_name}:\n"
                CR_outcomes = CR_market.get('CR_outcomes', [])
                for CR_outcome in CR_outcomes:
                    try:
                        CR_outcome_name = CR_outcome.get('CR_name', 'N/A')
                        CR_price = CR_outcome.get('CR_price', 0)
                        CR_prob = compute_CR_implied_probability(CR_price)
                        CR_answer += f"    {CR_outcome_name}: {CR_price} → {CR_prob:.1%}\n"
                    except:
                        pass

            CR_example_count += 1

        return {
            'CR_answer': CR_answer,
            'CR_sources': ['CR_probability_calculation'],
            'CR_confidence': 'high'
        }

    def _handle_CR_summary_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle summary questions with CR_ prefix"""
        CR_events = self.CR_snapshot.get('CR_events', [])
        CR_total_events = len(CR_events)

        CR_total_markets = 0
        CR_total_outcomes = 0
        CR_bookmakers = set()

        for CR_event in CR_events:
            CR_markets = CR_event.get('CR_markets', [])
            CR_total_markets += len(CR_markets)

            for CR_market in CR_markets:
                CR_outcomes = CR_market.get('CR_outcomes', [])
                CR_total_outcomes += len(CR_outcomes)
                CR_bookmaker = CR_market.get('CR_bookmaker', '')
                if CR_bookmaker:
                    CR_bookmakers.add(CR_bookmaker)

        CR_answer = f"Dataset Summary:\n\n"
        CR_answer += f"• Events: {CR_total_events}\n"
        CR_answer += f"• Markets: {CR_total_markets}\n"
        CR_answer += f"• Outcomes: {CR_total_outcomes}\n"
        CR_answer += f"• Bookmakers: {len(CR_bookmakers)}\n"
        CR_answer += f"• Bookmaker list: {', '.join(sorted(CR_bookmakers))}\n\n"

        if self.CR_findings:
            CR_answer += f"Previous Analysis Results:\n"
            CR_answer += f"• Total findings: {len(self.CR_findings)}\n"

            # Count by type
            CR_by_type = {}
            for CR_finding in self.CR_findings:
                CR_type = CR_finding.get('CR_type', 'unknown')
                CR_by_type[CR_type] = CR_by_type.get(CR_type, 0) + 1

            for CR_finding_type, CR_count in CR_by_type.items():
                CR_answer += f"• {CR_finding_type}: {CR_count}\n"

        return {
            'CR_answer': CR_answer,
            'CR_sources': ['CR_dataset_summary'],
            'CR_confidence': 'high'
        }

    def _handle_CR_general_question(self, CR_question: str) -> Dict[str, Any]:
        """Handle general questions with CR_ prefix"""
        CR_answer = ("I can help you analyze CR_ odds data. I can answer questions about:\n\n"
                 "• CR_arbitrage opportunities\n"
                 "• CR_value_edges\n"
                 "• CR_stale_lines\n"
                 "• CR_outlier odds\n"
                 "• CR_best_lines across bookmakers\n"
                 "• CR_consensus prices\n"
                 "• CR_vigorish calculations\n"
                 "• CR_implied probabilities\n"
                 "• CR_dataset summary\n\n"
                 "Please ask a specific question about any of these topics.")

        return {
            'CR_answer': CR_answer,
            'CR_sources': ['CR_help'],
            'CR_confidence': 'medium'
        }


class CR_LLMOddsChat:
    """
    LLM-powered chat that answers follow-up questions grounded in
    the briefing and findings. Falls back to CR_OddsChat if no provider.
    """

    def __init__(
        self,
        CR_snapshot: Dict[str, Any],
        CR_findings: List[Dict[str, Any]] = None,
        CR_briefing_text: str = "",
        CR_provider_name: Optional[str] = None
    ):
        self.CR_snapshot = CR_snapshot
        self.CR_findings = CR_findings or []
        self.CR_briefing_text = CR_briefing_text
        self.CR_history: List[Dict[str, Any]] = []

        from packages.llm.factory import get_CR_llm_provider
        from packages.agent.prompts import get_CR_chat_system_prompt, build_CR_chat_context_message

        self._provider = get_CR_llm_provider(CR_provider_name)
        self._system_prompt = get_CR_chat_system_prompt()
        self._context_message = build_CR_chat_context_message(CR_briefing_text, self.CR_findings)
        self._tools = CR_TOOL_REGISTRY

    def answer_CR_question(self, CR_question: str) -> Dict[str, Any]:
        """Answer a question using the LLM grounded in briefing context."""
        from packages.llm.tool_schemas import CR_TOOL_SCHEMAS
        from packages.agent.agent import _CR_tool_executor

        # Build message list: system + context + history + new question
        CR_messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": self._context_message},
            {"role": "assistant", "content": "I have reviewed the briefing and findings. I'm ready to answer your questions."},
        ]
        CR_messages.extend(self.CR_history)
        CR_messages.append({"role": "user", "content": CR_question})

        try:
            CR_response = self._provider.chat_with_tools(
                CR_messages=CR_messages,
                CR_tools=CR_TOOL_SCHEMAS,
                CR_tool_executor=_CR_tool_executor,
                CR_max_iterations=4
            )

            CR_answer = CR_response.CR_content
            CR_tool_trace = [CR_tc.to_dict() for CR_tc in CR_response.CR_tool_calls]

            # Append to history for multi-turn
            self.CR_history.append({"role": "user", "content": CR_question})
            self.CR_history.append({"role": "assistant", "content": CR_answer})

            return {
                'CR_answer': CR_answer,
                'CR_sources': [CR_tc['CR_tool_name'] for CR_tc in CR_tool_trace],
                'CR_tool_trace': CR_tool_trace,
                'CR_confidence': 'high' if CR_tool_trace else 'medium',
                'CR_provider': CR_response.CR_provider,
            }
        except Exception as CR_e:
            # Degrade gracefully to keyword-based fallback
            CR_fallback = CR_OddsChat(self.CR_snapshot, self.CR_findings)
            CR_result = CR_fallback.answer_CR_question(CR_question)
            CR_result['CR_tool_trace'] = []
            CR_result['CR_provider'] = 'fallback'
            CR_result['CR_error'] = str(CR_e)
            return CR_result


def start_CR_chat_session(
    CR_snapshot: Dict[str, Any],
    CR_findings: List[Dict[str, Any]] = None,
    CR_briefing_text: str = "",
    CR_provider_name: Optional[str] = None
):
    """
    Start a new CR_ chat session.
    Returns CR_LLMOddsChat when a provider is configured; CR_OddsChat otherwise.
    """
    from packages.llm.factory import get_CR_provider_name
    CR_active = CR_provider_name or get_CR_provider_name()
    if CR_active != "mock":
        return CR_LLMOddsChat(CR_snapshot, CR_findings, CR_briefing_text, CR_active)
    return CR_OddsChat(CR_snapshot, CR_findings)

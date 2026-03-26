"""
Grounded Q&A - answer follow-up questions based on briefing
NO hallucination
"""

from typing import Dict, Any, List, Optional
import json

from tools.registry import TOOL_REGISTRY
from data.contracts import CR_snapshot


class OddsChat:
    """
    Chat interface for answering questions about odds analysis
    Grounded in data and tools only
    """
    
    def __init__(self, snapshot: CR_snapshot, findings: List = None):
        """
        Initialize chat with context
        
        Args:
            snapshot: Data snapshot for context
            findings: Previous analysis findings
        """
        self.snapshot = snapshot
        self.findings = findings or []
        self.tools = TOOL_REGISTRY
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using available tools and data
        
        Args:
            question: User question
            
        Returns:
            Grounded answer with sources
        """
        question_lower = question.lower()
        
        # Handle different types of questions
        if 'arbitrage' in question_lower:
            return self._handle_arbitrage_question(question)
        elif 'value' in question_lower or 'edge' in question_lower:
            return self._handle_value_question(question)
        elif 'stale' in question_lower:
            return self._handle_stale_question(question)
        elif 'outlier' in question_lower:
            return self._handle_outlier_question(question)
        elif 'best' in question_lower and 'line' in question_lower:
            return self._handle_best_lines_question(question)
        elif 'consensus' in question_lower:
            return self._handle_consensus_question(question)
        elif 'vig' in question_lower or 'juice' in question_lower:
            return self._handle_vig_question(question)
        elif 'probability' in question_lower:
            return self._handle_probability_question(question)
        elif 'summary' in question_lower or 'overview' in question_lower:
            return self._handle_summary_question(question)
        else:
            return self._handle_general_question(question)
    
    def _handle_arbitrage_question(self, question: str) -> Dict[str, Any]:
        """Handle arbitrage-related questions"""
        try:
            result = self.tools['detect_arbitrage'](self.snapshot)
            
            if result['success']:
                findings = result['result']
                
                answer = f"Found {len(findings)} arbitrage opportunities."
                
                if findings:
                    answer += "\n\nTop opportunities:"
                    for i, finding in enumerate(findings[:3], 1):
                        profit_margin = finding.details.get('profit_margin', 0)
                        answer += f"\n{i}. {finding.description[:100]}..."
                        answer += f"\n   Profit margin: {profit_margin:.2%}"
                        answer += f"\n   Confidence: {finding.confidence:.1%}"
                
                return {
                    'answer': answer,
                    'sources': ['arbitrage_detection'],
                    'data_count': len(findings),
                    'confidence': 'high' if findings else 'medium'
                }
            else:
                return {
                    'answer': f"Error detecting arbitrage: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing arbitrage question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_value_question(self, question: str) -> Dict[str, Any]:
        """Handle value edge questions"""
        try:
            result = self.tools['detect_value_edges'](self.snapshot)
            
            if result['success']:
                findings = result['result']
                
                answer = f"Found {len(findings)} value edges."
                
                if findings:
                    # Group by edge size
                    large_edges = [f for f in findings if f.details.get('edge', 0) > 0.1]
                    medium_edges = [f for f in findings if 0.05 < f.details.get('edge', 0) <= 0.1]
                    small_edges = [f for f in findings if f.details.get('edge', 0) <= 0.05]
                    
                    answer += f"\n\nBy edge size:"
                    answer += f"\n• Large (>10%): {len(large_edges)}"
                    answer += f"\n• Medium (5-10%): {len(medium_edges)}"
                    answer += f"\n• Small (<5%): {len(small_edges)}"
                    
                    if large_edges:
                        answer += "\n\nLargest edges:"
                        for finding in large_edges[:3]:
                            edge = finding.details.get('edge', 0)
                            answer += f"\n• {finding.description[:80]}... ({edge:.1%})"
                
                return {
                    'answer': answer,
                    'sources': ['value_edge_detection'],
                    'data_count': len(findings),
                    'confidence': 'high'
                }
            else:
                return {
                    'answer': f"Error detecting value edges: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing value question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_stale_question(self, question: str) -> Dict[str, Any]:
        """Handle stale line questions"""
        try:
            result = self.tools['detect_stale_lines'](self.snapshot)
            
            if result['success']:
                findings = result['result']
                
                answer = f"Found {len(findings)} stale lines."
                
                if findings:
                    # Group by hours stale
                    very_stale = [f for f in findings if f.details.get('hours_stale', 0) > 48]
                    moderately_stale = [f for f in findings if 24 < f.details.get('hours_stale', 0) <= 48]
                    
                    answer += f"\n\nBy freshness:"
                    answer += f"\n• Very stale (>48h): {len(very_stale)}"
                    answer += f"\n• Moderately stale (24-48h): {len(moderately_stale)}"
                
                return {
                    'answer': answer,
                    'sources': ['stale_line_detection'],
                    'data_count': len(findings),
                    'confidence': 'high'
                }
            else:
                return {
                    'answer': f"Error detecting stale lines: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing stale line question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_outlier_question(self, question: str) -> Dict[str, Any]:
        """Handle outlier questions"""
        try:
            result = self.tools['detect_outliers'](self.snapshot)
            
            if result['success']:
                findings = result['result']
                
                answer = f"Found {len(findings)} outlier odds."
                
                if findings:
                    # Group by z-score
                    high_outliers = [f for f in findings if f.details.get('z_score', 0) > 3]
                    medium_outliers = [f for f in findings if 2 < f.details.get('z_score', 0) <= 3]
                    
                    answer += f"\n\nBy deviation:"
                    answer += f"\n• High (>3σ): {len(high_outliers)}"
                    answer += f"\n• Medium (2-3σ): {len(medium_outliers)}"
                
                return {
                    'answer': answer,
                    'sources': ['outlier_detection'],
                    'data_count': len(findings),
                    'confidence': 'high'
                }
            else:
                return {
                    'answer': f"Error detecting outliers: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing outlier question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_best_lines_question(self, question: str) -> Dict[str, Any]:
        """Handle best lines questions"""
        try:
            result = self.tools['compute_best_lines'](self.snapshot)
            
            if result['success']:
                best_lines = result['result']
                
                answer = f"Computed best lines across all bookmakers."
                
                # Show some examples
                event_count = 0
                for event_id, event_lines in best_lines.items():
                    if event_count >= 2:  # Limit to 2 events
                        break
                    
                    answer += f"\n\nEvent {event_id}:"
                    for market_name, market_lines in event_lines.items():
                        answer += f"\n  {market_name}:"
                        for outcome, (bookmaker, price) in market_lines.items():
                            answer += f"\n    {outcome}: {bookmaker} @ {price}"
                    
                    event_count += 1
                
                return {
                    'answer': answer,
                    'sources': ['best_lines_computation'],
                    'confidence': 'high'
                }
            else:
                return {
                    'answer': f"Error computing best lines: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing best lines question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_consensus_question(self, question: str) -> Dict[str, Any]:
        """Handle consensus questions"""
        try:
            result = self.tools['compute_consensus'](self.snapshot)
            
            if result['success']:
                consensus = result['result']
                
                answer = f"Computed consensus prices across bookmakers."
                
                # Show examples
                event_count = 0
                for event_id, event_consensus in consensus.items():
                    if event_count >= 2:  # Limit to 2 events
                        break
                    
                    answer += f"\n\nEvent {event_id}:"
                    for market_name, market_consensus in event_consensus.items():
                        answer += f"\n  {market_name}:"
                        for outcome, price in market_consensus.items():
                            answer += f"\n    {outcome}: {price:.3f}"
                    
                    event_count += 1
                
                return {
                    'answer': answer,
                    'sources': ['consensus_computation'],
                    'confidence': 'high'
                }
            else:
                return {
                    'answer': f"Error computing consensus: {result['error']}",
                    'sources': [],
                    'confidence': 'low'
                }
        except Exception as e:
            return {
                'answer': f"Error processing consensus question: {e}",
                'sources': [],
                'confidence': 'low'
            }
    
    def _handle_vig_question(self, question: str) -> Dict[str, Any]:
        """Handle vigorish questions"""
        answer = "Vigorish (vig) analysis:\n\n"
        
        # Calculate average vig across markets
        total_vig = 0
        market_count = 0
        
        for event in self.snapshot.events:
            for market in event.markets:
                prices = [outcome.price for outcome in market.outcomes]
                if len(prices) >= 2:  # Need at least 2 outcomes
                    try:
                        from core_engine.odds_math import compute_vig
                        vig = compute_vig(prices)
                        total_vig += vig
                        market_count += 1
                    except:
                        pass
        
        if market_count > 0:
            avg_vig = total_vig / market_count
            answer += f"Average vig across {market_count} markets: {avg_vig:.2%}\n\n"
            
            if avg_vig > 0.05:
                answer += "This is relatively high vig - look for value opportunities."
            elif avg_vig > 0.03:
                answer += "This is typical vig range."
            else:
                answer += "This is low vig - good for bettors."
        else:
            answer += "Could not calculate vig - insufficient data."
        
        return {
            'answer': answer,
            'sources': ['vig_calculation'],
            'confidence': 'medium'
        }
    
    def _handle_probability_question(self, question: str) -> Dict[str, Any]:
        """Handle probability questions"""
        answer = "Implied probability analysis:\n\n"
        
        # Show some examples
        example_count = 0
        for event in self.snapshot.events:
            if example_count >= 3:  # Limit examples
                break
            
            answer += f"Event {event.id}:\n"
            for market in event.markets[:1]:  # One market per event
                answer += f"  {market.name}:\n"
                for outcome in market.outcomes:
                    try:
                        from core_engine.odds_math import compute_implied_probability
                        prob = compute_implied_probability(outcome.price)
                        answer += f"    {outcome.name}: {outcome.price} → {prob:.1%}\n"
                    except:
                        pass
            
            example_count += 1
        
        return {
            'answer': answer,
            'sources': ['probability_calculation'],
            'confidence': 'high'
        }
    
    def _handle_summary_question(self, question: str) -> Dict[str, Any]:
        """Handle summary questions"""
        total_events = len(self.snapshot.events)
        total_markets = sum(len(event.markets) for event in self.snapshot.events)
        total_outcomes = sum(len(market.outcomes) for event in self.snapshot.events for market in event.markets)
        
        # Count unique bookmakers
        bookmakers = set()
        for event in self.snapshot.events:
            for market in event.markets:
                bookmakers.add(market.bookmaker)
        
        answer = f"Dataset Summary:\n\n"
        answer += f"• Events: {total_events}\n"
        answer += f"• Markets: {total_markets}\n"
        answer += f"• Outcomes: {total_outcomes}\n"
        answer += f"• Bookmakers: {len(bookmakers)}\n"
        answer += f"• Bookmaker list: {', '.join(sorted(bookmakers))}\n\n"
        
        if self.findings:
            answer += f"Previous Analysis Results:\n"
            answer += f"• Total findings: {len(self.findings)}\n"
            
            # Count by type
            by_type = {}
            for finding in self.findings:
                by_type[finding.type] = by_type.get(finding.type, 0) + 1
            
            for finding_type, count in by_type.items():
                answer += f"• {finding_type}: {count}\n"
        
        return {
            'answer': answer,
            'sources': ['dataset_summary'],
            'confidence': 'high'
        }
    
    def _handle_general_question(self, question: str) -> Dict[str, Any]:
        """Handle general questions"""
        answer = ("I can help you analyze odds data. I can answer questions about:\n\n"
                 "• Arbitrage opportunities\n"
                 "• Value edges\n"
                 "• Stale lines\n"
                 "• Outlier odds\n"
                 "• Best lines across bookmakers\n"
                 "• Consensus prices\n"
                 "• Vigorish calculations\n"
                 "• Implied probabilities\n"
                 "• Dataset summary\n\n"
                 "Please ask a specific question about any of these topics.")
        
        return {
            'answer': answer,
            'sources': ['help'],
            'confidence': 'medium'
        }


def start_chat_session(snapshot: CR_snapshot, findings: List = None) -> OddsChat:
    """
    Start a new chat session
    
    Args:
        snapshot: Data snapshot for context
        findings: Previous analysis findings
        
    Returns:
        Chat session instance
    """
    return OddsChat(snapshot, findings)

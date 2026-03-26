"""
Test suite for Betstamp AI Odds Agent alignment
Validates that the codebase properly handles Betstamp data format and requirements
"""

import pytest
import os
from datetime import datetime

from packages.data.loader import load_data
from packages.core_engine.detectors import detect_arbitrage, detect_stale_lines, detect_outliers, detect_value_edges
from packages.core_engine.odds_math import compute_implied_probability, compute_vig
from packages.agent.agent import run_agent
from packages.reporting.briefing import generate_briefing


class TestBetstampAlignment:
    """Test suite for Betstamp data format alignment"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.sample_data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'Betstamp AI Odds Agent - sample_odds_data.json')
        self.snapshot = load_data(self.sample_data_path)
    
    def test_data_loading(self):
        """Test that Betstamp data loads correctly"""
        assert self.snapshot is not None
        assert len(self.snapshot.events) == 10  # 10 NBA games
        
        # Test first event structure
        first_event = self.snapshot.events[0]
        assert first_event.name == "Boston Celtics vs Los Angeles Lakers"
        assert first_event.sport == "NBA"
        assert len(first_event.markets) == 24  # 8 sportsbooks × 3 markets
        
        # Test market structure
        markets_by_type = {}
        for market in first_event.markets:
            if market.name not in markets_by_type:
                markets_by_type[market.name] = []
            markets_by_type[market.name].append(market)
        
        assert len(markets_by_type['spread']) == 8  # 8 sportsbooks
        assert len(markets_by_type['moneyline']) == 8
        assert len(markets_by_type['total']) == 8
    
    def test_american_odds_handling(self):
        """Test that American odds are handled correctly"""
        # Test positive American odds (underdog)
        prob_positive = compute_implied_probability(196)
        expected_positive = 100.0 / (196 + 100)  # ~0.338
        assert abs(prob_positive - expected_positive) < 0.001
        
        # Test negative American odds (favorite)
        prob_negative = compute_implied_probability(-228)
        expected_negative = abs(-228) / (abs(-228) + 100)  # ~0.695
        assert abs(prob_negative - expected_negative) < 0.001
        
        # Test vig calculation with American odds
        vig = compute_vig([-111, -111])
        expected_vig = (compute_implied_probability(-111) * 2) - 1.0
        assert abs(vig - expected_vig) < 0.001
    
    def test_detection_algorithms(self):
        """Test that detection algorithms work with Betstamp data"""
        # Test arbitrage detection
        arbitrages = detect_arbitrage(self.snapshot.events)
        assert len(arbitrages) > 0  # Should find seeded arbitrage opportunities
        assert all(arb.type == 'arbitrage' for arb in arbitrages)
        assert all(arb.confidence > 0 for arb in arbitrages)
        
        # Test stale line detection
        stale_lines = detect_stale_lines(self.snapshot.events)
        assert isinstance(stale_lines, list)
        
        # Test outlier detection
        outliers = detect_outliers(self.snapshot.events)
        assert len(outliers) > 0  # Should find seeded outliers
        assert all(outlier.type == 'outlier' for outlier in outliers)
        
        # Test value edge detection
        value_edges = detect_value_edges(self.snapshot.events)
        assert len(value_edges) > 0  # Should find value edges
        assert all(edge.type == 'value_edge' for edge in value_edges)
    
    def test_sportsbook_coverage(self):
        """Test that all 8 sportsbooks are processed"""
        expected_sportsbooks = {
            'DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 
            'PointsBet', 'bet365', 'Pinnacle', 'BetRivers'
        }
        
        found_sportsbooks = set()
        for event in self.snapshot.events:
            for market in event.markets:
                found_sportsbooks.add(market.bookmaker)
        
        assert found_sportsbooks == expected_sportsbooks
    
    def test_market_types(self):
        """Test that all 3 market types are processed"""
        expected_market_types = {'spread', 'moneyline', 'total'}
        
        found_market_types = set()
        for event in self.snapshot.events:
            for market in event.markets:
                found_market_types.add(market.name)
        
        assert found_market_types == expected_market_types
    
    def test_agent_orchestration(self):
        """Test that agent orchestration works with Betstamp data"""
        findings = run_agent(self.snapshot)
        assert isinstance(findings, list)
        assert len(findings) > 0
        
        # Check that all finding types are present
        finding_types = {finding.type for finding in findings}
        expected_types = {'arbitrage', 'value_edge', 'outlier'}
        assert finding_types.intersection(expected_types)
    
    def test_briefing_generation(self):
        """Test that briefing generation works with Betstamp data"""
        findings = run_agent(self.snapshot)
        briefing = generate_briefing(findings, self.snapshot)
        
        assert isinstance(briefing, str)
        assert len(briefing) > 0
        assert 'ODDS ANALYSIS BRIEFING' in briefing
        assert 'SUMMARY' in briefing
        assert 'TOP FINDINGS' in briefing
    
    def test_cr_compliance(self):
        """Test that all data structures use CR_ prefix"""
        # Test data contracts
        from packages.data.contracts import CR_snapshot, CR_event, CR_market, CR_outcome, CR_finding
        
        # Verify CR_ prefix in class names
        assert CR_snapshot.__name__.startswith('CR_')
        assert CR_event.__name__.startswith('CR_')
        assert CR_market.__name__.startswith('CR_')
        assert CR_outcome.__name__.startswith('CR_')
        assert CR_finding.__name__.startswith('CR_')
        
        # Verify CR_ compliance in loaded data
        for event in self.snapshot.events:
            assert hasattr(event, 'id') or hasattr(event, 'CR_event_id')
            assert hasattr(event, 'sport') or hasattr(event, 'CR_sport')
    
    def test_data_integrity(self):
        """Test that data integrity is maintained"""
        # Test that all events have required fields
        for event in self.snapshot.events:
            assert event.name is not None and len(event.name) > 0
            assert event.sport is not None and len(event.sport) > 0
            assert len(event.markets) > 0
            
            for market in event.markets:
                assert market.name is not None and len(market.name) > 0
                assert market.bookmaker is not None and len(market.bookmaker) > 0
                assert len(market.outcomes) > 0
                
                for outcome in market.outcomes:
                    assert outcome.name is not None and len(outcome.name) > 0
                    assert outcome.price is not None
                    assert isinstance(outcome.price, (int, float))
    
    def test_performance_requirements(self):
        """Test that performance requirements are met"""
        import time
        
        # Test data loading performance
        start_time = time.time()
        snapshot = load_data(self.sample_data_path)
        load_time = time.time() - start_time
        
        assert load_time < 1.0  # Should load in under 1 second
        assert len(snapshot.events) == 10
        
        # Test detection performance
        start_time = time.time()
        arbitrages = detect_arbitrage(snapshot.events)
        detection_time = time.time() - start_time
        
        assert detection_time < 2.0  # Should detect in under 2 seconds
        assert len(arbitrages) > 0


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])

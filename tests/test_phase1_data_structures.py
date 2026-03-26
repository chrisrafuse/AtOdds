#!/usr/bin/env python3
"""
Test Suite for Phase 1: Data Structure Alignment
Tests for CR_ dictionary schemas, validation framework, and data loader
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from typing import Dict, Any

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.data.contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_finding,
    create_CR_snapshot,
    create_CR_briefing,
    create_CR_step,
    create_CR_tool_call,
    validate_CR_structure,
    get_schema_version,
    get_supported_structures
)

from packages.data.loader import (
    load_data,
    decimal_to_american_odds,
    calculate_implied_probability,
    normalize_sport_name,
    validate_data_quality,
    DataLoadError,
    DataQualityError
)

from packages.validation.structure_validator import (
    StructureValidator,
    ValidationError
)


class TestCROutcome(unittest.TestCase):
    """Test CR_outcome factory and validation"""
    
    def test_create_basic_outcome(self):
        """Test creating a basic outcome"""
        outcome = create_CR_outcome(
            CR_name="Lakers +5.5",
            CR_price=-110
        )
        
        self.assertEqual(outcome["CR_name"], "Lakers +5.5")
        self.assertEqual(outcome["CR_price"], -110)
        self.assertNotIn("CR_implied_probability", outcome)
    
    def test_create_outcome_with_probability(self):
        """Test creating outcome with implied probability"""
        outcome = create_CR_outcome(
            CR_name="Warriors -5.5",
            CR_price=+150,
            CR_implied_probability=0.4
        )
        
        self.assertEqual(outcome["CR_name"], "Warriors -5.5")
        self.assertEqual(outcome["CR_price"], 150)
        self.assertEqual(outcome["CR_implied_probability"], 0.4)
    
    def test_outcome_type_conversion(self):
        """Test type conversion in outcome creation"""
        outcome = create_CR_outcome(
            CR_name=123,  # Should convert to string
            CR_price=110.0  # Should stay as float
        )
        
        self.assertEqual(outcome["CR_name"], "123")
        self.assertEqual(outcome["CR_price"], 110.0)


class TestCRMarket(unittest.TestCase):
    """Test CR_market factory and validation"""
    
    def test_create_valid_market(self):
        """Test creating a valid market"""
        outcome1 = create_CR_outcome("Home +5.5", -110)
        outcome2 = create_CR_outcome("Away -5.5", -110)
        
        market = create_CR_market(
            CR_name="spread",
            CR_outcomes=[outcome1, outcome2],
            CR_bookmaker="DraftKings"
        )
        
        self.assertEqual(market["CR_name"], "spread")
        self.assertEqual(len(market["CR_outcomes"]), 2)
        self.assertEqual(market["CR_bookmaker"], "DraftKings")
    
    def test_market_requires_two_outcomes(self):
        """Test that market requires exactly 2 outcomes"""
        outcome1 = create_CR_outcome("Home", -110)
        
        with self.assertRaises(ValueError):
            create_CR_market(
                CR_name="spread",
                CR_outcomes=[outcome1],  # Only 1 outcome
                CR_bookmaker="DraftKings"
            )
    
    def test_market_with_last_update(self):
        """Test market with last_update timestamp"""
        outcome1 = create_CR_outcome("Home", -110)
        outcome2 = create_CR_outcome("Away", +100)
        
        market = create_CR_market(
            CR_name="moneyline",
            CR_outcomes=[outcome1, outcome2],
            CR_bookmaker="FanDuel",
            CR_last_update="2024-03-25T20:00:00Z"
        )
        
        self.assertEqual(market["CR_last_update"], "2024-03-25T20:00:00Z")


class TestCREvent(unittest.TestCase):
    """Test CR_event factory and validation"""
    
    def test_create_basic_event(self):
        """Test creating a basic event"""
        outcome1 = create_CR_outcome("Home", -110)
        outcome2 = create_CR_outcome("Away", +100)
        market = create_CR_market("moneyline", [outcome1, outcome2], "DraftKings")
        
        event = create_CR_event(
            CR_event_id="game_123",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[market]
        )
        
        self.assertEqual(event["CR_event_id"], "game_123")
        self.assertEqual(event["CR_event_name"], "Lakers vs Warriors")
        self.assertEqual(event["CR_sport"], "NBA")
        self.assertEqual(len(event["CR_markets"]), 1)
    
    def test_create_event_with_teams(self):
        """Test creating event with team information"""
        outcome1 = create_CR_outcome("Home", -110)
        outcome2 = create_CR_outcome("Away", +100)
        market = create_CR_market("moneyline", [outcome1, outcome2], "DraftKings")
        
        event = create_CR_event(
            CR_event_id="game_123",
            CR_event_name="Lakers vs Warriors",
            CR_sport="NBA",
            CR_markets=[market],
            CR_home_team="Lakers",
            CR_away_team="Warriors",
            CR_commence_time="2024-03-25T20:00:00Z"
        )
        
        self.assertEqual(event["CR_home_team"], "Lakers")
        self.assertEqual(event["CR_away_team"], "Warriors")
        self.assertEqual(event["CR_commence_time"], "2024-03-25T20:00:00Z")


class TestCRFinding(unittest.TestCase):
    """Test CR_finding factory and validation"""
    
    def test_create_arbitrage_finding(self):
        """Test creating an arbitrage finding"""
        finding = create_CR_finding(
            CR_type="arbitrage",
            CR_description="Arbitrage opportunity detected",
            CR_confidence=0.95,
            CR_event_id="game_123",
            CR_market_name="moneyline",
            CR_bookmakers=["DraftKings", "FanDuel"],
            CR_details={"profit_margin": 0.03}
        )
        
        self.assertEqual(finding["CR_type"], "arbitrage")
        self.assertEqual(finding["CR_confidence"], 0.95)
        self.assertEqual(len(finding["CR_bookmakers"]), 2)
    
    def test_invalid_finding_type(self):
        """Test that invalid finding type raises error"""
        with self.assertRaises(ValueError):
            create_CR_finding(
                CR_type="invalid_type",
                CR_description="Test",
                CR_confidence=0.5,
                CR_event_id="game_123",
                CR_market_name="moneyline",
                CR_bookmakers=["DraftKings"],
                CR_details={}
            )
    
    def test_invalid_confidence_range(self):
        """Test that confidence must be between 0 and 1"""
        with self.assertRaises(ValueError):
            create_CR_finding(
                CR_type="arbitrage",
                CR_description="Test",
                CR_confidence=1.5,  # Invalid
                CR_event_id="game_123",
                CR_market_name="moneyline",
                CR_bookmakers=["DraftKings"],
                CR_details={}
            )


class TestCRSnapshot(unittest.TestCase):
    """Test CR_snapshot factory and validation"""
    
    def test_create_snapshot(self):
        """Test creating a snapshot"""
        outcome1 = create_CR_outcome("Home", -110)
        outcome2 = create_CR_outcome("Away", +100)
        market = create_CR_market("moneyline", [outcome1, outcome2], "DraftKings")
        event = create_CR_event("game_123", "Lakers vs Warriors", "NBA", [market])
        
        snapshot = create_CR_snapshot(
            CR_events=[event],
            CR_timestamp="2024-03-25T20:00:00Z",
            CR_source="test_data.json"
        )
        
        self.assertEqual(len(snapshot["CR_events"]), 1)
        self.assertEqual(snapshot["CR_source"], "test_data.json")
    
    def test_snapshot_with_metadata(self):
        """Test snapshot with metadata"""
        snapshot = create_CR_snapshot(
            CR_events=[],
            CR_timestamp="2024-03-25T20:00:00Z",
            CR_source="test",
            CR_metadata={"version": "1.0", "count": 0}
        )
        
        self.assertIn("CR_metadata", snapshot)
        self.assertEqual(snapshot["CR_metadata"]["version"], "1.0")


class TestOddsConversion(unittest.TestCase):
    """Test odds conversion functions"""
    
    def test_decimal_to_american_positive(self):
        """Test conversion of decimal odds to positive American odds"""
        # 2.5 decimal = +150 American
        american = decimal_to_american_odds(2.5)
        self.assertEqual(american, 150)
    
    def test_decimal_to_american_negative(self):
        """Test conversion of decimal odds to negative American odds"""
        # 1.91 decimal ≈ -110 American
        american = decimal_to_american_odds(1.91)
        self.assertAlmostEqual(american, -110, delta=1)
    
    def test_decimal_to_american_even(self):
        """Test conversion at 2.0 (even odds)"""
        american = decimal_to_american_odds(2.0)
        self.assertEqual(american, 100)
    
    def test_invalid_decimal_odds(self):
        """Test that invalid decimal odds raise error"""
        with self.assertRaises(ValueError):
            decimal_to_american_odds(0.5)
    
    def test_implied_probability_positive_odds(self):
        """Test implied probability calculation for positive odds"""
        # +150 = 40% implied probability
        prob = calculate_implied_probability(150)
        self.assertAlmostEqual(prob, 0.4, places=2)
    
    def test_implied_probability_negative_odds(self):
        """Test implied probability calculation for negative odds"""
        # -110 ≈ 52.4% implied probability
        prob = calculate_implied_probability(-110)
        self.assertAlmostEqual(prob, 0.524, places=2)


class TestSportNormalization(unittest.TestCase):
    """Test sport name normalization"""
    
    def test_normalize_basketball(self):
        """Test basketball normalization"""
        self.assertEqual(normalize_sport_name("basketball"), "NBA")
        self.assertEqual(normalize_sport_name("NBA"), "NBA")
        self.assertEqual(normalize_sport_name("nba"), "NBA")
    
    def test_normalize_football(self):
        """Test football normalization"""
        self.assertEqual(normalize_sport_name("football"), "NFL")
        self.assertEqual(normalize_sport_name("NFL"), "NFL")
    
    def test_normalize_unknown_sport(self):
        """Test unknown sport normalization"""
        result = normalize_sport_name("cricket")
        self.assertEqual(result, "CRICKET")


class TestDataQualityValidation(unittest.TestCase):
    """Test data quality validation"""
    
    def test_valid_data(self):
        """Test validation of valid data"""
        data = {
            "odds": [
                {"game_id": "123", "sport": "NBA"}
            ]
        }
        
        is_valid, errors = validate_data_quality(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_missing_odds_key(self):
        """Test validation fails when odds key is missing"""
        data = {"games": []}
        
        is_valid, errors = validate_data_quality(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_empty_odds_list(self):
        """Test validation fails for empty odds list"""
        data = {"odds": []}
        
        is_valid, errors = validate_data_quality(data)
        self.assertFalse(is_valid)


class TestStructureValidator(unittest.TestCase):
    """Test the StructureValidator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = StructureValidator()
    
    def test_validate_valid_outcome(self):
        """Test validation of valid outcome"""
        outcome = create_CR_outcome("Lakers +5.5", -110, 0.524)
        
        is_valid, errors = self.validator.validate_structure(outcome, "CR_outcome")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_missing_required_field(self):
        """Test validation fails for missing required field"""
        outcome = {"CR_name": "Lakers"}  # Missing CR_price
        
        is_valid, errors = self.validator.validate_structure(outcome, "CR_outcome")
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_unexpected_field(self):
        """Test validation detects unexpected fields"""
        outcome = {
            "CR_name": "Lakers",
            "CR_price": -110,
            "CR_unexpected_field": "value"
        }
        
        is_valid, errors = self.validator.validate_structure(outcome, "CR_outcome")
        self.assertFalse(is_valid)
    
    def test_validate_market_with_wrong_outcome_count(self):
        """Test market validation fails with wrong outcome count"""
        market = {
            "CR_name": "spread",
            "CR_outcomes": [{"CR_name": "Home", "CR_price": -110}],  # Only 1
            "CR_bookmaker": "DraftKings"
        }
        
        is_valid, errors = self.validator.validate_structure(market, "CR_market")
        self.assertFalse(is_valid)
    
    def test_get_supported_structures(self):
        """Test getting list of supported structures"""
        structures = get_supported_structures()
        
        self.assertIn("CR_outcome", structures)
        self.assertIn("CR_market", structures)
        self.assertIn("CR_event", structures)
        self.assertIn("CR_snapshot", structures)
    
    def test_schema_version(self):
        """Test schema version retrieval"""
        version = get_schema_version()
        self.assertIsInstance(version, str)
        self.assertGreater(len(version), 0)


class TestDataLoader(unittest.TestCase):
    """Test data loader functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data = {
            "odds": [
                {
                    "game_id": "test_game_1",
                    "sport": "NBA",
                    "home_team": "Lakers",
                    "away_team": "Warriors",
                    "commence_time": "2024-03-25T20:00:00Z",
                    "sportsbook": "DraftKings",
                    "markets": {
                        "spread": {
                            "home_line": 5.5,
                            "away_line": -5.5,
                            "home_odds": -110,
                            "away_odds": -110
                        },
                        "moneyline": {
                            "home_odds": 150,
                            "away_odds": -180
                        },
                        "total": {
                            "line": 215.5,
                            "over_odds": -110,
                            "under_odds": -110
                        }
                    }
                }
            ]
        }
    
    def test_load_data_from_dict(self):
        """Test loading data from a temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_path = f.name
        
        try:
            snapshot = load_data(temp_path, CR_validate=False)
            
            self.assertIn("CR_events", snapshot)
            self.assertGreater(len(snapshot["CR_events"]), 0)
            self.assertEqual(snapshot["CR_source"], os.path.basename(temp_path))
        finally:
            os.unlink(temp_path)
    
    def test_load_data_file_not_found(self):
        """Test that loading non-existent file raises error"""
        with self.assertRaises(DataLoadError):
            load_data("/nonexistent/path/to/file.json")
    
    def test_load_data_invalid_json(self):
        """Test that invalid JSON raises error"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with self.assertRaises(DataLoadError):
                load_data(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_data_empty_odds(self):
        """Test that empty odds list raises error"""
        empty_data = {"odds": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(empty_data, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(DataQualityError):
                load_data(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_data_creates_markets(self):
        """Test that data loader creates all market types"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_path = f.name
        
        try:
            snapshot = load_data(temp_path, CR_validate=False)
            event = snapshot["CR_events"][0]
            
            # Should have 3 markets (spread, moneyline, total)
            self.assertEqual(len(event["CR_markets"]), 3)
            
            market_names = [m["CR_name"] for m in event["CR_markets"]]
            self.assertIn("spread", market_names)
            self.assertIn("moneyline", market_names)
            self.assertIn("total", market_names)
        finally:
            os.unlink(temp_path)
    
    def test_load_data_calculates_implied_probability(self):
        """Test that loader calculates implied probabilities"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_data, f)
            temp_path = f.name
        
        try:
            snapshot = load_data(temp_path, CR_validate=False)
            event = snapshot["CR_events"][0]
            market = event["CR_markets"][0]
            outcome = market["CR_outcomes"][0]
            
            # Should have implied probability calculated
            self.assertIn("CR_implied_probability", outcome)
            self.assertGreater(outcome["CR_implied_probability"], 0)
            self.assertLess(outcome["CR_implied_probability"], 1)
        finally:
            os.unlink(temp_path)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete Phase 1 implementation"""
    
    def test_end_to_end_data_pipeline(self):
        """Test complete data pipeline from loading to validation"""
        test_data = {
            "odds": [
                {
                    "game_id": "integration_test_1",
                    "sport": "NBA",
                    "home_team": "Lakers",
                    "away_team": "Warriors",
                    "commence_time": "2024-03-25T20:00:00Z",
                    "sportsbook": "DraftKings",
                    "markets": {
                        "moneyline": {
                            "home_odds": -110,
                            "away_odds": +100
                        }
                    }
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = f.name
        
        try:
            # Load data with validation enabled
            snapshot = load_data(temp_path, CR_validate=True)
            
            # Verify snapshot structure
            self.assertIn("CR_events", snapshot)
            self.assertIn("CR_timestamp", snapshot)
            self.assertIn("CR_source", snapshot)
            
            # Verify event structure
            event = snapshot["CR_events"][0]
            self.assertEqual(event["CR_event_id"], "integration_test_1")
            self.assertEqual(event["CR_sport"], "NBA")
            
            # Verify market structure
            market = event["CR_markets"][0]
            self.assertEqual(market["CR_name"], "moneyline")
            self.assertEqual(len(market["CR_outcomes"]), 2)
            
            # Verify outcome structure
            outcome = market["CR_outcomes"][0]
            self.assertIn("CR_name", outcome)
            self.assertIn("CR_price", outcome)
            self.assertIn("CR_implied_probability", outcome)
            
        finally:
            os.unlink(temp_path)
    
    def test_validation_catches_invalid_data(self):
        """Test that validation catches invalid data structures"""
        validator = StructureValidator()
        
        # Create invalid outcome (missing required field)
        invalid_outcome = {"CR_name": "Lakers"}
        
        is_valid, errors = validator.validate_structure(invalid_outcome, "CR_outcome")
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


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

#!/usr/bin/env python3
"""
Structure Validation Framework
Comprehensive validation for CR_ data structures with field-level validation,
type checking, cross-field dependencies, and schema evolution support.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from pathlib import Path


class ValidationError(Exception):
    """Custom validation error with detailed context"""

    def __init__(self, message: str, field_path: str = "", value: Any = None):
        self.message = message
        self.field_path = field_path
        self.value = value
        super().__init__(f"Validation Error at '{field_path}': {message}")


class StructureValidator:
    """Comprehensive CR_ data structure validator"""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.field_types = self._initialize_field_types()
        self.cross_field_validators = self._initialize_cross_field_validators()
        self.schema_version = "1.0"

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules for all CR_ structures"""
        return {
            "CR_outcome": {
                "required_fields": ["CR_name", "CR_price"],
                "optional_fields": ["CR_implied_probability"],
                "field_rules": {
                    "CR_name": {"type": str, "min_length": 1, "max_length": 100},
                    "CR_price": {"type": (int, float), "min_value": -10000, "max_value": 10000},
                    "CR_implied_probability": {"type": (int, float), "min_value": 0.0, "max_value": 1.0}
                }
            },
            "CR_market": {
                "required_fields": ["CR_name", "CR_outcomes", "CR_bookmaker"],
                "optional_fields": ["CR_last_update"],
                "field_rules": {
                    "CR_name": {"type": str, "pattern": r"^(spread|moneyline|total)(_[A-Za-z0-9_]+)?$"},
                    "CR_outcomes": {"type": list, "min_items": 2, "max_items": 2},
                    "CR_bookmaker": {"type": str, "min_length": 1, "max_length": 50},
                    "CR_last_update": {"type": str, "format": "iso_datetime"}
                }
            },
            "CR_event": {
                "required_fields": ["CR_event_id", "CR_event_name", "CR_sport", "CR_markets"],
                "optional_fields": ["CR_commence_time", "CR_home_team", "CR_away_team"],
                "field_rules": {
                    "CR_event_id": {"type": str, "min_length": 1, "max_length": 50},
                    "CR_event_name": {"type": str, "min_length": 1, "max_length": 200},
                    "CR_sport": {"type": str, "allowed_values": ["NBA", "NFL", "MLB", "NHL", "MLS", "WNBA"]},
                    "CR_markets": {"type": list, "min_items": 1},
                    "CR_commence_time": {"type": str, "format": "iso_datetime"},
                    "CR_home_team": {"type": str, "min_length": 1, "max_length": 100},
                    "CR_away_team": {"type": str, "min_length": 1, "max_length": 100}
                }
            },
            "CR_finding": {
                "required_fields": ["CR_type", "CR_description", "CR_confidence", "CR_event_id", "CR_market_name", "CR_bookmakers", "CR_details"],
                "optional_fields": [],
                "field_rules": {
                    "CR_type": {"type": str, "allowed_values": ["arbitrage", "value_edge", "stale_line", "outlier"]},
                    "CR_description": {"type": str, "min_length": 1, "max_length": 500},
                    "CR_confidence": {"type": (int, float), "min_value": 0.0, "max_value": 1.0},
                    "CR_event_id": {"type": str, "min_length": 1},
                    "CR_market_name": {"type": str, "min_length": 1},
                    "CR_bookmakers": {"type": list, "min_items": 1},
                    "CR_details": {"type": dict}
                }
            },
            "CR_snapshot": {
                "required_fields": ["CR_events", "CR_timestamp", "CR_source"],
                "optional_fields": ["CR_metadata"],
                "field_rules": {
                    "CR_events": {"type": list, "min_items": 1},
                    "CR_timestamp": {"type": str, "format": "iso_datetime"},
                    "CR_source": {"type": str, "min_length": 1},
                    "CR_metadata": {"type": dict}
                }
            },
            "CR_briefing": {
                "required_fields": ["CR_summary", "CR_total_events", "CR_total_markets", "CR_findings", "CR_consensus_prices", "CR_timestamp"],
                "optional_fields": ["CR_recommendations", "CR_performance_metrics"],
                "field_rules": {
                    "CR_summary": {"type": str, "min_length": 1, "max_length": 2000},
                    "CR_total_events": {"type": int, "min_value": 0},
                    "CR_total_markets": {"type": int, "min_value": 0},
                    "CR_findings": {"type": list},
                    "CR_consensus_prices": {"type": dict},
                    "CR_timestamp": {"type": str, "format": "iso_datetime"},
                    "CR_recommendations": {"type": list},
                    "CR_performance_metrics": {"type": dict}
                }
            },
            "CR_step": {
                "required_fields": ["CR_step_name", "CR_timestamp", "CR_duration_ms", "CR_status"],
                "optional_fields": ["CR_details"],
                "field_rules": {
                    "CR_step_name": {"type": str, "min_length": 1, "max_length": 100},
                    "CR_timestamp": {"type": str, "format": "iso_datetime"},
                    "CR_duration_ms": {"type": int, "min_value": 0},
                    "CR_status": {"type": str, "allowed_values": ["success", "error", "pending"]},
                    "CR_details": {"type": dict}
                }
            },
            "CR_tool_call": {
                "required_fields": ["CR_tool_name", "CR_timestamp", "CR_inputs", "CR_outputs", "CR_duration_ms", "CR_status"],
                "optional_fields": [],
                "field_rules": {
                    "CR_tool_name": {"type": str, "min_length": 1, "max_length": 100},
                    "CR_timestamp": {"type": str, "format": "iso_datetime"},
                    "CR_inputs": {"type": dict},
                    "CR_outputs": {"type": dict},
                    "CR_duration_ms": {"type": int, "min_value": 0},
                    "CR_status": {"type": str, "allowed_values": ["success", "error"]}
                }
            }
        }

    def _initialize_field_types(self) -> Dict[str, Dict[str, Any]]:
        """Initialize field type definitions and conversion functions"""
        return {
            "iso_datetime": {
                "pattern": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?",
                "converter": self._convert_iso_datetime
            },
            "american_odds": {
                "converter": self._convert_american_odds
            },
            "probability": {
                "converter": self._convert_probability
            }
        }

    def _initialize_cross_field_validators(self) -> Dict[str, List[Callable]]:
        """Initialize cross-field validation functions"""
        return {
            "CR_market": [
                self._validate_market_outcomes_consistency,
                self._validate_spread_line_consistency
            ],
            "CR_event": [
                self._validate_event_team_consistency,
                self._validate_market_uniqueness
            ],
            "CR_finding": [
                self._validate_finding_event_consistency
            ]
        }

    def validate_structure(self, data: Dict[str, Any], structure_type: str) -> Tuple[bool, List[str]]:
        """
        Validate a CR_ data structure

        Args:
            data: The data structure to validate
            structure_type: The type of structure (e.g., "CR_event", "CR_market")

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            if structure_type not in self.validation_rules:
                errors.append(f"Unknown structure type: {structure_type}")
                return False, errors

            rules = self.validation_rules[structure_type]

            # Check required fields
            for field in rules["required_fields"]:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

            # Check for unexpected fields
            allowed_fields = set(rules["required_fields"] + rules["optional_fields"])
            for field in data:
                if field not in allowed_fields:
                    errors.append(f"Unexpected field: {field}")

            # Validate each field
            for field_name, field_value in data.items():
                field_errors = self._validate_field(
                    field_name, field_value, rules["field_rules"].get(field_name, {})
                )
                errors.extend([f"{field_name}: {error}" for error in field_errors])

            # Run cross-field validators
            if structure_type in self.cross_field_validators:
                for validator in self.cross_field_validators[structure_type]:
                    try:
                        validator(data)
                    except ValidationError as e:
                        errors.append(e.message)

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors

    def _validate_field(self, field_name: str, value: Any, rules: Dict[str, Any]) -> List[str]:
        """Validate a single field against its rules"""
        errors = []

        if not rules:
            return errors

        # Type validation
        if "type" in rules:
            expected_type = rules["type"]
            if isinstance(expected_type, tuple):
                if not isinstance(value, expected_type):
                    errors.append(f"Expected type {expected_type}, got {type(value).__name__}")
            else:
                if not isinstance(value, expected_type):
                    # Try type conversion
                    try:
                        converted_value = self._convert_type(value, expected_type)
                        # Note: In a real implementation, we'd modify the original data
                        # For now, we just validate the type
                    except (ValueError, TypeError):
                        errors.append(f"Expected type {expected_type.__name__}, got {type(value).__name__}")

        # String validation
        if isinstance(value, str):
            if "min_length" in rules and len(value) < rules["min_length"]:
                errors.append(f"String too short: {len(value)} < {rules['min_length']}")

            if "max_length" in rules and len(value) > rules["max_length"]:
                errors.append(f"String too long: {len(value)} > {rules['max_length']}")

            if "allowed_values" in rules and value not in rules["allowed_values"]:
                errors.append(f"Value '{value}' not in allowed values: {rules['allowed_values']}")

            if "format" in rules:
                format_errors = self._validate_format(value, rules["format"])
                errors.extend(format_errors)

        # Numeric validation
        if isinstance(value, (int, float)):
            if "min_value" in rules and value < rules["min_value"]:
                errors.append(f"Value too small: {value} < {rules['min_value']}")

            if "max_value" in rules and value > rules["max_value"]:
                errors.append(f"Value too large: {value} > {rules['max_value']}")

        # List validation
        if isinstance(value, list):
            if "min_items" in rules and len(value) < rules["min_items"]:
                errors.append(f"List too short: {len(value)} < {rules['min_items']}")

            if "max_items" in rules and len(value) > rules["max_items"]:
                errors.append(f"List too long: {len(value)} > {rules['max_items']}")

        # Dict validation
        if isinstance(value, dict):
            # Basic dict validation - could be expanded
            pass

        return errors

    def _validate_format(self, value: str, format_type: str) -> List[str]:
        """Validate string format"""
        errors = []

        if format_type == "iso_datetime":
            if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?", value):
                errors.append("Invalid ISO datetime format")

        return errors

    def _convert_type(self, value: Any, target_type: type) -> Any:
        """Convert value to target type"""
        if target_type == str:
            return str(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == bool:
            return bool(value)
        elif target_type == list:
            return list(value) if not isinstance(value, list) else value
        elif target_type == dict:
            return dict(value) if not isinstance(value, dict) else value
        else:
            raise ValueError(f"Unsupported type conversion: {target_type}")

    def _convert_iso_datetime(self, value: str) -> datetime:
        """Convert ISO datetime string to datetime object"""
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValidationError(f"Invalid ISO datetime format: {value}")

    def _convert_american_odds(self, value: Union[int, float, str]) -> int:
        """Convert to American odds format"""
        try:
            odds = int(value)
            if odds < -10000 or odds > 10000:
                raise ValidationError(f"American odds out of range: {odds}")
            return odds
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid American odds: {value}")

    def _convert_probability(self, value: Union[int, float, str]) -> float:
        """Convert to probability (0.0 to 1.0)"""
        try:
            prob = float(value)
            if prob < 0.0 or prob > 1.0:
                raise ValidationError(f"Probability out of range: {prob}")
            return prob
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid probability: {value}")

    def _validate_market_outcomes_consistency(self, data: Dict[str, Any]) -> None:
        """Validate that market outcomes are consistent"""
        if "CR_outcomes" not in data or "CR_name" not in data:
            return

        outcomes = data["CR_outcomes"]
        market_name = data["CR_name"]

        if not isinstance(outcomes, list):
            raise ValidationError("CR_outcomes must be a list", "CR_outcomes")

        # Check moneyline markets have exactly 2 outcomes
        if market_name == "moneyline" and len(outcomes) != 2:
            raise ValidationError(f"Moneyline market must have exactly 2 outcomes, got {len(outcomes)}")

        # Check spread and total markets have consistent line values
        if market_name in ["spread", "total"]:
            for outcome in outcomes:
                if not isinstance(outcome, dict) or "CR_name" not in outcome:
                    raise ValidationError("Invalid outcome structure", "CR_outcomes")

                name = outcome["CR_name"]
                if market_name == "spread":
                    if not re.search(r"[-+]?\d+\.?\d*", name):
                        raise ValidationError(f"Spread outcome must contain line value: {name}")
                elif market_name == "total":
                    if not re.search(r"(Over|Under)\s+\d+\.?\d*", name):
                        raise ValidationError(f"Total outcome must contain line value: {name}")

    def _validate_spread_line_consistency(self, data: Dict[str, Any]) -> None:
        """Validate spread line consistency across outcomes"""
        if "CR_name" not in data or data["CR_name"] != "spread":
            return

        outcomes = data.get("CR_outcomes", [])
        if len(outcomes) != 2:
            return

        # Extract line values from outcome names
        lines = []
        for outcome in outcomes:
            if "CR_name" in outcome:
                match = re.search(r"([-+]?\d+\.?\d*)", outcome["CR_name"])
                if match:
                    lines.append(float(match.group(1)))

        if len(lines) == 2:
            # Lines should be opposites (e.g., -5.5 and +5.5)
            if abs(abs(lines[0]) - abs(lines[1])) > 0.01:
                raise ValidationError(f"Spread lines not consistent: {lines}")

    def _validate_event_team_consistency(self, data: Dict[str, Any]) -> None:
        """Validate event team consistency"""
        if "CR_home_team" not in data or "CR_away_team" not in data or "CR_event_name" not in data:
            return

        home_team = data["CR_home_team"]
        away_team = data["CR_away_team"]
        event_name = data["CR_event_name"]

        # Check that event name contains both teams
        if home_team not in event_name or away_team not in event_name:
            raise ValidationError("Event name must contain both home and away teams")

    def _validate_market_uniqueness(self, data: Dict[str, Any]) -> None:
        """Validate that market names are unique within an event"""
        markets = data.get("CR_markets", [])
        if not isinstance(markets, list):
            return

        market_names = []
        for market in markets:
            if isinstance(market, dict) and "CR_name" in market:
                market_names.append(market["CR_name"])

        if len(market_names) != len(set(market_names)):
            raise ValidationError("Duplicate market names found in event")

    def _validate_finding_event_consistency(self, data: Dict[str, Any]) -> None:
        """Validate that finding references valid event and market"""
        if "CR_event_id" not in data or "CR_market_name" not in data:
            return

        # In a real implementation, we'd check against actual events and markets
        # For now, just validate the format
        event_id = data["CR_event_id"]
        market_name = data["CR_market_name"]

        if not event_id or not isinstance(event_id, str):
            raise ValidationError("Invalid event_id in finding")

        if not market_name or not isinstance(market_name, str):
            raise ValidationError("Invalid market_name in finding")

    def validate_schema_evolution(self, old_data: Dict[str, Any], new_data: Dict[str, Any], structure_type: str) -> Tuple[bool, List[str]]:
        """
        Validate schema evolution from old to new version

        Args:
            old_data: Old version data
            new_data: New version data
            structure_type: Structure type

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        try:
            # Check that required fields are preserved
            rules = self.validation_rules.get(structure_type, {})
            for field in rules.get("required_fields", []):
                if field in old_data and field not in new_data:
                    errors.append(f"Required field {field} was removed in new version")

            # Check that data types are compatible
            for field in old_data:
                if field in new_data:
                    old_type = type(old_data[field])
                    new_type = type(new_data[field])

                    # Check for incompatible type changes
                    if old_type == int and new_type == float:
                        # OK: int to float conversion
                        pass
                    elif old_type == float and new_type == int:
                        # OK: float to int conversion (if no decimal part)
                        if old_data[field] != int(new_data[field]):
                            errors.append(f"Incompatible type change for {field}: {old_type} to {new_type}")
                    elif old_type != new_type:
                        errors.append(f"Incompatible type change for {field}: {old_type} to {new_type}")

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"Schema evolution validation error: {str(e)}")
            return False, errors

    def generate_validation_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive validation report"""
        total_structures = len(results)
        valid_structures = sum(1 for r in results if r.get("valid", False))
        total_errors = sum(len(r.get("errors", [])) for r in results)

        report = f"""
# Structure Validation Report
Generated: {datetime.now().isoformat()}
Schema Version: {self.schema_version}

## Summary
- Total Structures: {total_structures}
- Valid Structures: {valid_structures}
- Invalid Structures: {total_structures - valid_structures}
- Total Errors: {total_errors}
- Success Rate: {(valid_structures/total_structures*100):.1f}%

## Structure Details
"""

        for result in results:
            status = "✅ VALID" if result.get("valid", False) else "❌ INVALID"
            report += f"\n### {status}: {result.get('structure_type', 'Unknown')}\n"

            if result.get("structure_id"):
                report += f"- Structure ID: {result['structure_id']}\n"

            if result.get("errors"):
                report += "- Errors:\n"
                for error in result["errors"]:
                    report += f"  - {error}\n"

            if result.get("warnings"):
                report += "- Warnings:\n"
                for warning in result["warnings"]:
                    report += f"  - {warning}\n"

        return report


def main():
    """Main validation function for CLI usage"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="CR_ Structure Validator")
    parser.add_argument("file", help="JSON file to validate")
    parser.add_argument("--type", required=True, help="Structure type to validate against")
    parser.add_argument("--report", help="Output report file")
    parser.add_argument("--schema-evolution", help="Compare against old version file")

    args = parser.parse_args()

    validator = StructureValidator()

    try:
        with open(args.file, 'r') as f:
            data = json.load(f)

        if args.schema_evolution:
            with open(args.schema_evolution, 'r') as f:
                old_data = json.load(f)

            is_valid, errors = validator.validate_schema_evolution(old_data, data, args.type)
        else:
            is_valid, errors = validator.validate_structure(data, args.type)

        if is_valid:
            print(f"✅ Validation passed for {args.type}")
        else:
            print(f"❌ Validation failed for {args.type}")
            for error in errors:
                print(f"  - {error}")

        if args.report:
            results = [{
                "structure_type": args.type,
                "structure_id": data.get("CR_event_id", "unknown"),
                "valid": is_valid,
                "errors": errors,
                "warnings": []
            }]

            report = validator.generate_validation_report(results)
            with open(args.report, 'w') as f:
                f.write(report)
            print(f"Report saved to: {args.report}")

        return 0 if is_valid else 1

    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return 1
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

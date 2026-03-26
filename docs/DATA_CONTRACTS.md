# CR_ Data Contracts Documentation

## Overview

This document describes the CR_ data contract system implemented in Phase 1: Data Structure Alignment. All data structures use dictionary-based schemas with factory functions and comprehensive validation.

## Schema Version

Current Version: **1.0**

## Core Principles

1. **Dictionary-Based**: All structures are Python dictionaries, not dataclasses
2. **CR_ Prefix**: All keys use the `CR_` prefix for consistency
3. **Factory Functions**: Use factory functions to create structures
4. **Validation**: All structures can be validated using the validation framework
5. **Type Safety**: Factory functions provide type hints and runtime type checking

## Data Structures

### CR_outcome

Represents a single betting outcome within a market.

**Required Fields:**
- `CR_name` (str): Outcome name (e.g., "Lakers +5.5", "Over 215.5")
- `CR_price` (int): American odds (e.g., -110, +150)

**Optional Fields:**
- `CR_implied_probability` (float): Implied probability (0.0 to 1.0)

**Factory Function:**
```python
from packages.data.contracts import create_CR_outcome

outcome = create_CR_outcome(
    CR_name="Lakers +5.5",
    CR_price=-110,
    CR_implied_probability=0.524
)
```

**Example:**
```json
{
    "CR_name": "Lakers +5.5",
    "CR_price": -110,
    "CR_implied_probability": 0.524
}
```

### CR_market

Represents a betting market (e.g., spread, moneyline, total).

**Required Fields:**
- `CR_name` (str): Market name - must be one of: "spread", "moneyline", "total"
- `CR_outcomes` (list): List of exactly 2 CR_outcome dictionaries
- `CR_bookmaker` (str): Bookmaker/sportsbook name

**Optional Fields:**
- `CR_last_update` (str): ISO datetime string of last update

**Factory Function:**
```python
from packages.data.contracts import create_CR_market

market = create_CR_market(
    CR_name="spread",
    CR_outcomes=[outcome1, outcome2],
    CR_bookmaker="DraftKings",
    CR_last_update="2024-03-25T20:00:00Z"
)
```

**Example:**
```json
{
    "CR_name": "spread",
    "CR_outcomes": [
        {"CR_name": "Lakers +5.5", "CR_price": -110},
        {"CR_name": "Warriors -5.5", "CR_price": -110}
    ],
    "CR_bookmaker": "DraftKings",
    "CR_last_update": "2024-03-25T20:00:00Z"
}
```

### CR_event

Represents a sporting event with associated markets.

**Required Fields:**
- `CR_event_id` (str): Unique event identifier
- `CR_event_name` (str): Event name (e.g., "Lakers vs Warriors")
- `CR_sport` (str): Sport name - must be one of: "NBA", "NFL", "MLB", "NHL", "MLS", "WNBA"
- `CR_markets` (list): List of CR_market dictionaries (minimum 1)

**Optional Fields:**
- `CR_commence_time` (str): ISO datetime string of event start time
- `CR_home_team` (str): Home team name
- `CR_away_team` (str): Away team name

**Factory Function:**
```python
from packages.data.contracts import create_CR_event

event = create_CR_event(
    CR_event_id="game_123",
    CR_event_name="Lakers vs Warriors",
    CR_sport="NBA",
    CR_markets=[market1, market2],
    CR_commence_time="2024-03-25T20:00:00Z",
    CR_home_team="Lakers",
    CR_away_team="Warriors"
)
```

### CR_finding

Represents a system finding (arbitrage, value edge, etc.).

**Required Fields:**
- `CR_type` (str): Finding type - must be one of: "arbitrage", "value_edge", "stale_line", "outlier"
- `CR_description` (str): Human-readable description
- `CR_confidence` (float): Confidence score (0.0 to 1.0)
- `CR_event_id` (str): Associated event ID
- `CR_market_name` (str): Associated market name
- `CR_bookmakers` (list): List of bookmaker names involved
- `CR_details` (dict): Additional details dictionary

**Factory Function:**
```python
from packages.data.contracts import create_CR_finding

finding = create_CR_finding(
    CR_type="arbitrage",
    CR_description="Arbitrage opportunity detected",
    CR_confidence=0.95,
    CR_event_id="game_123",
    CR_market_name="moneyline",
    CR_bookmakers=["DraftKings", "FanDuel"],
    CR_details={"profit_margin": 0.03}
)
```

### CR_snapshot

Represents a complete dataset snapshot.

**Required Fields:**
- `CR_events` (list): List of CR_event dictionaries (minimum 1)
- `CR_timestamp` (str): ISO datetime string of snapshot creation
- `CR_source` (str): Data source identifier

**Optional Fields:**
- `CR_metadata` (dict): Additional metadata dictionary

**Factory Function:**
```python
from packages.data.contracts import create_CR_snapshot

snapshot = create_CR_snapshot(
    CR_events=[event1, event2],
    CR_timestamp="2024-03-25T20:00:00Z",
    CR_source="betstamp_api",
    CR_metadata={"version": "1.0", "count": 2}
)
```

### CR_briefing

Represents a structured briefing output.

**Required Fields:**
- `CR_summary` (str): Executive summary text
- `CR_total_events` (int): Total number of events analyzed
- `CR_total_markets` (int): Total number of markets analyzed
- `CR_findings` (list): List of CR_finding dictionaries
- `CR_consensus_prices` (dict): Dictionary of consensus prices
- `CR_timestamp` (str): ISO datetime string

**Optional Fields:**
- `CR_recommendations` (list): List of recommendation dictionaries
- `CR_performance_metrics` (dict): Performance metrics dictionary

### CR_step

Represents an execution step for tracing.

**Required Fields:**
- `CR_step_name` (str): Step name
- `CR_timestamp` (str): ISO datetime string
- `CR_duration_ms` (int): Duration in milliseconds
- `CR_status` (str): Status - must be one of: "success", "error", "pending"

**Optional Fields:**
- `CR_details` (dict): Additional details dictionary

### CR_tool_call

Represents a tool execution record.

**Required Fields:**
- `CR_tool_name` (str): Tool name
- `CR_timestamp` (str): ISO datetime string
- `CR_inputs` (dict): Input parameters dictionary
- `CR_outputs` (dict): Output results dictionary
- `CR_duration_ms` (int): Duration in milliseconds
- `CR_status` (str): Status - must be one of: "success", "error"

## Validation

### Using Validation

All structures can be validated using the `validate_CR_structure` function:

```python
from packages.data.contracts import validate_CR_structure

# Validate a structure
try:
    validate_CR_structure(my_event, "CR_event")
    print("✅ Validation passed")
except ValueError as e:
    print(f"❌ Validation failed: {e}")
```

### Validation Framework

The validation framework provides:

1. **Field-level validation**: Type checking, range validation, format validation
2. **Cross-field validation**: Consistency checks across multiple fields
3. **Schema evolution support**: Backward compatibility checking
4. **Detailed error reporting**: Clear error messages with field paths

Example:
```python
from packages.validation.structure_validator import StructureValidator

validator = StructureValidator()
is_valid, errors = validator.validate_structure(my_data, "CR_event")

if not is_valid:
    for error in errors:
        print(f"  - {error}")
```

## Odds Format

All odds in the system use **American odds format**:

- **Negative odds** (e.g., -110): Amount you must bet to win $100
- **Positive odds** (e.g., +150): Amount you win if you bet $100

### Converting Decimal to American Odds

```python
from packages.data.loader import decimal_to_american_odds

# Convert 2.5 decimal odds to American
american = decimal_to_american_odds(2.5)  # Returns +150
```

### Calculating Implied Probability

```python
from packages.data.loader import calculate_implied_probability

# Calculate implied probability from American odds
prob = calculate_implied_probability(-110)  # Returns ~0.524 (52.4%)
```

## Data Loading

### Loading Data

Use the `load_data` function to load and normalize data:

```python
from packages.data.loader import load_data

# Load with validation (default)
snapshot = load_data("path/to/data.json", CR_validate=True)

# Load without validation (faster)
snapshot = load_data("path/to/data.json", CR_validate=False)

# Load default sample data
snapshot = load_data()
```

### Data Quality Checks

The loader performs automatic data quality checks:

1. **File validation**: Checks file exists and is valid JSON
2. **Structure validation**: Ensures required keys are present
3. **Data normalization**: Converts odds formats, normalizes sport names
4. **Error handling**: Graceful handling with detailed error messages

### Error Handling

```python
from packages.data.loader import DataLoadError, DataQualityError

try:
    snapshot = load_data("data.json")
except DataLoadError as e:
    print(f"Failed to load data: {e}")
except DataQualityError as e:
    print(f"Data quality issues: {e}")
```

## Best Practices

### 1. Always Use Factory Functions

❌ **Don't** create structures manually:
```python
outcome = {
    "CR_name": "Lakers",
    "CR_price": -110
}
```

✅ **Do** use factory functions:
```python
outcome = create_CR_outcome(
    CR_name="Lakers",
    CR_price=-110
)
```

### 2. Validate Critical Data

Always validate data at system boundaries:

```python
# Validate data coming from external sources
snapshot = load_data("external_data.json", CR_validate=True)

# Validate before persisting
validate_CR_structure(my_event, "CR_event")
save_to_database(my_event)
```

### 3. Use Type Hints

Factory functions provide type hints for IDE support:

```python
from typing import Dict, Any

def process_event(CR_event: Dict[str, Any]) -> None:
    # IDE will provide autocomplete and type checking
    event_id = CR_event["CR_event_id"]
```

### 4. Handle Errors Gracefully

```python
try:
    market = create_CR_market(
        CR_name="spread",
        CR_outcomes=[outcome1],  # Wrong count
        CR_bookmaker="DraftKings"
    )
except ValueError as e:
    logger.error(f"Failed to create market: {e}")
    # Handle error appropriately
```

## Migration from Dataclasses

If you have existing code using the old dataclass-based structures:

### Before (Dataclasses):
```python
from packages.data.contracts import CR_outcome

outcome = CR_outcome(
    name="Lakers",
    price=-110,
    implied_probability=0.524
)

# Access fields
print(outcome.name)
```

### After (Dictionaries):
```python
from packages.data.contracts import create_CR_outcome

outcome = create_CR_outcome(
    CR_name="Lakers",
    CR_price=-110,
    CR_implied_probability=0.524
)

# Access fields
print(outcome["CR_name"])
```

## Schema Versioning

The schema version is tracked in the contracts module:

```python
from packages.data.contracts import get_schema_version

version = get_schema_version()  # Returns "1.0"
```

## Supported Structures

Get a list of all supported structure types:

```python
from packages.data.contracts import get_supported_structures

structures = get_supported_structures()
# Returns: ["CR_outcome", "CR_market", "CR_event", ...]
```

## See Also

- [Validation Rules](VALIDATION_RULES.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [API Documentation](API_DOCS.md)

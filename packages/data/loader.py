"""
CR_ Data Loader - Load and normalize dataset with validation
Phase 1: Data Structure Alignment - Dictionary-based loading with American odds conversion
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import logging

from .contracts import (
    create_CR_outcome,
    create_CR_market,
    create_CR_event,
    create_CR_snapshot,
    validate_CR_structure
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """Custom exception for data loading errors"""
    pass


class DataQualityError(Exception):
    """Custom exception for data quality issues"""
    pass


def decimal_to_american_odds(CR_decimal_odds: float) -> int:
    """
    Convert decimal odds to American odds format

    Args:
        CR_decimal_odds: Decimal odds (e.g., 2.5, 1.91)

    Returns:
        American odds (e.g., +150, -110)
    """
    if CR_decimal_odds < 1.0:
        raise ValueError(f"Decimal odds must be >= 1.0, got {CR_decimal_odds}")

    if CR_decimal_odds >= 2.0:
        # Positive American odds
        CR_american_odds = int((CR_decimal_odds - 1) * 100)
    else:
        # Negative American odds
        CR_american_odds = int(-100 / (CR_decimal_odds - 1))

    return CR_american_odds


def calculate_implied_probability(CR_american_odds: int) -> float:
    """
    Calculate implied probability from American odds

    Args:
        CR_american_odds: American odds (e.g., -110, +150)

    Returns:
        Implied probability (0.0 to 1.0)
    """
    if CR_american_odds > 0:
        # Positive odds
        return 100 / (CR_american_odds + 100)
    else:
        # Negative odds
        return abs(CR_american_odds) / (abs(CR_american_odds) + 100)


def normalize_sport_name(CR_sport: str) -> str:
    """
    Normalize sport name to standard format

    Args:
        CR_sport: Raw sport name

    Returns:
        Normalized sport name
    """
    CR_sport_mapping = {
        'basketball': 'NBA',
        'nba': 'NBA',
        'football': 'NFL',
        'nfl': 'NFL',
        'baseball': 'MLB',
        'mlb': 'MLB',
        'hockey': 'NHL',
        'nhl': 'NHL',
        'soccer': 'MLS',
        'mls': 'MLS',
        'wnba': 'WNBA'
    }

    return CR_sport_mapping.get(CR_sport.lower(), CR_sport.upper())


def validate_data_quality(CR_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate data quality before processing

    Args:
        CR_data: Raw data dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    CR_errors = []

    if not isinstance(CR_data, dict):
        CR_errors.append("Data must be a dictionary")
        return False, CR_errors

    if 'odds' not in CR_data:
        CR_errors.append("Missing 'odds' key in data")

    if not isinstance(CR_data.get('odds', []), list):
        CR_errors.append("'odds' must be a list")

    if len(CR_data.get('odds', [])) == 0:
        CR_errors.append("'odds' list is empty")

    return len(CR_errors) == 0, CR_errors


def load_data(CR_file_path: Optional[str] = None, CR_validate: bool = True) -> Dict[str, Any]:
    """
    Load JSON dataset and normalize to CR_ structure

    Args:
        CR_file_path: Path to data file, defaults to Betstamp sample data
        CR_validate: Whether to validate structures (default: True)

    Returns:
        CR_snapshot dictionary with normalized data

    Raises:
        DataLoadError: If file cannot be loaded
        DataQualityError: If data quality checks fail
    """
    if CR_file_path is None:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        CR_file_path = os.path.join(current_dir, 'data', 'Betstamp AI Odds Agent - sample_odds_data.json')

    logger.info(f"Loading data from: {CR_file_path}")

    try:
        with open(CR_file_path, 'r', encoding='utf-8') as f:
            CR_raw_data = json.load(f)
    except FileNotFoundError:
        raise DataLoadError(f"Data file not found: {CR_file_path}")
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in data file: {e}")
    except Exception as e:
        raise DataLoadError(f"Error loading data file: {e}")

    # Validate data quality
    CR_is_valid, CR_quality_errors = validate_data_quality(CR_raw_data)
    if not CR_is_valid:
        error_msg = "Data quality validation failed:\n" + "\n".join(f"  - {err}" for err in CR_quality_errors)
        raise DataQualityError(error_msg)

    logger.info(f"Processing {len(CR_raw_data.get('odds', []))} odds records")

    # Process data
    CR_events = []
    CR_processing_errors = []

    # Group by game_id to aggregate all sportsbooks for each game
    CR_games_by_id = {}
    for CR_game_data in CR_raw_data.get('odds', []):
        CR_game_id = CR_game_data.get('game_id', '')
        if not CR_game_id:
            CR_processing_errors.append("Found game with missing game_id")
            continue

        if CR_game_id not in CR_games_by_id:
            CR_games_by_id[CR_game_id] = {
                'game_data': CR_game_data,
                'all_game_data': []
            }
        CR_games_by_id[CR_game_id]['all_game_data'].append(CR_game_data)

    logger.info(f"Found {len(CR_games_by_id)} unique games")

    # Create CR_events from grouped games
    for CR_game_id, CR_game_info in CR_games_by_id.items():
        try:
            CR_game_data = CR_game_info['game_data']
            CR_all_game_data = CR_game_info['all_game_data']

            # Create all markets for this game across all sportsbooks
            CR_all_markets = []
            for CR_sportsbook_data in CR_all_game_data:
                CR_markets = _create_markets_from_betstamp(CR_sportsbook_data)
                CR_all_markets.extend(CR_markets)

            if not CR_all_markets:
                CR_processing_errors.append(f"No markets found for game {CR_game_id}")
                continue

            # Create event
            CR_event_name = f"{CR_game_data.get('home_team', 'Unknown')} vs {CR_game_data.get('away_team', 'Unknown')}"
            CR_sport = normalize_sport_name(CR_game_data.get('sport', 'Unknown'))
            CR_commence_time = CR_game_data.get('commence_time', datetime.now().isoformat())

            CR_event = create_CR_event(
                CR_event_id=CR_game_id,
                CR_event_name=CR_event_name,
                CR_sport=CR_sport,
                CR_markets=CR_all_markets,
                CR_commence_time=CR_commence_time,
                CR_home_team=CR_game_data.get('home_team'),
                CR_away_team=CR_game_data.get('away_team')
            )

            # Validate event if requested
            if CR_validate:
                try:
                    validate_CR_structure(CR_event, "CR_event")
                except ValueError as e:
                    CR_processing_errors.append(f"Event validation failed for {CR_game_id}: {e}")
                    continue

            CR_events.append(CR_event)

        except Exception as e:
            CR_processing_errors.append(f"Error processing game {CR_game_id}: {e}")
            logger.error(f"Error processing game {CR_game_id}: {e}")

    if CR_processing_errors:
        logger.warning(f"Encountered {len(CR_processing_errors)} processing errors")
        for error in CR_processing_errors[:5]:
            logger.warning(f"  - {error}")

    if not CR_events:
        raise DataQualityError("No valid events could be created from the data")

    logger.info(f"Successfully created {len(CR_events)} events")

    # Create snapshot
    CR_snapshot = create_CR_snapshot(
        CR_events=CR_events,
        CR_timestamp=datetime.now().isoformat(),
        CR_source=os.path.basename(CR_file_path),
        CR_metadata={
            "total_games_processed": len(CR_games_by_id),
            "total_events_created": len(CR_events),
            "processing_errors": len(CR_processing_errors),
            "validation_enabled": CR_validate
        }
    )

    # Validate snapshot if requested
    if CR_validate:
        try:
            validate_CR_structure(CR_snapshot, "CR_snapshot")
        except ValueError as e:
            raise DataQualityError(f"Snapshot validation failed: {e}")

    logger.info("Data loading completed successfully")

    return CR_snapshot


def _create_markets_from_betstamp(CR_game_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create CR_market dictionaries from Betstamp game data

    Args:
        CR_game_data: Raw game data from Betstamp

    Returns:
        List of CR_market dictionaries
    """
    CR_markets = []
    CR_markets_data = CR_game_data.get('markets', {})
    CR_sportsbook = CR_game_data.get('sportsbook', 'Unknown')

    # Create spread market
    if 'spread' in CR_markets_data:
        try:
            CR_spread = CR_markets_data['spread']
            CR_home_line = CR_spread.get('home_line', 0)
            CR_away_line = CR_spread.get('away_line', 0)
            CR_home_odds = CR_spread.get('home_odds', 0)
            CR_away_odds = CR_spread.get('away_odds', 0)

            # Convert to American odds if needed (assuming input is decimal)
            if isinstance(CR_home_odds, float) and CR_home_odds > 1.0 and CR_home_odds < 100:
                CR_home_odds = decimal_to_american_odds(CR_home_odds)
            if isinstance(CR_away_odds, float) and CR_away_odds > 1.0 and CR_away_odds < 100:
                CR_away_odds = decimal_to_american_odds(CR_away_odds)

            CR_home_outcome = create_CR_outcome(
                CR_name=f"{CR_game_data.get('home_team', 'Home')} {CR_home_line:+.1f}",
                CR_price=int(CR_home_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_home_odds))
            )

            CR_away_outcome = create_CR_outcome(
                CR_name=f"{CR_game_data.get('away_team', 'Away')} {CR_away_line:+.1f}",
                CR_price=int(CR_away_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_away_odds))
            )

            CR_market = create_CR_market(
                CR_name=f"spread_{CR_sportsbook}",
                CR_outcomes=[CR_home_outcome, CR_away_outcome],
                CR_bookmaker=CR_sportsbook
            )

            CR_markets.append(CR_market)
        except Exception as e:
            logger.warning(f"Error creating spread market for {CR_sportsbook}: {e}")

    # Create moneyline market
    if 'moneyline' in CR_markets_data:
        try:
            CR_moneyline = CR_markets_data['moneyline']
            CR_home_odds = CR_moneyline.get('home_odds', 0)
            CR_away_odds = CR_moneyline.get('away_odds', 0)

            # Convert to American odds if needed
            if isinstance(CR_home_odds, float) and CR_home_odds > 1.0 and CR_home_odds < 100:
                CR_home_odds = decimal_to_american_odds(CR_home_odds)
            if isinstance(CR_away_odds, float) and CR_away_odds > 1.0 and CR_away_odds < 100:
                CR_away_odds = decimal_to_american_odds(CR_away_odds)

            CR_home_outcome = create_CR_outcome(
                CR_name=CR_game_data.get('home_team', 'Home'),
                CR_price=int(CR_home_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_home_odds))
            )

            CR_away_outcome = create_CR_outcome(
                CR_name=CR_game_data.get('away_team', 'Away'),
                CR_price=int(CR_away_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_away_odds))
            )

            CR_market = create_CR_market(
                CR_name=f"moneyline_{CR_sportsbook}",
                CR_outcomes=[CR_home_outcome, CR_away_outcome],
                CR_bookmaker=CR_sportsbook
            )

            CR_markets.append(CR_market)
        except Exception as e:
            logger.warning(f"Error creating moneyline market for {CR_sportsbook}: {e}")

    # Create total market
    if 'total' in CR_markets_data:
        try:
            CR_total = CR_markets_data['total']
            CR_line = CR_total.get('line', 0)
            CR_over_odds = CR_total.get('over_odds', 0)
            CR_under_odds = CR_total.get('under_odds', 0)

            # Convert to American odds if needed
            if isinstance(CR_over_odds, float) and CR_over_odds > 1.0 and CR_over_odds < 100:
                CR_over_odds = decimal_to_american_odds(CR_over_odds)
            if isinstance(CR_under_odds, float) and CR_under_odds > 1.0 and CR_under_odds < 100:
                CR_under_odds = decimal_to_american_odds(CR_under_odds)

            CR_over_outcome = create_CR_outcome(
                CR_name=f"Over {CR_line}",
                CR_price=int(CR_over_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_over_odds))
            )

            CR_under_outcome = create_CR_outcome(
                CR_name=f"Under {CR_line}",
                CR_price=int(CR_under_odds),
                CR_implied_probability=calculate_implied_probability(int(CR_under_odds))
            )

            CR_market = create_CR_market(
                CR_name=f"total_{CR_sportsbook}",
                CR_outcomes=[CR_over_outcome, CR_under_outcome],
                CR_bookmaker=CR_sportsbook
            )

            CR_markets.append(CR_market)
        except Exception as e:
            logger.warning(f"Error creating total market for {CR_sportsbook}: {e}")

    return CR_markets

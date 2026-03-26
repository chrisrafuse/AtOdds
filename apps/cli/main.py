#!/usr/bin/env python3
"""
CR_ compliant CLI entry point for AtOdds system
Runs complete analysis pipeline with CR_ prefix throughout
"""

import sys
import os
import argparse
from datetime import datetime

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from packages.data.loader import load_data
from packages.agent.agent import execute_CR_analysis_pipeline
from packages.reporting.briefing import generate_CR_briefing, generate_CR_json_briefing
from packages.observability.trace_cr import get_CR_tracer


def parse_CR_arguments() -> argparse.Namespace:
    """
    Parse CR_ command-line arguments

    Returns:
        Parsed CR_ arguments
    """
    CR_parser = argparse.ArgumentParser(
        description='AtOdds - CR_ compliant odds analysis system'
    )

    CR_parser.add_argument(
        '--data-file',
        dest='CR_data_file',
        type=str,
        default='data/sample_odds.json',
        help='Path to CR_ data file (default: data/sample_odds.json)'
    )

    CR_parser.add_argument(
        '--output-format',
        dest='CR_output_format',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format: text or json (default: text)'
    )

    CR_parser.add_argument(
        '--trace',
        dest='CR_enable_trace',
        action='store_true',
        help='Enable CR_ execution tracing'
    )

    CR_parser.add_argument(
        '--verbose',
        dest='CR_verbose',
        action='store_true',
        help='Enable verbose CR_ output'
    )

    return CR_parser.parse_args()


def run_CR_cli_pipeline(CR_args: argparse.Namespace) -> int:
    """
    Run complete CR_ CLI pipeline

    Args:
        CR_args: Parsed CR_ command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    CR_tracer = None

    try:
        # Start tracing if enabled
        if CR_args.CR_enable_trace:
            CR_tracer = get_CR_tracer()
            CR_session_id = CR_tracer.start_CR_session()
            if CR_args.CR_verbose:
                print(f"✓ Started CR_ trace session: {CR_session_id}")

        # Load data
        if CR_args.CR_verbose:
            print(f"Loading CR_ data from: {CR_args.CR_data_file}")

        CR_snapshot = load_data(CR_args.CR_data_file)

        if CR_args.CR_verbose:
            CR_event_count = len(CR_snapshot.get('CR_events', []))
            print(f"✓ Loaded {CR_event_count} CR_ events")

        # Run complete analysis pipeline
        if CR_args.CR_verbose:
            print("Running CR_ analysis pipeline...")

        CR_results = execute_CR_analysis_pipeline(CR_snapshot)

        CR_findings = CR_results.get('CR_findings', [])
        CR_summary = CR_results.get('CR_findings_summary', {})

        if CR_args.CR_verbose:
            CR_total_findings = CR_summary.get('CR_total_findings', 0)
            print(f"✓ Analysis complete: {CR_total_findings} CR_ findings")

        # Generate and output briefing
        if CR_args.CR_output_format == 'json':
            import json
            CR_briefing = generate_CR_json_briefing(CR_findings, CR_snapshot)
            print(json.dumps(CR_briefing, indent=2))
        else:
            CR_briefing = generate_CR_briefing(CR_findings, CR_snapshot)
            print(CR_briefing)

        # End tracing if enabled
        if CR_tracer:
            CR_trace_summary = CR_tracer.end_CR_session()
            if CR_args.CR_verbose:
                CR_duration = CR_trace_summary.get('CR_duration_seconds', 0)
                print(f"\n✓ CR_ trace session completed in {CR_duration:.2f}s")

        return 0

    except FileNotFoundError as CR_error:
        print(f"✗ CR_ Error: Data file not found - {CR_error}")
        if CR_tracer:
            CR_tracer.log_CR_error(CR_error, {'CR_context': 'file_loading'})
            CR_tracer.end_CR_session()
        return 1

    except Exception as CR_error:
        print(f"✗ CR_ Error: {CR_error}")
        if CR_tracer:
            CR_tracer.log_CR_error(CR_error, {'CR_context': 'pipeline_execution'})
            CR_tracer.end_CR_session()
        return 1


def main():
    """CR_ compliant entry point - runs full pipeline and prints briefing"""
    CR_args = parse_CR_arguments()
    CR_exit_code = run_CR_cli_pipeline(CR_args)
    sys.exit(CR_exit_code)


if __name__ == "__main__":
    main()

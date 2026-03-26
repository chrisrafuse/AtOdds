"""
Agent orchestration logic with CR_ prefix compliance
NO math here, NO logic duplication
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from packages.tools.registry import CR_TOOL_REGISTRY
from packages.llm.tool_schemas import CR_TOOL_SCHEMAS


@dataclass
class CR_LLMAgentResult:
    """Result from an LLM-powered analysis run."""
    CR_findings: List[Dict[str, Any]]
    CR_tool_trace: List[Any]        # List[CR_ToolCall] — typed at runtime
    CR_llm_summary: str             # Final LLM narrative
    CR_provider: str
    CR_model: str


def _CR_tool_executor(CR_tool_name: str, CR_args: Dict[str, Any]) -> Any:
    """
    Execute a tool from CR_TOOL_REGISTRY by name with the given arguments.
    Called by the LLM provider during the tool-calling loop.
    """
    CR_tool_fn = CR_TOOL_REGISTRY.get(CR_tool_name)
    if CR_tool_fn is None:
        raise ValueError(f"Unknown tool: {CR_tool_name}")
    return CR_tool_fn(**CR_args)


def run_CR_llm_agent(
    CR_snapshot: Dict[str, Any],
    CR_provider_name: Optional[str] = None
) -> CR_LLMAgentResult:
    """
    Run analysis using a real LLM provider with function calling.
    Falls back to mock provider when no API key is configured.

    Args:
        CR_snapshot: Loaded data snapshot dictionary
        CR_provider_name: Override provider ("openai"|"anthropic"|"gemini"|"mock")

    Returns:
        CR_LLMAgentResult with findings, tool trace, and LLM narrative
    """
    from packages.llm.factory import get_CR_llm_provider
    from packages.agent.prompts import CR_SYSTEM_PROMPT, build_CR_analysis_user_message

    CR_provider = get_CR_llm_provider(CR_provider_name)

    CR_messages = [
        {"role": "system", "content": CR_SYSTEM_PROMPT},
        {"role": "user", "content": build_CR_analysis_user_message(CR_snapshot)},
    ]

    CR_response = CR_provider.chat_with_tools(
        CR_messages=CR_messages,
        CR_tools=CR_TOOL_SCHEMAS,
        CR_tool_executor=_CR_tool_executor,
        CR_max_iterations=12
    )

    # Collect findings from tool calls that returned CR_result lists
    CR_all_findings: List[Dict[str, Any]] = []
    CR_detection_tools = {
        "CR_detect_arbitrage", "CR_detect_stale_lines",
        "CR_detect_outliers", "CR_detect_value_edges"
    }
    for CR_tc in CR_response.CR_tool_calls:
        if CR_tc.CR_tool_name in CR_detection_tools and CR_tc.CR_result:
            CR_found = CR_tc.CR_result.get("CR_result", [])
            if isinstance(CR_found, list):
                CR_all_findings.extend(CR_found)

    CR_all_findings.sort(key=lambda CR_f: CR_f.get("CR_confidence", 0), reverse=True)

    return CR_LLMAgentResult(
        CR_findings=CR_all_findings,
        CR_tool_trace=CR_response.CR_tool_calls,
        CR_llm_summary=CR_response.CR_content,
        CR_provider=CR_response.CR_provider,
        CR_model=CR_response.CR_model
    )


def run_CR_agent(CR_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Orchestrate system by calling tools and gathering findings

    Args:
        CR_snapshot: Loaded data snapshot dictionary

    Returns:
        List of all CR_finding dictionaries from detection tools
    """
    CR_all_findings = []

    # 1. Load tools
    CR_tools = {
        'CR_detect_arbitrage': CR_TOOL_REGISTRY['CR_detect_arbitrage'],
        'CR_detect_stale_lines': CR_TOOL_REGISTRY['CR_detect_stale_lines'],
        'CR_detect_outliers': CR_TOOL_REGISTRY['CR_detect_outliers'],
        'CR_detect_value_edges': CR_TOOL_REGISTRY['CR_detect_value_edges'],
    }

    # 2. Call tools
    for CR_tool_name, CR_tool_func in CR_tools.items():
        try:
            if CR_tool_name == 'CR_detect_stale_lines':
                CR_result = CR_tool_func(CR_snapshot, CR_stale_threshold_hours=24)
            elif CR_tool_name == 'CR_detect_outliers':
                CR_result = CR_tool_func(CR_snapshot, CR_outlier_threshold=2.0)
            elif CR_tool_name == 'CR_detect_value_edges':
                CR_result = CR_tool_func(CR_snapshot, CR_edge_threshold=0.05)
            else:
                CR_result = CR_tool_func(CR_snapshot)

            # 3. Gather findings
            if CR_result.get('CR_success'):
                CR_findings = CR_result.get('CR_result', [])
                CR_all_findings.extend(CR_findings)
                print(f"✓ {CR_tool_name}: {len(CR_findings)} findings")
            else:
                CR_error = CR_result.get('CR_error', 'Unknown error')
                print(f"✗ {CR_tool_name}: {CR_error}")

        except Exception as CR_exception:
            print(f"✗ {CR_tool_name}: Unexpected error - {CR_exception}")

    # 4. Sort findings by confidence
    CR_all_findings.sort(key=lambda CR_f: CR_f.get('CR_confidence', 0), reverse=True)

    return CR_all_findings


def analyze_CR_snapshot(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-level analysis of the dataset

    Args:
        CR_snapshot: Data snapshot dictionary to analyze

    Returns:
        Analysis summary dictionary
    """
    CR_events = CR_snapshot.get('CR_events', [])
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

    return {
        'CR_total_events': CR_total_events,
        'CR_total_markets': CR_total_markets,
        'CR_total_outcomes': CR_total_outcomes,
        'CR_unique_bookmakers': len(CR_bookmakers),
        'CR_bookmaker_list': list(CR_bookmakers),
        'CR_snapshot_timestamp': CR_snapshot.get('CR_timestamp', datetime.now().isoformat()),
        'CR_data_source': CR_snapshot.get('CR_source', 'unknown')
    }


def generate_CR_analysis_summary(CR_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary of findings

    Args:
        CR_findings: List of CR_finding dictionaries

    Returns:
        Summary statistics dictionary
    """
    CR_summary = {
        'CR_total_findings': len(CR_findings),
        'CR_by_type': {},
        'CR_by_confidence': {
            'CR_high': 0,  # > 0.8
            'CR_medium': 0,  # 0.5-0.8
            'CR_low': 0,  # < 0.5
        },
        'CR_by_bookmaker': {},
        'CR_by_event': {}
    }

    for CR_finding in CR_findings:
        # Count by type
        CR_type = CR_finding.get('CR_type', 'unknown')
        CR_summary['CR_by_type'][CR_type] = CR_summary['CR_by_type'].get(CR_type, 0) + 1

        # Count by confidence
        CR_confidence = CR_finding.get('CR_confidence', 0)
        if CR_confidence > 0.8:
            CR_summary['CR_by_confidence']['CR_high'] += 1
        elif CR_confidence > 0.5:
            CR_summary['CR_by_confidence']['CR_medium'] += 1
        else:
            CR_summary['CR_by_confidence']['CR_low'] += 1

        # Count by bookmaker
        CR_bookmakers = CR_finding.get('CR_bookmakers', [])
        for CR_bookmaker in CR_bookmakers:
            CR_summary['CR_by_bookmaker'][CR_bookmaker] = CR_summary['CR_by_bookmaker'].get(CR_bookmaker, 0) + 1

        # Count by event
        CR_event_id = CR_finding.get('CR_event_id', 'unknown')
        CR_summary['CR_by_event'][CR_event_id] = CR_summary['CR_by_event'].get(CR_event_id, 0) + 1

    return CR_summary


def execute_CR_analysis_pipeline(CR_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute complete analysis pipeline.
    Uses LLM agent when a provider+key is configured; falls back to deterministic run.

    Args:
        CR_snapshot: Data snapshot dictionary

    Returns:
        Complete analysis results dictionary including tool_trace and llm_summary
    """
    from packages.llm.factory import get_CR_provider_name

    # 1. Analyze snapshot metadata
    CR_snapshot_analysis = analyze_CR_snapshot(CR_snapshot)

    # 2. Run agent (LLM or deterministic fallback)
    CR_active_provider = get_CR_provider_name()
    CR_tool_trace = []
    CR_llm_summary = ""
    CR_llm_provider = CR_active_provider
    CR_llm_model = ""

    try:
        CR_llm_result = run_CR_llm_agent(CR_snapshot, CR_active_provider)
        CR_findings = CR_llm_result.CR_findings
        CR_tool_trace = [CR_tc.to_dict() for CR_tc in CR_llm_result.CR_tool_trace]
        CR_llm_summary = CR_llm_result.CR_llm_summary
        CR_llm_model = CR_llm_result.CR_model
    except Exception:
        # Hard fallback: deterministic pipeline
        CR_findings = run_CR_agent(CR_snapshot)
        CR_llm_provider = "fallback"

    # 3. Generate findings summary
    CR_findings_summary = generate_CR_analysis_summary(CR_findings)

    # 4. Generate sportsbook rankings
    try:
        from packages.reporting.rankings import generate_CR_sportsbook_rankings
        CR_sportsbook_rankings = generate_CR_sportsbook_rankings(CR_snapshot, CR_findings)
    except Exception:
        CR_sportsbook_rankings = []

    return {
        'CR_snapshot_analysis': CR_snapshot_analysis,
        'CR_findings': CR_findings,
        'CR_findings_summary': CR_findings_summary,
        'CR_sportsbook_rankings': CR_sportsbook_rankings,
        'CR_tool_trace': CR_tool_trace,
        'CR_llm_summary': CR_llm_summary,
        'CR_llm_provider': CR_llm_provider,
        'CR_llm_model': CR_llm_model,
        'CR_pipeline_timestamp': datetime.now().isoformat()
    }

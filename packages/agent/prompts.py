"""
Production LLM prompts for the AtOdds agent.
System prompt drives briefing mode; chat prompt drives follow-up Q&A.
"""

CR_SYSTEM_PROMPT = """You are an odds intelligence agent for a professional sports betting analytics platform.

Your job: analyze sportsbook odds data using deterministic tools, then produce a structured market briefing.

RULES:
- You MUST call tools for ALL calculations — never compute implied probabilities, vig, or edges yourself
- Call tools in this order: CR_detect_stale_lines, CR_detect_arbitrage, CR_detect_outliers, CR_detect_value_edges, CR_compute_best_lines, CR_compute_consensus
- After all tool calls, write the briefing using ONLY the tool results
- Every claim must reference the tool that produced it
- If data is missing or a question is out of scope, say so explicitly — never guess

BRIEFING FORMAT (use this exact structure):
## Market Overview
[Event count, bookmaker count, market count from the data]

## Flagged Anomalies
[Stale lines and outliers with specific bookmakers, markets, and hours/z-scores]

## Top Value Opportunities
[Arbitrage and value edges with the math: implied probabilities and edge percentage]

## Best Available Lines
[Best price per side per event from CR_compute_best_lines results]

## Recommendations
[Actionable summary — which books to use, which to avoid, any urgent flags]"""

CR_CHAT_SYSTEM_PROMPT = """You are an odds analysis assistant answering follow-up questions about a completed market briefing.

RULES:
- Answer ONLY from the briefing and findings provided in the conversation
- You MAY call analysis tools to get fresh data for a specific question
- Never fabricate odds, probabilities, or bookmaker names
- If the question is outside the scope of the current data, say: "That information is not available in the current dataset."
- Keep answers concise and evidence-based"""


def get_CR_system_prompt() -> str:
    return CR_SYSTEM_PROMPT


def get_CR_chat_system_prompt() -> str:
    return CR_CHAT_SYSTEM_PROMPT


def build_CR_analysis_user_message(CR_snapshot: dict) -> str:
    """Build the initial user message for a briefing run."""
    CR_events = CR_snapshot.get("CR_events", [])
    CR_bookmakers = set()
    CR_market_count = 0
    for CR_event in CR_events:
        for CR_market in CR_event.get("CR_markets", []):
            CR_market_count += 1
            CR_bk = CR_market.get("CR_bookmaker", "")
            if CR_bk:
                CR_bookmakers.add(CR_bk)

    import json
    return (
        f"Analyze this odds snapshot and produce the full market briefing.\n\n"
        f"Dataset: {len(CR_events)} events, {CR_market_count} markets, "
        f"{len(CR_bookmakers)} bookmakers ({', '.join(sorted(CR_bookmakers))})\n\n"
        f"Snapshot data:\n{json.dumps(CR_snapshot)}"
    )


def build_CR_chat_context_message(CR_briefing_text: str, CR_findings: list) -> str:
    """Build the context message prepended to chat conversations."""
    import json
    CR_finding_summary = f"{len(CR_findings)} findings from last analysis run"
    return (
        f"Current briefing:\n{CR_briefing_text}\n\n"
        f"Findings summary: {CR_finding_summary}\n"
        f"Findings data:\n{json.dumps(CR_findings[:20])}"  # cap at 20 to stay within context
    )


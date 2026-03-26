"""
Briefing generation with CR_ prefix compliance - convert findings to structured output
"""

from typing import List, Dict, Any
from datetime import datetime
import json

from packages.agent.agent import analyze_CR_snapshot, generate_CR_analysis_summary


def _format_CR_math_proof(CR_finding: Dict[str, Any]) -> str:
    """Return a single-line math proof string for inline display, or empty string."""
    CR_proof = CR_finding.get("CR_math_proof")
    if not CR_proof:
        return ""
    return f"   Math: {CR_proof.get('CR_formula', '')}"


def generate_CR_briefing(
    CR_findings: List[Dict[str, Any]],
    CR_snapshot: Dict[str, Any] = None,
    CR_sportsbook_rankings: List[Dict[str, Any]] = None
) -> str:
    """
    Convert CR_ findings to structured output

    Args:
        CR_findings: List of CR_ finding dictionaries
        CR_snapshot: Optional CR_ snapshot dictionary for context

    Returns:
        Formatted briefing text
    """
    CR_briefing_lines = []

    # Header
    CR_briefing_lines.append("=" * 60)
    CR_briefing_lines.append("CR_ ODDS ANALYSIS BRIEFING")
    CR_briefing_lines.append("=" * 60)
    CR_briefing_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    CR_briefing_lines.append("")

    # Summary
    CR_summary = generate_CR_analysis_summary(CR_findings)
    CR_briefing_lines.append("📊 CR_ SUMMARY")
    CR_briefing_lines.append("-" * 30)
    CR_briefing_lines.append(f"Total Findings: {CR_summary['CR_total_findings']}")

    if CR_summary['CR_by_type']:
        CR_briefing_lines.append("Findings by Type:")
        for CR_finding_type, CR_count in CR_summary['CR_by_type'].items():
            CR_briefing_lines.append(f"  • {CR_finding_type}: {CR_count}")

    if CR_summary['CR_by_confidence']['CR_high'] > 0:
        CR_briefing_lines.append(f"High Confidence (>80%): {CR_summary['CR_by_confidence']['CR_high']}")

    CR_briefing_lines.append("")

    # Top Findings
    CR_briefing_lines.append("🔍 TOP CR_ FINDINGS")
    CR_briefing_lines.append("-" * 30)

    CR_top_findings = CR_findings[:10]  # Show top 10 by confidence
    for CR_i, CR_finding in enumerate(CR_top_findings, 1):
        CR_confidence = CR_finding.get('CR_confidence', 0)
        CR_confidence_bar = "🟢" if CR_confidence > 0.8 else "🟡" if CR_confidence > 0.5 else "🔴"

        CR_type = CR_finding.get('CR_type', 'unknown')
        CR_briefing_lines.append(f"{CR_i}. {CR_confidence_bar} {CR_type.upper()}")
        CR_briefing_lines.append(f"   Event: {CR_finding.get('CR_event_id', 'N/A')}")
        CR_briefing_lines.append(f"   Market: {CR_finding.get('CR_market_name', 'N/A')}")
        CR_briefing_lines.append(f"   Bookmakers: {', '.join(CR_finding.get('CR_bookmakers', []))}")
        CR_briefing_lines.append(f"   Confidence: {CR_confidence:.1%}")
        CR_briefing_lines.append(f"   Description: {CR_finding.get('CR_description', 'N/A')}")

        # Add specific details based on type
        CR_details = CR_finding.get('CR_details', {})
        if CR_type == 'arbitrage' and 'CR_profit_margin' in CR_details:
            CR_briefing_lines.append(f"   Profit Margin: {CR_details['CR_profit_margin']:.2%}")
        elif CR_type == 'value_edge' and 'CR_edge' in CR_details:
            CR_briefing_lines.append(f"   Edge: {CR_details['CR_edge']:.2%}")
        elif CR_type == 'outlier' and 'CR_z_score' in CR_details:
            CR_briefing_lines.append(f"   Z-Score: {CR_details['CR_z_score']:.2f}")

        CR_math_line = _format_CR_math_proof(CR_finding)
        if CR_math_line:
            CR_briefing_lines.append(CR_math_line)

        CR_briefing_lines.append("")

    # Detailed breakdown by type
    if CR_summary['CR_by_type']:
        CR_briefing_lines.append("📈 DETAILED BREAKDOWN")
        CR_briefing_lines.append("-" * 30)

        for CR_finding_type in ['arbitrage', 'value_edge', 'outlier', 'stale_line']:
            if CR_finding_type in CR_summary['CR_by_type']:
                CR_type_findings = [CR_f for CR_f in CR_findings if CR_f.get('CR_type') == CR_finding_type]
                CR_briefing_lines.append(f"\n{CR_finding_type.upper()} ({len(CR_type_findings)} cases)")

                for CR_finding in CR_type_findings[:3]:  # Show top 3 for each type
                    CR_desc = CR_finding.get('CR_description', '')[:80]
                    CR_briefing_lines.append(f"  • {CR_desc}...")

    # Sportsbook quality rankings
    if CR_sportsbook_rankings:
        CR_briefing_lines.append("\n📊 SPORTSBOOK QUALITY RANKINGS")
        CR_briefing_lines.append("-" * 30)
        CR_briefing_lines.append(f"  {'Rank':<5} {'Sportsbook':<18} {'Avg Vig':<10} {'Best Lines':<12} {'Score':<8} {'Verdict'}")
        CR_briefing_lines.append(f"  {'-'*5} {'-'*18} {'-'*10} {'-'*12} {'-'*8} {'-'*12}")
        for CR_r in CR_sportsbook_rankings:
            CR_briefing_lines.append(
                f"  {CR_r['CR_rank']:<5} {CR_r['CR_bookmaker']:<18} "
                f"{CR_r['CR_avg_vig_pct']:<10} {CR_r['CR_best_line_pct']:<12} "
                f"{CR_r['CR_quality_score']:<8} {CR_r['CR_verdict']}"
            )
    elif CR_summary['CR_by_bookmaker']:
        CR_briefing_lines.append("\n🏢 BOOKMAKER ANALYSIS")
        CR_briefing_lines.append("-" * 30)
        CR_sorted_bookmakers = sorted(CR_summary['CR_by_bookmaker'].items(), key=lambda x: x[1], reverse=True)
        for CR_bookmaker, CR_count in CR_sorted_bookmakers[:5]:
            CR_briefing_lines.append(f"  • {CR_bookmaker}: {CR_count} findings")

    # Recommendations
    CR_briefing_lines.append("\n💡 RECOMMENDATIONS")
    CR_briefing_lines.append("-" * 30)

    if CR_summary['CR_by_type'].get('arbitrage', 0) > 0:
        CR_briefing_lines.append("• ARBITRAGE: Immediate action recommended")
        CR_briefing_lines.append("  - Verify odds are still current")
        CR_briefing_lines.append("  - Calculate optimal stake distribution")
        CR_briefing_lines.append("  - Execute quickly before odds change")

    if CR_summary['CR_by_type'].get('value_edge', 0) > 0:
        CR_briefing_lines.append("• VALUE EDGES: Consider for long-term strategy")
        CR_briefing_lines.append("  - Focus on edges >10% for better risk/reward")
        CR_briefing_lines.append("  - Track performance over time")

    if CR_summary['CR_by_type'].get('stale_line', 0) > 0:
        CR_briefing_lines.append("• STALE LINES: Data quality issue")
        CR_briefing_lines.append("  - Update data sources")
        CR_briefing_lines.append("  - Implement automated freshness checks")

    if CR_summary['CR_by_type'].get('outlier', 0) > 0:
        CR_briefing_lines.append("• OUTLIERS: Investigate for errors or opportunities")
        CR_briefing_lines.append("  - Verify data accuracy")
        CR_briefing_lines.append("  - Some outliers may be genuine mispricings")

    # Footer
    CR_briefing_lines.append("\n" + "=" * 60)
    CR_briefing_lines.append("END OF CR_ BRIEFING")
    CR_briefing_lines.append("=" * 60)

    return "\n".join(CR_briefing_lines)


def generate_CR_json_briefing(CR_findings: List[Dict[str, Any]], CR_snapshot: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate structured JSON briefing with CR_ prefix

    Args:
        CR_findings: List of CR_ finding dictionaries
        CR_snapshot: Optional CR_ snapshot dictionary for context

    Returns:
        Structured CR_ briefing data
    """
    CR_summary = generate_CR_analysis_summary(CR_findings)

    return {
        'CR_metadata': {
            'CR_generated_at': datetime.now().isoformat(),
            'CR_total_findings': len(CR_findings),
            'CR_version': '1.0'
        },
        'CR_summary': CR_summary,
        'CR_findings': CR_findings,
        'CR_recommendations': generate_CR_recommendations(CR_summary)
    }


def generate_CR_recommendations(CR_summary: Dict[str, Any]) -> List[str]:
    """Generate actionable CR_ recommendations"""
    CR_recommendations = []

    if CR_summary['CR_by_type'].get('arbitrage', 0) > 0:
        CR_recommendations.append("Execute arbitrage opportunities immediately")

    if CR_summary['CR_by_type'].get('value_edge', 0) > 3:
        CR_recommendations.append("Multiple value edges detected - consider systematic approach")

    if CR_summary['CR_by_type'].get('stale_line', 0) > 0:
        CR_recommendations.append("Improve data freshness monitoring")

    if CR_summary['CR_by_confidence']['CR_high'] > 5:
        CR_recommendations.append("High number of high-confidence findings - market may be inefficient")

    if not CR_recommendations:
        CR_recommendations.append("No immediate action required - monitor for changes")

    return CR_recommendations

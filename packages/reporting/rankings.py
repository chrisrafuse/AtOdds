"""
Sportsbook quality rankings — scores each bookmaker by vig, best-line frequency,
freshness, and outlier count. No LLM dependency.
"""

from typing import List, Dict, Any

from packages.core_engine.odds_math import compute_CR_vig
from packages.core_engine.consensus import compute_CR_best_lines


def generate_CR_sportsbook_rankings(
    CR_snapshot: Dict[str, Any],
    CR_findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Rank each bookmaker by composite quality score.

    Score formula (0–100):
      - avg_vig component    (40 pts): lower vig = higher score
      - best_line frequency  (40 pts): how often this book has the best price
      - freshness            (10 pts): inverse of stale_count / total_markets
      - accuracy             (10 pts): inverse of outlier_count / total_markets

    Returns:
        List of ranking dicts sorted by CR_quality_score descending
    """
    CR_events = CR_snapshot.get("CR_events", [])

    # Collect per-bookmaker stats
    CR_stats: Dict[str, Dict[str, Any]] = {}
    CR_total_markets = 0

    for CR_event in CR_events:
        CR_markets = CR_event.get("CR_markets", [])

        # Group by market name for best-line detection
        CR_market_groups: Dict[str, List[Dict]] = {}
        for CR_market in CR_markets:
            CR_bk = CR_market.get("CR_bookmaker", "")
            CR_mname = CR_market.get("CR_name", "")
            if not CR_bk:
                continue

            if CR_bk not in CR_stats:
                CR_stats[CR_bk] = {
                    "CR_vig_sum": 0.0,
                    "CR_vig_count": 0,
                    "CR_best_line_count": 0,
                    "CR_market_count": 0,
                }

            CR_stats[CR_bk]["CR_market_count"] += 1
            CR_total_markets += 1

            # Vig per market
            CR_outcomes = CR_market.get("CR_outcomes", [])
            CR_prices = [o.get("CR_price") for o in CR_outcomes if o.get("CR_price") is not None]
            if len(CR_prices) >= 2:
                try:
                    CR_vig = compute_CR_vig([int(p) for p in CR_prices])
                    CR_stats[CR_bk]["CR_vig_sum"] += CR_vig
                    CR_stats[CR_bk]["CR_vig_count"] += 1
                except (ValueError, TypeError):
                    pass

            if CR_mname not in CR_market_groups:
                CR_market_groups[CR_mname] = []
            CR_market_groups[CR_mname].append(CR_market)

        # Best-line counts: which bookmaker had the best price per outcome
        for CR_mname, CR_grouped in CR_market_groups.items():
            if len(CR_grouped) < 2:
                continue
            try:
                CR_best = compute_CR_best_lines(CR_grouped)
                for _, (CR_winner_bk, _) in CR_best.items():
                    if CR_winner_bk in CR_stats:
                        CR_stats[CR_winner_bk]["CR_best_line_count"] += 1
            except Exception:
                pass

    # Count stale and outlier findings per bookmaker
    CR_stale_counts: Dict[str, int] = {}
    CR_outlier_counts: Dict[str, int] = {}
    for CR_finding in CR_findings:
        CR_ftype = CR_finding.get("CR_type", "")
        for CR_bk in CR_finding.get("CR_bookmakers", []):
            if CR_ftype == "stale_line":
                CR_stale_counts[CR_bk] = CR_stale_counts.get(CR_bk, 0) + 1
            elif CR_ftype == "outlier":
                CR_outlier_counts[CR_bk] = CR_outlier_counts.get(CR_bk, 0) + 1

    # Build ranked list
    CR_rankings = []
    for CR_bk, CR_s in CR_stats.items():
        CR_total = CR_s["CR_market_count"] or 1
        CR_avg_vig = (CR_s["CR_vig_sum"] / CR_s["CR_vig_count"]) if CR_s["CR_vig_count"] > 0 else 0.05
        # best_line_count counts per-outcome wins; cap at 1.0 relative to markets
        CR_best_freq = min(CR_s["CR_best_line_count"] / CR_total, 1.0)
        CR_stale_rate = CR_stale_counts.get(CR_bk, 0) / CR_total
        CR_outlier_rate = CR_outlier_counts.get(CR_bk, 0) / CR_total

        # Composite quality score (0–100)
        CR_quality_score = min(100.0, (
            (1 - min(CR_avg_vig, 0.15) / 0.15) * 40
            + CR_best_freq * 40
            + (1 - min(CR_stale_rate, 1.0)) * 10
            + (1 - min(CR_outlier_rate, 1.0)) * 10
        ))

        CR_verdict = (
            "Recommended" if CR_quality_score >= 65
            else "Avoid" if CR_quality_score < 35
            else "Average"
        )

        CR_rankings.append({
            "CR_bookmaker": CR_bk,
            "CR_avg_vig": round(CR_avg_vig, 4),
            "CR_avg_vig_pct": f"{CR_avg_vig * 100:.2f}%",
            "CR_best_line_count": CR_s["CR_best_line_count"],
            "CR_best_line_pct": f"{CR_best_freq * 100:.1f}%",
            "CR_stale_count": CR_stale_counts.get(CR_bk, 0),
            "CR_outlier_count": CR_outlier_counts.get(CR_bk, 0),
            "CR_market_count": CR_s["CR_market_count"],
            "CR_quality_score": round(CR_quality_score, 1),
            "CR_verdict": CR_verdict,
        })

    CR_rankings.sort(key=lambda r: r["CR_quality_score"], reverse=True)
    for CR_i, CR_r in enumerate(CR_rankings, 1):
        CR_r["CR_rank"] = CR_i

    return CR_rankings

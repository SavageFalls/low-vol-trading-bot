from __future__ import annotations

import json
from pathlib import Path

from app.models import DailyResearchReport


def render_markdown(report: DailyResearchReport) -> str:
    lines = [
        "## DAILY HEDGE FUND BRIEFING",
        "",
        "### Macro Regime",
        f"- Regime: **{report.macro_regime}**",
        f"- Confidence: **{report.macro_confidence:.2f}**",
        f"- View: {report.macro_explanation}",
        "",
        "### Top Conviction Ideas (MAX 3)",
        "",
    ]

    if not report.opportunities:
        lines.append("No high-conviction opportunities passed strict filtering today.")

    for opp in report.opportunities[:3]:
        lines.extend(
            [
                f"Ticker: {opp.ticker}",
                f"Rating: {opp.rating}",
                f"Confidence: {opp.confidence:.2f}",
                "",
                f"Macro View: {opp.macro_view}",
                f"Positioning & Flows: {opp.positioning_flows}",
                f"Sentiment: {opp.sentiment}",
                f"Fundamentals: {opp.fundamentals}",
                f"Technical Levels: {opp.key_levels}",
                f"Thesis: {opp.thesis}",
                "",
                "Decision Trace:",
                opp.decision_trace,
                "",
                "---",
                "",
            ]
        )
    return "\n".join(lines)


def persist_report(report: DailyResearchReport, reports_dir: Path) -> tuple[Path, Path]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.created_at.strftime("%Y%m%d_%H%M%S")
    md_path = reports_dir / f"daily_report_{stamp}.md"
    json_path = reports_dir / f"daily_report_{stamp}.json"

    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    return md_path, json_path

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Dict


def write_report(report_dir: str, run_type: str, ideas: List[Dict], macro_summary: Dict) -> str:
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(report_dir) / f"briefing_{run_type}_{ts}.md"

    lines = [
        f"# Daily Hedge Fund Briefing ({run_type})",
        f"Generated (UTC): {datetime.utcnow().isoformat()}",
        "",
        "## Macro Regime",
        f"- Regime: **{macro_summary['regime']}**",
        f"- Macro Score: **{macro_summary['score']:.2f}**",
        f"- Summary: {macro_summary['summary']}",
        "",
        "## Top Opportunities",
    ]

    for idea in ideas:
        lines += [
            f"### {idea['ticker']}",
            f"- **Rating:** {idea['rating']}  ",
            f"- **Confidence:** {idea['confidence']:.2f}  ",
            f"- **Macro View:** {idea['macro_summary']}  ",
            f"- **Positioning & Flows:** {idea['positioning_summary']}  ",
            f"- **Sentiment:** {idea['sentiment_summary']}  ",
            f"- **Fundamentals:** {idea['fundamental_summary']}  ",
            (
                "- **Key Levels:** "
                f"Last={idea['levels'].get('last')}, MA50={idea['levels'].get('ma50')}, "
                f"MA200={idea['levels'].get('ma200')}, 52wH={idea['levels'].get('52w_high')}, "
                f"52wL={idea['levels'].get('52w_low')}  "
            ),
            f"- **Thesis:** {idea['thesis']}  ",
            f"- **Decision Trace:** {idea['rationale']}  ",
            "",
        ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return str(path)

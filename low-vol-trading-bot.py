from __future__ import annotations

import glob
import json
from pathlib import Path

import pandas as pd
import streamlit as st

REPORTS_DIR = Path("reports")

st.set_page_config(page_title="Daily Hedge Fund Briefing", layout="wide")
st.title("📈 AI Research Analyst Dashboard")
st.caption("Institutional-format autonomous daily briefing viewer.")

report_files = sorted(glob.glob(str(REPORTS_DIR / "daily_report_*.json")), reverse=True)
if not report_files:
    st.warning("No reports yet. Run `python main.py run-once` or `python -m app.scheduler` first.")
    st.stop()

selected = st.selectbox("Select report", report_files)
with open(selected, "r", encoding="utf-8") as f:
    report = json.load(f)

st.subheader("Macro Regime")
st.write(f"Regime: **{report.get('macro_regime', 'unknown')}**")
st.write(f"Confidence: **{report.get('macro_confidence', 0):.2f}**")
st.write(report.get("macro_explanation", "No macro commentary."))

rows = []
for opp in report.get("opportunities", []):
    rows.append(
        {
            "Ticker": opp["ticker"],
            "Rating": opp["rating"],
            "Confidence": round(opp["confidence"], 3),
            "Composite": round(opp["composite_score"], 3),
        }
    )

df = pd.DataFrame(rows)
if df.empty:
    st.info("No high-conviction ideas in this report.")
else:
    st.dataframe(df, use_container_width=True)

for opp in report.get("opportunities", []):
    with st.expander(f"{opp['ticker']} — {opp['rating']}"):
        st.markdown(f"**Macro View:** {opp['macro_view']}")
        st.markdown(f"**Positioning & Flows:** {opp['positioning_flows']}")
        st.markdown(f"**Sentiment:** {opp['sentiment']}")
        st.markdown(f"**Fundamentals:** {opp['fundamentals']}")
        st.markdown(f"**Technical Levels:** {opp['key_levels']}")
        st.markdown(f"**Thesis:** {opp['thesis']}")
        st.code(opp.get("decision_trace", ""))

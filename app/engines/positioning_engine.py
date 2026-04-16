from __future__ import annotations

import numpy as np
import pandas as pd


class PositioningEngine:
    def analyze(self, cot_df: pd.DataFrame | None, insider_df: pd.DataFrame | None) -> dict:
        score = 0.0
        notes = []

        if cot_df is not None and not cot_df.empty:
            net_cols = [c for c in cot_df.columns if "Noncommercial Positions-Long" in c or "Noncommercial Long" in c]
            short_cols = [c for c in cot_df.columns if "Noncommercial Positions-Short" in c or "Noncommercial Short" in c]
            if net_cols and short_cols:
                latest = cot_df.iloc[-1]
                net = float(latest[net_cols[0]]) - float(latest[short_cols[0]])
                if net < 0:
                    score += 0.15
                    notes.append("Spec positioning is light/short (contrarian upside).")
                else:
                    score -= 0.1
                    notes.append("Spec positioning already long.")

        if insider_df is not None and not insider_df.empty and insider_df.shape[1] > 8:
            try:
                price_col = [c for c in insider_df.columns if "Price" in str(c)][0]
                qty_col = [c for c in insider_df.columns if "Qty" in str(c) or "Shares" in str(c)][0]
                txn_col = [c for c in insider_df.columns if "Trade Type" in str(c) or "Type" in str(c)][0]
                amount = pd.to_numeric(insider_df[price_col], errors="coerce") * pd.to_numeric(
                    insider_df[qty_col], errors="coerce"
                )
                buys = amount[insider_df[txn_col].astype(str).str.contains("P - Purchase", na=False)].sum()
                sells = amount[insider_df[txn_col].astype(str).str.contains("S - Sale", na=False)].sum()
                if buys > sells:
                    score += 0.2
                    notes.append("Insider buying outweighs selling.")
                elif sells > buys * 2:
                    score -= 0.2
                    notes.append("Heavy insider selling pressure.")
            except Exception:
                notes.append("Insider parsing unavailable; neutral positioning weight.")

        score = float(np.clip(score, -1, 1))
        return {"score": score, "summary": " ".join(notes) if notes else "No strong positioning edge."}

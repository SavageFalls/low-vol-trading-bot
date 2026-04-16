from __future__ import annotations

import numpy as np
import pandas as pd

from app.models import EngineSignal


class PositioningEngine:
    ETF_PROXY = ["SPY", "QQQ", "IWM", "XLF", "XLK"]

    @staticmethod
    def _net_cot_score(cot_df: pd.DataFrame) -> float | None:
        if cot_df.empty or "Market_and_Exchange_Names" not in cot_df.columns:
            return None
        mapped = cot_df[cot_df["Market_and_Exchange_Names"].str.contains("NASDAQ|S&P|DJIA", case=False, na=False)]
        if mapped.empty:
            return None
        row = mapped.iloc[-1]
        long_col = [c for c in mapped.columns if "Asset_Mgr_Positions_Long_All" in c]
        short_col = [c for c in mapped.columns if "Asset_Mgr_Positions_Short_All" in c]
        if not long_col or not short_col:
            return None
        long_val, short_val = float(row[long_col[0]]), float(row[short_col[0]])
        return (long_val - short_val) / max(1.0, long_val + short_val)

    @staticmethod
    def _insider_score(insider_df: pd.DataFrame) -> float | None:
        if insider_df.empty:
            return None
        cols = insider_df.columns
        if not any("Value" in c for c in cols):
            return None
        value_col = [c for c in cols if "Value" in c][0]
        x = insider_df.copy()
        x[value_col] = x[value_col].astype(str).str.replace("$", "", regex=False).str.replace(",", "")
        x[value_col] = pd.to_numeric(x[value_col], errors="coerce")
        buys = x[x.astype(str).apply(lambda s: s.str.contains("P - Purchase", na=False)).any(axis=1)]
        sells = x[x.astype(str).apply(lambda s: s.str.contains("S - Sale", na=False)).any(axis=1)]
        buy_val = float(buys[value_col].sum()) if not buys.empty else 0.0
        sell_val = float(sells[value_col].sum()) if not sells.empty else 0.0
        return (buy_val - sell_val) / max(1.0, buy_val + sell_val)

    @staticmethod
    def _etf_flow_proxy_score(etf_prices: pd.DataFrame, etf_volumes: pd.DataFrame) -> float | None:
        if etf_prices.empty or etf_volumes.empty:
            return None
        tickers = [t for t in etf_prices.columns if t in etf_volumes.columns]
        if not tickers:
            return None
        scores = []
        for t in tickers:
            p = etf_prices[t].dropna()
            v = etf_volumes[t].dropna()
            if len(p) < 40 or len(v) < 40:
                continue
            ret5 = p.iloc[-1] / p.iloc[-6] - 1
            dv = (p * v).dropna()
            z = (dv.iloc[-1] - dv.iloc[-20:].mean()) / (dv.iloc[-20:].std() + 1e-9)
            scores.append(np.tanh(1.4 * ret5) * np.tanh(z / 2.5))
        return float(np.mean(scores)) if scores else None

    @staticmethod
    def _unusual_volume_score(ticker: str, prices: pd.DataFrame, volumes: pd.DataFrame) -> float | None:
        if ticker not in prices.columns or ticker not in volumes.columns:
            return None
        p = prices[ticker].dropna()
        v = volumes[ticker].dropna()
        if len(p) < 30 or len(v) < 30:
            return None
        v_ratio = float(v.iloc[-1] / max(1.0, v.iloc[-20:].mean()))
        ret1 = float(p.iloc[-1] / p.iloc[-2] - 1)
        if v_ratio < 1.4:
            return 0.0
        return float(np.clip(np.sign(ret1) * min((v_ratio - 1.0) / 2.0, 1.0), -1, 1))

    def analyze(
        self,
        ticker: str,
        cot_df: pd.DataFrame,
        insider_df: pd.DataFrame,
        prices: pd.DataFrame,
        volumes: pd.DataFrame,
        etf_prices: pd.DataFrame,
        etf_volumes: pd.DataFrame,
    ) -> EngineSignal:
        cot = self._net_cot_score(cot_df)
        insider = self._insider_score(insider_df)
        etf_flow = self._etf_flow_proxy_score(etf_prices, etf_volumes)
        unusual_vol = self._unusual_volume_score(ticker, prices, volumes)

        components = {"cot": cot, "insider": insider, "etf_flow": etf_flow, "unusual_volume": unusual_vol}
        available = {k: v for k, v in components.items() if v is not None}
        missing_count = len(components) - len(available)

        if not available:
            return EngineSignal(
                score=-0.2,
                confidence=0.2,
                summary="Positioning data unknown: COT/insider/flow/volume unavailable.",
                evidence={"state": "unknown", "missing": len(components)},
            )

        weights = {"cot": 0.35, "insider": 0.30, "etf_flow": 0.20, "unusual_volume": 0.15}
        used_weight = sum(weights[k] for k in available)
        raw = sum(weights[k] * available[k] for k in available) / used_weight
        data_penalty = 0.12 * missing_count
        score = float(np.clip(raw - data_penalty, -1, 1))

        if score > 0.25:
            state = "accumulation"
        elif score < -0.25:
            state = "distribution"
        else:
            state = "neutral"

        confidence = float(np.clip(0.45 + 0.12 * len(available) - 0.08 * missing_count, 0.2, 0.85))
        summary = (
            f"State={state}; cot={cot if cot is not None else 'n/a'}, insider={insider if insider is not None else 'n/a'}, "
            f"etf_flow_proxy={etf_flow if etf_flow is not None else 'n/a'}, unusual_volume={unusual_vol if unusual_vol is not None else 'n/a'}"
        )
        return EngineSignal(score=score, confidence=confidence, summary=summary, evidence={**available, "state": state})

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
from fredapi import Fred


class MacroDataClient:
    SERIES = {
        "fed_funds": "FEDFUNDS",
        "cpi_yoy_proxy": "CPIAUCSL",
        "unemployment": "UNRATE",
        "financial_conditions": "NFCI",
        "m2": "M2SL",
        "yield_10y": "DGS10",
        "yield_2y": "DGS2",
    }

    def __init__(self, fred_api_key: str | None):
        self.fred = Fred(api_key=fred_api_key) if fred_api_key else None

    def fetch_macro_snapshot(self) -> dict:
        if not self.fred:
            return {}

        end = datetime.utcnow().date()
        start = end - timedelta(days=365 * 3)
        raw = {}
        for key, series_id in self.SERIES.items():
            s = self.fred.get_series(series_id, observation_start=start, observation_end=end)
            s = pd.to_numeric(s, errors="coerce").dropna()
            raw[key] = s

        cpi = raw["cpi_yoy_proxy"]
        cpi_yoy = (cpi.iloc[-1] / cpi.shift(12).dropna().iloc[-1] - 1) * 100 if len(cpi) > 12 else 0.0
        curve = float(raw["yield_10y"].iloc[-1] - raw["yield_2y"].iloc[-1])
        m2_growth = (
            (raw["m2"].iloc[-1] / raw["m2"].shift(12).dropna().iloc[-1] - 1) * 100 if len(raw["m2"]) > 12 else 0.0
        )
        fed_6m = float(raw["fed_funds"].iloc[-1] - raw["fed_funds"].shift(6).dropna().iloc[-1]) if len(raw["fed_funds"]) > 6 else 0.0

        return {
            "fed_funds": float(raw["fed_funds"].iloc[-1]),
            "fed_funds_6m_delta": fed_6m,
            "cpi_yoy": float(cpi_yoy),
            "unemployment": float(raw["unemployment"].iloc[-1]),
            "financial_conditions": float(raw["financial_conditions"].iloc[-1]),
            "yield_curve_10y_2y": curve,
            "m2_growth": float(m2_growth),
        }

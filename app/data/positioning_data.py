from __future__ import annotations

from io import StringIO

import pandas as pd
import requests


class PositioningDataClient:
    CFTC_FIN_URL = "https://www.cftc.gov/files/dea/history/fut_fin_txt_2025.zip"
    OPEN_INSIDER_URL = "http://openinsider.com/screener?s={ticker}&o=&pl=&ph=&ll=&lh=&fd=90&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sicMin=&sicMax=&sortcol=0&cnt=100&page=1"

    def fetch_cot_financial_futures(self) -> pd.DataFrame:
        # CFTC publishes yearly zip archives. We parse latest available bundle by URL.
        resp = requests.get(self.CFTC_FIN_URL, timeout=30)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.content.decode("latin1")), low_memory=False)
        # If decode/read fails for an environment, caller should handle and use neutral score.
        return df

    def fetch_openinsider(self, ticker: str) -> pd.DataFrame:
        url = self.OPEN_INSIDER_URL.format(ticker=ticker)
        try:
            tables = pd.read_html(url)
        except ValueError:
            return pd.DataFrame()
        if not tables:
            return pd.DataFrame()
        return tables[-1]

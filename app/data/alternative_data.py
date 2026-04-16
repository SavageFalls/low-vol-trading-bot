from __future__ import annotations

from io import StringIO
from urllib.request import urlopen

import pandas as pd
import requests


class AlternativeDataClient:
    COT_URL = "https://www.cftc.gov/dea/newcot/FinFutWk.txt"
    OPEN_INSIDER_URL = "http://openinsider.com/latest-insider-trading"

    def fetch_cot_financial_futures(self) -> pd.DataFrame:
        content = urlopen(self.COT_URL, timeout=20).read().decode("utf-8", errors="ignore")
        lines = [line for line in content.splitlines() if line.strip()]
        if not lines:
            return pd.DataFrame()
        df = pd.read_csv(StringIO("\n".join(lines)), sep=",", engine="python")
        return df

    def fetch_openinsider(self) -> pd.DataFrame:
        resp = requests.get(self.OPEN_INSIDER_URL, timeout=20)
        resp.raise_for_status()
        tables = pd.read_html(resp.text)
        if not tables:
            return pd.DataFrame()
        table = tables[0]
        table.columns = [str(c).strip() for c in table.columns]
        return table

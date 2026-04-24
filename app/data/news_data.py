from __future__ import annotations

from typing import Dict, List
from xml.etree import ElementTree

import requests


class NewsClient:
    def fetch_rss(self, ticker: str, limit: int = 20) -> List[Dict]:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
        except Exception:
            return []

        items: List[Dict] = []
        try:
            root = ElementTree.fromstring(resp.content)
        except ElementTree.ParseError:
            return []

        for item in root.findall(".//item")[:limit]:
            items.append(
                {
                    "title": (item.findtext("title") or "").strip(),
                    "summary": (item.findtext("description") or "").strip(),
                    "published": (item.findtext("pubDate") or "").strip(),
                    "link": (item.findtext("link") or "").strip(),
                }
            )
        return items

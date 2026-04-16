from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

import feedparser


class NewsClient:
    RSS_SOURCES = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
        "https://www.marketwatch.com/rss/topstories",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ]

    def fetch_news_for_ticker(self, ticker: str, days: int = 3) -> List[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        items: List[dict] = []
        for source in self.RSS_SOURCES:
            url = source.format(ticker=ticker)
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = None
                if getattr(entry, "published_parsed", None):
                    published = datetime(*entry.published_parsed[:6])
                if published and published < cutoff:
                    continue
                items.append(
                    {
                        "title": getattr(entry, "title", ""),
                        "summary": getattr(entry, "summary", ""),
                        "link": getattr(entry, "link", ""),
                        "published": published.isoformat() if published else "",
                    }
                )
        return items

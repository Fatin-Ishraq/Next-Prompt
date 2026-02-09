"""
RSS Feed Fetcher Module
Fetches and parses RSS feeds from curated tech sources.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import hashlib

from config import Config


class RSSFetcher:
    """Fetches and processes RSS feeds."""
    
    def __init__(self, genre: str = None):
        self.genre = genre or Config.GENRE
        self.feeds = Config.get_feeds(self.genre)
    
    def fetch_all(self, max_age_hours: int = 24) -> List[Dict]:
        """
        Fetch all RSS feeds and return normalized articles.
        
        Args:
            max_age_hours: Maximum age of articles to include (default 24h)
            
        Returns:
            List of article dictionaries with normalized structure
        """
        all_articles = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        for feed_url in self.feeds:
            try:
                articles = self._fetch_feed(feed_url, cutoff_time)
                all_articles.extend(articles)
                print(f"✅ Fetched {len(articles)} articles from {self._get_source_name(feed_url)}")
            except Exception as e:
                print(f"⚠️  Error fetching {feed_url}: {e}")
        
        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)
        
        # Sort by published date (newest first)
        unique_articles.sort(key=lambda x: x["published"], reverse=True)
        
        print(f"\n📊 Total: {len(unique_articles)} unique articles from {len(self.feeds)} feeds")
        return unique_articles
    
    def _fetch_feed(self, feed_url: str, cutoff_time: datetime) -> List[Dict]:
        """Fetch a single RSS feed and return normalized articles."""
        feed = feedparser.parse(feed_url)
        articles = []
        
        for entry in feed.entries:
            try:
                # Parse published date
                published = self._parse_date(entry)
                if published and published < cutoff_time:
                    continue  # Skip old articles
                
                # Generate unique ID
                article_id = hashlib.md5(entry.link.encode()).hexdigest()[:12]
                
                # Extract summary/description
                summary = ""
                if hasattr(entry, "summary"):
                    summary = entry.summary
                elif hasattr(entry, "description"):
                    summary = entry.description
                
                # Clean HTML from summary
                summary = self._clean_html(summary)[:500]
                
                article = {
                    "id": article_id,
                    "title": entry.title,
                    "url": entry.link,
                    "summary": summary,
                    "source": self._get_source_name(feed_url),
                    "published": published or datetime.now(timezone.utc),
                    "genre": self.genre,
                }
                articles.append(article)
                
            except Exception as e:
                print(f"   ⚠️  Error parsing entry: {e}")
                continue
        
        return articles
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse published date from RSS entry."""
        # Try published_parsed first
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6])
                return dt.replace(tzinfo=timezone.utc)
            except:
                pass
        
        # Try updated_parsed
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                dt = datetime(*entry.updated_parsed[:6])
                return dt.replace(tzinfo=timezone.utc)
            except:
                pass
        
        # For arXiv and other feeds, try parsing published string
        if hasattr(entry, "published"):
            try:
                from email.utils import parsedate_to_datetime
                dt = parsedate_to_datetime(entry.published)
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
            except:
                pass
        
        # Return current time as fallback (will be filtered if too old)
        return datetime.now(timezone.utc)
    
    def _get_source_name(self, feed_url: str) -> str:
        """Extract source name from feed URL."""
        source_map = {
            "techcrunch.com": "TechCrunch",
            "theverge.com": "The Verge",
            "arstechnica.com": "Ars Technica",
            "wired.com": "Wired",
            "hnrss.org": "Hacker News",
            "technologyreview.com": "MIT Tech Review",
            "arxiv.org": "arXiv",
        }
        
        for domain, name in source_map.items():
            if domain in feed_url:
                return name
        
        return feed_url.split("/")[2]
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()


if __name__ == "__main__":
    # Test RSS fetching
    print("🔄 Testing RSS Fetcher...")
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all(max_age_hours=48)  # Get last 48 hours for testing
    
    print(f"\n📰 Sample articles:")
    for article in articles[:5]:
        print(f"\n   📌 {article['title']}")
        print(f"      Source: {article['source']}")
        print(f"      URL: {article['url'][:60]}...")

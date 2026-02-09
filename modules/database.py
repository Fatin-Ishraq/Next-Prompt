"""
Supabase Database Module
Handles persistence for posted articles and AI context/memory.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from typing import List, Dict, Optional
from supabase import create_client, Client

from config import Config


class Database:
    """Supabase database interface for AutoPost."""
    
    def __init__(self):
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    
    # ==================== Posts Table ====================
    
    def is_already_posted(self, url: str) -> bool:
        """Check if an article URL has already been posted."""
        try:
            result = self.client.table("posts").select("id").eq("url", url).execute()
            return len(result.data) > 0
        except Exception as e:
            print(f"⚠️  Database error checking post: {e}")
            return False
    
    def save_post(self, post_data: Dict) -> Optional[str]:
        """
        Save a posted article to the database.
        
        Args:
            post_data: Dictionary with keys: url, title, caption, image_url, fb_post_id, genre
            
        Returns:
            The ID of the created record, or None if failed
        """
        try:
            record = {
                "url": post_data.get("url"),
                "title": post_data.get("title"),
                "caption": post_data.get("caption"),
                "image_url": post_data.get("image_url"),
                "fb_post_id": post_data.get("fb_post_id"),
                "genre": post_data.get("genre", Config.GENRE),
                "posted_at": datetime.now(timezone.utc).isoformat(),
            }
            
            result = self.client.table("posts").insert(record).execute()
            if result.data:
                print(f"✅ Saved post to database: {post_data.get('title', '')[:50]}...")
                return result.data[0].get("id")
            return None
        except Exception as e:
            print(f"⚠️  Database error saving post: {e}")
            return None
    
    def get_recent_posts(self, limit: int = 20, genre: str = None) -> List[Dict]:
        """Get recent posts for context."""
        try:
            query = self.client.table("posts").select("*").order("posted_at", desc=True).limit(limit)
            if genre:
                query = query.eq("genre", genre)
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"⚠️  Database error getting recent posts: {e}")
            return []
    
    def get_posted_urls(self, limit: int = 100) -> set:
        """Get set of recently posted URLs to avoid duplicates."""
        try:
            result = self.client.table("posts").select("url").order("posted_at", desc=True).limit(limit).execute()
            return {post["url"] for post in result.data}
        except Exception as e:
            print(f"⚠️  Database error getting posted URLs: {e}")
            return set()
    
    # ==================== Context Table ====================
    
    def get_context(self, key: str) -> Optional[str]:
        """Get a context value by key."""
        try:
            result = self.client.table("context").select("value").eq("key", key).execute()
            if result.data:
                return result.data[0].get("value")
            return None
        except Exception as e:
            print(f"⚠️  Database error getting context: {e}")
            return None
    
    def set_context(self, key: str, value: str) -> bool:
        """Set or update a context value."""
        try:
            # Try to update first
            existing = self.client.table("context").select("id").eq("key", key).execute()
            
            if existing.data:
                # Update existing
                self.client.table("context").update({
                    "value": value,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("key", key).execute()
            else:
                # Insert new
                self.client.table("context").insert({
                    "key": key,
                    "value": value,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
            
            return True
        except Exception as e:
            print(f"⚠️  Database error setting context: {e}")
            return False
    
    def get_all_context(self) -> Dict[str, str]:
        """Get all context key-value pairs."""
        try:
            result = self.client.table("context").select("key, value").execute()
            return {item["key"]: item["value"] for item in result.data}
        except Exception as e:
            print(f"⚠️  Database error getting all context: {e}")
            return {}


# SQL to create tables in Supabase:
CREATE_TABLES_SQL = """
-- Posts table to track all posted articles
CREATE TABLE IF NOT EXISTS posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    caption TEXT,
    image_url TEXT,
    fb_post_id TEXT,
    genre TEXT DEFAULT 'tech',
    posted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Context table for AI memory
CREATE TABLE IF NOT EXISTS context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(url);
CREATE INDEX IF NOT EXISTS idx_posts_posted_at ON posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_context_key ON context(key);
"""


if __name__ == "__main__":
    print("🔄 Testing Supabase Database...")

    
    try:
        db = Database()
        
        # Test connection
        posts = db.get_recent_posts(limit=5)
        print(f"\n✅ Connection successful! Found {len(posts)} recent posts.")
        
        # Show posted URLs
        urls = db.get_posted_urls(limit=10)
        print(f"📊 {len(urls)} URLs in post history")
        
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print("\n⚠️  Make sure to create the tables using the SQL above!")

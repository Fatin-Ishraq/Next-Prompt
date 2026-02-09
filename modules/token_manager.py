"""
Facebook Token Manager
Handles automatic token exchange and refresh for Facebook API.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from typing import Optional

from config import Config
from modules.database import Database


class TokenManager:
    """Manages Facebook access tokens with automatic refresh."""
    
    def __init__(self):
        self.app_id = Config.FB_APP_ID
        self.app_secret = Config.FB_APP_SECRET
        self.page_id = Config.FB_PAGE_ID
        self.db = Database()
    
    def get_page_token(self) -> Optional[str]:
        """
        Get a valid page access token.
        First checks database for stored token, then validates it.
        
        Returns:
            Valid page access token, or None if unavailable
        """
        # Check for stored page token
        stored_token = self.db.get_context("fb_page_token")
        
        if stored_token and self._is_token_valid(stored_token):
            print("✅ Using stored page token")
            return stored_token
        
        # Try to get from stored long-lived user token
        user_token = self.db.get_context("fb_long_lived_token")
        if user_token:
            print("🔄 Refreshing page token from user token...")
            page_token = self._fetch_page_token(user_token)
            if page_token:
                self.db.set_context("fb_page_token", page_token)
                return page_token
        
        # Fallback to env variable
        env_token = Config.FB_ACCESS_TOKEN
        if env_token:
            print("⚠️  Using token from environment (may expire)")
            return env_token
        
        print("❌ No valid Facebook token available")
        return None
    
    def setup_tokens(self, short_lived_token: str) -> bool:
        """
        One-time setup: Exchange short-lived token for permanent page token.
        
        Args:
            short_lived_token: Short-lived user token from Graph Explorer
            
        Returns:
            True if setup successful
        """
        print("\n🔐 Facebook Token Setup")
        print("=" * 40)
        
        # Step 1: Exchange for long-lived user token
        print("\n1️⃣ Exchanging for long-lived user token...")
        long_lived_token = self._exchange_for_long_lived(short_lived_token)
        if not long_lived_token:
            return False
        
        self.db.set_context("fb_long_lived_token", long_lived_token)
        print("   ✅ Long-lived token saved (valid ~60 days)")
        
        # Step 2: Get page access token
        print("\n2️⃣ Fetching page access token...")
        page_token = self._fetch_page_token(long_lived_token)
        if not page_token:
            return False
        
        self.db.set_context("fb_page_token", page_token)
        print("   ✅ Page token saved (never expires!)")
        
        # Step 3: Verify
        print("\n3️⃣ Verifying page token...")
        if self._is_token_valid(page_token):
            print("   ✅ Token verified and working!")
            print("\n🎉 Setup complete! Tokens stored in Supabase.")
            return True
        else:
            print("   ❌ Token verification failed")
            return False
    
    def _exchange_for_long_lived(self, short_token: str) -> Optional[str]:
        """Exchange short-lived token for long-lived token (~60 days)."""
        url = (
            f"https://graph.facebook.com/v19.0/oauth/access_token?"
            f"grant_type=fb_exchange_token"
            f"&client_id={self.app_id}"
            f"&client_secret={self.app_secret}"
            f"&fb_exchange_token={short_token}"
        )
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if "access_token" in data:
                return data["access_token"]
            else:
                print(f"   ⚠️  Error: {data.get('error', data)}")
                return None
        except Exception as e:
            print(f"   ⚠️  Request error: {e}")
            return None
    
    def _fetch_page_token(self, user_token: str) -> Optional[str]:
        """Fetch page access token from user token."""
        url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            for page in data.get("data", []):
                if page["id"] == self.page_id:
                    return page["access_token"]
            
            print(f"   ⚠️  Page {self.page_id} not found. Available pages:")
            for page in data.get("data", []):
                print(f"      - {page['name']} (ID: {page['id']})")
            return None
        except Exception as e:
            print(f"   ⚠️  Request error: {e}")
            return None
    
    def _is_token_valid(self, token: str) -> bool:
        """Check if a token is still valid."""
        url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
        
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Facebook Token Manager")
    parser.add_argument("--setup", help="Short-lived token to exchange", type=str)
    parser.add_argument("--check", action="store_true", help="Check current token status")
    args = parser.parse_args()
    
    manager = TokenManager()
    
    if args.setup:
        success = manager.setup_tokens(args.setup)
        if not success:
            print("\n❌ Setup failed. Check your App ID, App Secret, and token.")
    elif args.check:
        print("🔍 Checking token status...")
        token = manager.get_page_token()
        if token:
            print(f"✅ Valid token available (ends with ...{token[-10:]})")
        else:
            print("❌ No valid token")
    else:
        print("Usage:")
        print("  Setup:  python modules/token_manager.py --setup YOUR_SHORT_LIVED_TOKEN")
        print("  Check:  python modules/token_manager.py --check")

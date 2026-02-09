"""
AutoPost Configuration
Central configuration loader for all API keys and settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for AutoPost system."""
    
    # Facebook Configuration
    FB_PAGE_ID = os.getenv("FB_PAGE_ID", "887553684451232").strip()
    FB_ACCESS_TOKEN = os.getenv("fb_user_access_token", "").strip()
    FB_APP_ID = os.getenv("FB_APP_ID", "")
    FB_APP_SECRET = os.getenv("FB_APP_SECRET", "")
    
    # Mistral AI Configuration
    MISTRAL_API_KEY = os.getenv("mistral_api_key", "")
    MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
    MISTRAL_MODEL = "mistral-large-latest"
    
    # deAPI Image Generation Configuration
    DEAPI_KEY = os.getenv("DE_API_Image_KEY", "")
    DEAPI_BASE_URL = "https://api.deapi.ai/api/v1/client"
    DEAPI_MODEL = "Flux_2_Klein_4B_BF16"
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 1024
    IMAGE_STYLE = "minimalist"  # Minimalist style for generated images
    
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("supabase_url", "")
    SUPABASE_KEY = os.getenv("supabase_key", "")
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv("cloudinary_cloud_name", "")
    CLOUDINARY_API_KEY = os.getenv("cloudinary_api_key", "")
    CLOUDINARY_API_SECRET = os.getenv("cloudinary_api_secret", "")
    
    # Scheduling Configuration
    CYCLE_HOURS = 6  # Run every 6 hours
    
    # Content Configuration
    GENRE = os.getenv("GENRE", "tech")
    TONE = "engaging"  # Engaging tone for captions
    
    # RSS Feeds by Genre
    RSS_FEEDS = {
        "tech": [
            "https://techcrunch.com/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://feeds.arstechnica.com/arstechnica/index",
            "https://www.wired.com/feed/rss",
            "https://hnrss.org/frontpage",
        ]
    }
    
    @classmethod
    def get_feeds(cls, genre: str = None) -> list:
        """Get RSS feeds for a specific genre."""
        genre = genre or cls.GENRE
        return cls.RSS_FEEDS.get(genre, cls.RSS_FEEDS["tech"])
    
    @classmethod
    def validate(cls) -> dict:
        """Validate that all required config values are set."""
        issues = []
        
        if not cls.FB_ACCESS_TOKEN:
            issues.append("FB_ACCESS_TOKEN not set")
        if not cls.MISTRAL_API_KEY:
            issues.append("MISTRAL_API_KEY not set")
        if not cls.DEAPI_KEY:
            issues.append("DEAPI_KEY not set")
        if not cls.SUPABASE_URL:
            issues.append("SUPABASE_URL not set")
        if not cls.SUPABASE_KEY:
            issues.append("SUPABASE_KEY not set")
        if not cls.CLOUDINARY_CLOUD_NAME:
            issues.append("CLOUDINARY credentials not set")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


if __name__ == "__main__":
    # Test configuration loading
    result = Config.validate()
    if result["valid"]:
        print("✅ All configuration values are set!")
    else:
        print("⚠️  Missing configuration:")
        for issue in result["issues"]:
            print(f"   - {issue}")
    
    print(f"\n📰 RSS Feeds for '{Config.GENRE}':")
    for feed in Config.get_feeds():
        print(f"   - {feed}")

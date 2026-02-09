"""
AutoPost - Main Orchestrator
Coordinates all modules to automatically fetch, curate, and post tech news to Facebook.
"""
import sys
import time
from datetime import datetime, timezone

from config import Config
from modules.rss_fetcher import RSSFetcher
from modules.database import Database
from modules.ai_engine import AIEngine
from modules.image_generator import ImageGenerator
from modules.cloudinary_uploader import CloudinaryUploader
from modules.facebook_poster import FacebookPoster


class AutoPost:
    """Main orchestrator for the AutoPost system."""
    
    def __init__(self):
        self.rss = RSSFetcher()
        self.db = Database()
        self.ai = AIEngine()
        self.image_gen = ImageGenerator()
        self.cloudinary = CloudinaryUploader()
        self.facebook = FacebookPoster()
    
    def run_cycle(self, dry_run: bool = False):
        """
        Run a complete post cycle.
        
        Args:
            dry_run: If True, skip the actual Facebook posting
        """
        print("\n" + "="*60)
        print(f"🚀 AutoPost Cycle Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Step 1: Fetch RSS feeds
            print("\n📡 Step 1: Fetching RSS feeds...")
            articles = self.rss.fetch_all(max_age_hours=24)
            if not articles:
                print("⚠️  No articles found. Skipping cycle.")
                return False
            
            # Step 2: Filter out already posted articles
            print("\n🔍 Step 2: Filtering already posted articles...")
            posted_urls = self.db.get_posted_urls(limit=100)
            unposted = [a for a in articles if a["url"] not in posted_urls]
            print(f"   Found {len(unposted)} unposted articles (filtered {len(articles) - len(unposted)})")
            
            if not unposted:
                print("⚠️  All articles already posted. Skipping cycle.")
                return False
            
            # Step 3: Get context from database
            print("\n🧠 Step 3: Loading context...")
            recent_posts = self.db.get_recent_posts(limit=10, genre=Config.GENRE)
            
            # Step 4: AI selects best news
            print("\n🤖 Step 4: AI selecting best news...")
            selected = self.ai.select_best_news(unposted, recent_posts)
            if not selected:
                print("⚠️  AI couldn't select an article. Skipping cycle.")
                return False
            
            # Step 5: AI generates caption
            print("\n✍️  Step 5: Generating caption...")
            caption = self.ai.generate_caption(selected)
            
            # Step 6: AI generates image prompt
            print("\n🎨 Step 6: Generating image prompt...")
            image_prompt = self.ai.generate_image_prompt(selected)
            
            # Step 7: Generate image
            print("\n🖼️  Step 7: Generating image with deAPI...")
            image_url = self.image_gen.generate_image(image_prompt)
            if not image_url:
                print("⚠️  Image generation failed. Skipping cycle.")
                return False
            
            # Step 8: Upload to Cloudinary
            print("\n☁️  Step 8: Uploading to Cloudinary...")
            cloudinary_url = self.cloudinary.upload_from_url(image_url)
            if not cloudinary_url:
                print("⚠️  Cloudinary upload failed. Using deAPI URL.")
                cloudinary_url = image_url
            
            # Step 9: Post to Facebook (unless dry run)
            fb_post_id = None
            if dry_run:
                print("\n🔸 Step 9: DRY RUN - Skipping Facebook post")
                print(f"\n📝 Would have posted:")
                print(f"   Caption: {caption[:100]}...")
                print(f"   Image: {cloudinary_url}")
                print(f"   Link: {selected['url']}")
            else:
                print("\n📱 Step 9: Posting to Facebook...")
                fb_post_id = self.facebook.post_with_image(
                    caption=caption,
                    image_url=cloudinary_url,
                    link=selected["url"]
                )
                
                if not fb_post_id:
                    print("⚠️  Facebook posting failed. Skipping database save.")
                    return False
            
            # Step 10: Save to database
            if not dry_run:
                print("\n💾 Step 10: Saving to database...")
                self.db.save_post({
                    "url": selected["url"],
                    "title": selected["title"],
                    "caption": caption,
                    "image_url": cloudinary_url,
                    "fb_post_id": fb_post_id,
                    "genre": Config.GENRE
                })
            
            print("\n✅ Cycle completed successfully!")
            print(f"📰 Posted: {selected['title']}")
            if fb_post_id:
                print(f"🔗 Facebook Post ID: {fb_post_id}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during cycle: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoPost - Automated Facebook News Posting")
    parser.add_argument("--dry-run", action="store_true", help="Run without posting to Facebook")
    parser.add_argument("--single", action="store_true", help="Run a single cycle and exit")
    parser.add_argument("--test", action="store_true", help="Test all modules")
    args = parser.parse_args()
    
    # Validate configuration
    print("🔧 Checking configuration...")
    validation = Config.validate()
    if not validation["valid"]:
        print("❌ Configuration errors:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
        return
    print("✅ Configuration valid!\n")
    
    # Test mode
    if args.test:
        print("🧪 Running module tests...\n")
        autopost = AutoPost()
        print("✅ All modules initialized successfully!")
        return
    
    # Single cycle mode
    if args.single:
        autopost = AutoPost()
        autopost.run_cycle(dry_run=args.dry_run)
        return
    
    # Continuous mode (run every 6 hours)
    print(f"⏰ Starting AutoPost in continuous mode (every {Config.CYCLE_HOURS} hours)")
    print(f"📊 Genre: {Config.GENRE}")
    print(f"🎯 Press Ctrl+C to stop\n")
    
    autopost = AutoPost()
    
    try:
        while True:
            autopost.run_cycle(dry_run=args.dry_run)
            
            # Wait for next cycle
            wait_seconds = Config.CYCLE_HOURS * 3600
            print(f"\n😴 Sleeping for {Config.CYCLE_HOURS} hours...")
            print(f"   Next cycle at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(wait_seconds)
            
    except KeyboardInterrupt:
        print("\n\n👋 AutoPost stopped by user")


if __name__ == "__main__":
    main()

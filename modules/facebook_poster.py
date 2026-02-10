"""
Facebook Poster Module
Posts content to Facebook Page via Graph API.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from typing import Optional, Dict

from config import Config


class FacebookPoster:
    """Facebook Graph API integration for posting."""

    def __init__(self, use_token_manager: bool = True):
        self.page_id = Config.FB_PAGE_ID
        self.api_version = "v19.0"

        # Try to get token from TokenManager first
        if use_token_manager:
            try:
                from modules.token_manager import TokenManager

                manager = TokenManager()
                self.access_token = manager.get_page_token()
            except Exception as e:
                print(f"⚠️  TokenManager error: {e}")
                self.access_token = Config.FB_ACCESS_TOKEN
        else:
            self.access_token = Config.FB_ACCESS_TOKEN

    def post_with_image(
        self, caption: str, image_url: str, link: str = None
    ) -> Optional[str]:
        """
        Post to Facebook Page with an image.
        Posts to the feed endpoint so it appears in timeline, not just photos.

        Args:
            caption: The post caption/message
            image_url: URL of the image to post
            link: Optional link to include in first comment

        Returns:
            Facebook post ID, or None if failed
        """
        try:
            print(f"📱 Posting to Facebook Page feed...")

            # Step 1: Upload the photo to get a photo ID
            upload_url = (
                f"https://graph.facebook.com/{self.api_version}/{self.page_id}/photos"
            )
            upload_payload = {
                "url": image_url,
                "published": "false",  # Don't publish yet, just upload
                "access_token": self.access_token,
            }

            upload_response = requests.post(upload_url, data=upload_payload, timeout=30)

            if upload_response.status_code != 200:
                print(f"⚠️  Photo upload failed: {upload_response.text}")
                return None

            photo_id = upload_response.json().get("id")
            if not photo_id:
                print("⚠️  No photo ID returned from upload")
                return None

            # Step 2: Post to feed with the uploaded photo attached
            feed_url = (
                f"https://graph.facebook.com/{self.api_version}/{self.page_id}/feed"
            )
            feed_payload = {
                "message": caption,
                "attached_media[0]": f'{{"media_fbid":"{photo_id}"}}',
                "access_token": self.access_token,
            }

            response = requests.post(feed_url, data=feed_payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                post_id = data.get("id")
                print(f"✅ Posted successfully to feed! Post ID: {post_id}")

                # Add link as first comment if provided
                if link and post_id:
                    self._add_comment(post_id, f"🔗 Read more: {link}")

                return post_id
            else:
                print(f"⚠️  Facebook API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            print(f"⚠️  Error posting to Facebook: {e}")
            return None

    def _add_comment(self, post_id: str, message: str) -> bool:
        """Add a comment to a post."""
        url = f"https://graph.facebook.com/{self.api_version}/{post_id}/comments"

        payload = {"message": message, "access_token": self.access_token}

        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                print(f"💬 Added comment with link")
                return True
            return False
        except:
            return False


if __name__ == "__main__":
    print("🔄 Testing Facebook Poster...")

    # Test caption and image
    test_caption = "🚀 Testing AutoPost system! This is an automated post.\n\nRead more in comments 👇"
    test_image = "https://picsum.photos/1024/1024"
    test_link = "https://techcrunch.com"

    try:
        poster = FacebookPoster()
        post_id = poster.post_with_image(test_caption, test_image, test_link)

        if post_id:
            print(f"\n✅ Test passed!")
            print(f"📌 Post ID: {post_id}")
            print(f"🔗 View at: https://facebook.com/{post_id}")
        else:
            print(f"\n❌ Test failed - posting unsuccessful")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

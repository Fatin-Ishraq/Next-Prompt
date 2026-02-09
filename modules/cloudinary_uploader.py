"""
Cloudinary Uploader Module
Uploads images to Cloudinary for permanent storage.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cloudinary
import cloudinary.uploader
from typing import Optional
import requests
from datetime import datetime

from config import Config


class CloudinaryUploader:
    """Cloudinary integration for image storage."""
    
    def __init__(self):
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=Config.CLOUDINARY_CLOUD_NAME,
            api_key=Config.CLOUDINARY_API_KEY,
            api_secret=Config.CLOUDINARY_API_SECRET,
            secure=True
        )
    
    def upload_from_url(self, image_url: str, public_id: str = None) -> Optional[str]:
        """
        Upload an image from a URL to Cloudinary.
        
        Args:
            image_url: URL of the image to upload
            public_id: Optional custom public ID for the image
            
        Returns:
            Cloudinary URL of the uploaded image, or None if failed
        """
        try:
            # Generate public_id if not provided
            if not public_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                public_id = f"autopost/{Config.GENRE}/{timestamp}"
            
            print(f"☁️  Uploading to Cloudinary: {public_id}")
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_url,
                public_id=public_id,
                folder="autopost",
                overwrite=False,
                resource_type="image"
            )
            
            uploaded_url = result.get("secure_url")
            print(f"✅ Uploaded: {uploaded_url}")
            return uploaded_url
            
        except Exception as e:
            print(f"⚠️  Cloudinary upload error: {e}")
            return None


if __name__ == "__main__":
    print("🔄 Testing Cloudinary Uploader...")
    
    # Test with a sample image URL
    test_image_url = "https://picsum.photos/1024/1024"
    
    try:
        uploader = CloudinaryUploader()
        result_url = uploader.upload_from_url(test_image_url, public_id="test_upload")
        
        if result_url:
            print(f"\n✅ Test passed!")
            print(f"🖼️  Cloudinary URL: {result_url}")
        else:
            print(f"\n❌ Test failed - upload unsuccessful")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

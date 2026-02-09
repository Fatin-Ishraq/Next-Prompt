"""
Image Generator Module - deAPI Integration
Generates images using deAPI's ZImageTurbo_INT8 model.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
from typing import Optional

from config import Config


class ImageGenerator:
    """deAPI integration for text-to-image generation."""
    
    def __init__(self):
        self.api_key = Config.DEAPI_KEY
        self.base_url = Config.DEAPI_BASE_URL
        self.model = Config.DEAPI_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            
        Returns:
            URL of the generated image, or None if failed
        """
        print(f"🎨 Generating image with prompt: {prompt[:80]}...")
        
        # Step 1: Submit the generation request
        request_id = self._submit_request(prompt)
        if not request_id:
            return None
        
        print(f"⏳ Request submitted. ID: {request_id}")
        
        # Step 2: Poll for results
        image_url = self._poll_for_result(request_id)
        if image_url:
            print(f"✅ Image generated: {image_url}")
        else:
            print(f"❌ Image generation failed")
        
        return image_url
    
    def _submit_request(self, prompt: str) -> Optional[str]:
        """Submit image generation request to deAPI."""
        url = f"{self.base_url}/txt2img"
        
        payload = {
            "prompt": prompt,
            "model": self.model,
            "width": Config.IMAGE_WIDTH,
            "height": Config.IMAGE_HEIGHT,
            "steps": 4,
            "guidance": 7.5,
            "seed": -1,  # -1 for random seed
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("data", {}).get("request_id")
                return request_id
            else:
                print(f"⚠️  deAPI error {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"⚠️  Error submitting request: {e}")
            return None
    
    def _poll_for_result(self, request_id: str, max_wait: int = 120) -> Optional[str]:
        """
        Poll deAPI for the generation result.
        
        Args:
            request_id: The request ID from the submission
            max_wait: Maximum time to wait in seconds
            
        Returns:
            URL of the generated image, or None if failed/timeout
        """
        url = f"{self.base_url}/request-status/{request_id}"
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Debug: print the response structure
                    if not hasattr(self, '_debug_printed'):
                        print(f"   Debug - Response structure: {list(data.keys())}")
                        self._debug_printed = True
                    
                    # Handle different response structures
                    inner_data = data.get("data") or data
                    if inner_data is None or not isinstance(inner_data, dict):
                        print(f"   Warning - unexpected response format: {data}")
                        time.sleep(3)
                        continue
                    
                    status = inner_data.get("status")
                    
                    if status == "done":
                        # Extract image URL - deAPI returns it as result_url
                        image_url = inner_data.get("result_url")
                        if not image_url:
                            # Fallback to nested result structure (if format changes)
                            result = inner_data.get("result", {})
                            if isinstance(result, dict):
                                image_url = result.get("url") or result.get("image_url")
                            elif isinstance(result, str):
                                image_url = result
                        return image_url
                    elif status == "error":
                        error_msg = inner_data.get("error", "Unknown error")
                        print(f"⚠️  Generation error: {error_msg}")
                        return None
                    else:
                        # Still processing
                        print(f"   Status: {status}... waiting")
                        time.sleep(3)
                else:
                    print(f"⚠️  Status check error {response.status_code}: {response.text[:200]}")
                    time.sleep(3)
            except Exception as e:
                print(f"⚠️  Polling error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(3)
        
        print(f"⚠️  Timeout after {max_wait} seconds")
        return None


if __name__ == "__main__":
    print("🔄 Testing deAPI Image Generator...")
    
    test_prompt = "A sleek, minimalist tech illustration of artificial intelligence, featuring geometric shapes and neural network patterns in blue and white on a dark background"
    
    try:
        generator = ImageGenerator()
        image_url = generator.generate_image(test_prompt)
        
        if image_url:
            print(f"\n✅ Test passed!")
            print(f"🖼️  Image URL: {image_url}")
        else:
            print(f"\n❌ Test failed - no image generated")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

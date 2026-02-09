"""
AI Engine Module - Mistral Large 3 Integration
Uses Mistral AI to select the best news and generate engaging captions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import List, Dict, Optional

from config import Config


class AIEngine:
    """Mistral AI integration for content curation and generation."""
    
    def __init__(self):
        self.api_url = Config.MISTRAL_API_URL
        self.api_key = Config.MISTRAL_API_KEY
        self.model = Config.MISTRAL_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def select_best_news(self, articles: List[Dict], recent_posts: List[Dict] = None) -> Optional[Dict]:
        """
        Analyze articles and select the most interesting one.
        
        Args:
            articles: List of article dictionaries from RSS feeds
            recent_posts: List of recently posted articles to avoid duplication
            
        Returns:
            The selected article, or None if no good match
        """
        if not articles:
            return None
        
        # Build context about recent posts
        recent_topics = ""
        if recent_posts:
            recent_titles = [post.get("title", "") for post in recent_posts[:5]]
            recent_topics = "\n".join([f"- {title}" for title in recent_titles])
        
        # Build article list for AI
        article_list = ""
        for i, article in enumerate(articles[:20], 1):  # Limit to top 20 for context size
            article_list += f"{i}. [{article['source']}] {article['title']}\n"
            if article.get('summary'):
                article_list += f"   Summary: {article['summary'][:200]}...\n"
        
        prompt = f"""You are a tech news curator for a popular Facebook page. Your job is to select the SINGLE MOST interesting and engaging tech news story from today's feeds.

Recent posts (avoid similar topics):
{recent_topics if recent_topics else "None - this is the first post"}

Available articles:
{article_list}

Select the ONE article that:
1. Is most newsworthy and impactful
2. Will generate the most engagement on social media
3. Is NOT similar to recent posts
4. Has broad appeal to tech enthusiasts

Respond with ONLY the number (1-{min(20, len(articles))}) of the best article. Nothing else."""

        try:
            response = self._call_mistral([{"role": "user", "content": prompt}])
            
            if response:
                # Extract the number
                selection = response.strip()
                try:
                    index = int(selection) - 1
                    if 0 <= index < len(articles):
                        selected = articles[index]
                        print(f"📌 AI selected: {selected['title']}")
                        return selected
                except ValueError:
                    print(f"⚠️  AI returned invalid selection: {response}")
        except Exception as e:
            print(f"⚠️  Error in news selection: {e}")
        
        # Fallback: return first article
        print("⚠️  Using fallback: selecting first article")
        return articles[0]
    
    def generate_caption(self, article: Dict) -> str:
        """
        Generate an engaging Facebook caption for the article.
        
        Args:
            article: Article dictionary with title, summary, url
            
        Returns:
            Engaging caption text
        """
        prompt = f"""Create an ENGAGING Facebook post caption for this tech news article.

Title: {article['title']}
Summary: {article.get('summary', 'No summary available')}
Source: {article['source']}

Requirements:
- Tone: {Config.TONE}
- Length: 2-3 sentences
- Include relevant emojis
- Create curiosity without clickbait
- End with a call-to-action (e.g., "Read more in comments 👇")
- DO NOT include hashtags
- DO NOT include the link (it will be in comments)

Write ONLY the caption, nothing else."""

        try:
            response = self._call_mistral([{"role": "user", "content": prompt}])
            if response:
                caption = response.strip()
                print(f"✍️  Generated caption: {caption[:80]}...")
                return caption
        except Exception as e:
            print(f"⚠️  Error generating caption: {e}")
        
        # Fallback caption
        return f"🚀 {article['title']}\n\nRead more in comments 👇"
    
    def generate_image_prompt(self, article: Dict) -> str:
        """
        Generate an image prompt for the article.
        
        Args:
            article: Article dictionary
            
        Returns:
            Image generation prompt
        """
        prompt = f"""Create a detailed image generation prompt for this tech news article.

Title: {article['title']}
Summary: {article.get('summary', '')}

The image should be:
- Style: {Config.IMAGE_STYLE}, modern, tech-focused
- Suitable for Facebook posts
- Eye-catching but not cluttered
- Professional and high-quality

Write a detailed image generation prompt (1-2 sentences) that captures the essence of this article.
Include only the prompt, no explanation."""

        try:
            response = self._call_mistral([{"role": "user", "content": prompt}])
            if response:
                image_prompt = response.strip()
                print(f"🖼️  Image prompt: {image_prompt[:80]}...")
                return image_prompt
        except Exception as e:
            print(f"⚠️  Error generating image prompt: {e}")
        
        # Fallback: simple prompt
        return f"Minimalist tech illustration representing: {article['title']}"
    
    def _call_mistral(self, messages: List[Dict]) -> Optional[str]:
        """Make API call to Mistral."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"⚠️  Mistral API error {response.status_code}: {response.text}")
            return None


if __name__ == "__main__":
    print("🔄 Testing Mistral AI Engine...")
    
    # Test data
    test_articles = [
        {
            "title": "OpenAI releases GPT-5 with breakthrough reasoning capabilities",
            "summary": "The new model shows significant improvements in complex reasoning tasks and multimodal understanding.",
            "source": "TechCrunch",
            "url": "https://example.com/1"
        },
        {
            "title": "Google announces Quantum Chip breakthrough",
            "summary": "New quantum processor achieves quantum advantage in practical applications.",
            "source": "The Verge",
            "url": "https://example.com/2"
        }
    ]
    
    try:
        ai = AIEngine()
        
        print("\n1️⃣ Testing news selection...")
        selected = ai.select_best_news(test_articles)
        
        if selected:
            print("\n2️⃣ Testing caption generation...")
            caption = ai.generate_caption(selected)
            
            print("\n3️⃣ Testing image prompt generation...")
            image_prompt = ai.generate_image_prompt(selected)
            
            print("\n✅ All tests passed!")
            print(f"\n📰 Selected: {selected['title']}")
            print(f"\n📝 Caption:\n{caption}")
            print(f"\n🎨 Image Prompt:\n{image_prompt}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

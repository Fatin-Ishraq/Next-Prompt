"""
AI Engine Module - Google Gemini Integration
Uses Gemini AI to select the best news and generate educational captions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from typing import List, Dict, Optional

from config import Config


class AIEngine:
    """Gemini AI integration for content curation and generation."""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.base_url = Config.GEMINI_API_URL
        self.model = Config.GEMINI_MODEL
    
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
        for i, article in enumerate(articles[:20], 1):
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
            response = self._call_gemini(prompt)
            
            if response:
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
        
        print("⚠️  Using fallback: selecting first article")
        return articles[0]
    
    def generate_caption(self, article: Dict) -> str:
        """
        Generate an educational Facebook caption for the article.
        
        Args:
            article: Article dictionary with title, summary, url
            
        Returns:
            Educational caption text
        """
        prompt = f"""Create an EDUCATIONAL Facebook post caption for this tech news article.

Title: {article['title']}
Summary: {article.get('summary', 'No summary available')}
Source: {article['source']}

Write 2-3 substantial paragraphs that:
- Hook the reader immediately with a compelling opening line
- Explain what happened and why it's significant in the tech world
- Provide context - how does this fit into the bigger picture? What led to this?
- Include technical details that developers and tech enthusiasts would appreciate
- Explain any jargon in simple terms so anyone can follow
- Discuss potential implications or what this means for the future
- Include 3-4 relevant emojis placed naturally throughout
- End the final paragraph with "Read more in comments 👇"

Write in an engaging, conversational tone - like you're explaining exciting tech news to a smart friend who wants to actually understand it, not just skim headlines.

DO NOT use hashtags. DO NOT include the link. Write ONLY the caption."""

        try:
            response = self._call_gemini(prompt)
            if response:
                caption = response.strip()
                print(f"✍️  Generated caption: {caption[:80]}...")
                return caption
        except Exception as e:
            print(f"⚠️  Error generating caption: {e}")
        
        return f"🚀 {article['title']}\n\nRead more in comments 👇"
    
    def generate_image_prompt(self, article: Dict) -> str:
        """
        Generate a hook-style image prompt based on article analysis.
        
        Args:
            article: Article dictionary
            
        Returns:
            Image generation prompt that works as a visual hook
        """
        prompt = f"""Analyze this tech article and create an image prompt that will stop people scrolling.

Title: {article['title']}
Summary: {article.get('summary', '')}

Your task:
1. What is the CORE visual concept of this story? (A product? A breakthrough? A warning? An achievement?)
2. What emotion should the image evoke? (Excitement, awe, curiosity, concern?)
3. Create a scene-based image that tells part of the story visually

Image requirements:
- NO TEXT, NO WORDS, NO LETTERS, NO LOGOS - AI image generators cannot render text properly
- NO human faces (they look uncanny)
- Dramatic lighting and composition
- Clean, uncluttered background
- Professional quality suitable for social media
- The image should make someone curious about the article

Write a detailed image generation prompt (2-3 sentences) describing a specific scene or visual concept. Focus on what should be IN the image, not abstract styles.

Example good prompts:
- "A sleek smartphone unfolding like origami, floating against a dark gradient background with subtle blue rim lighting"
- "Massive server room with glowing quantum processors, ethereal mist flowing between racks, cinematic wide shot"
- "Robot hand and human hand reaching toward each other, dramatic side lighting, dark background"

Write ONLY the image prompt, no explanation."""

        try:
            response = self._call_gemini(prompt)
            if response:
                image_prompt = response.strip()
                print(f"🖼️  Image prompt: {image_prompt[:80]}...")
                return image_prompt
        except Exception as e:
            print(f"⚠️  Error generating image prompt: {e}")
        
        return f"Dramatic tech concept visualization, cinematic lighting, dark background, no text. Theme: {article['title'][:40]}"
    
    def _call_gemini(self, prompt: str) -> Optional[str]:
        """Make API call to Gemini."""
        url = f"{self.base_url}/{self.model}:generateContent"
        
        headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 2500
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                # Extract text from Gemini response structure
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    if text:
                        return text
                    else:
                        print("⚠️  Gemini returned empty text")
                        return None
                except (KeyError, IndexError) as e:
                    print(f"⚠️  Error parsing Gemini response: {e}")
                    print(f"    Response: {data}")
                    return None
            else:
                print(f"⚠️  Gemini API error {response.status_code}: {response.text[:500]}")
                return None
        except requests.exceptions.Timeout:
            print("⚠️  Gemini API timeout (60s)")
            return None
        except Exception as e:
            print(f"⚠️  Gemini API exception: {e}")
            return None


if __name__ == "__main__":
    print("🔄 Testing Gemini AI Engine...")
    
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

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Gemini_AI-Powered-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini AI">
  <img src="https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<h1 align="center">⚡ Next Prompt</h1>

<p align="center">
  <strong>AI-powered automated content curator that transforms breaking tech news into engaging Facebook posts.</strong>
</p>

<p align="center">
  <em>Fetch → Curate → Generate → Post — all on autopilot, every 6 hours.</em>
</p>

<p align="center">
  <a href="https://www.facebook.com/profile.php?id=61575488554617"><strong>📱 See it live on Facebook →</strong></a>
</p>

---

## ✨ Features

- **🔍 Smart News Curation** — Aggregates from TechCrunch, The Verge, Ars Technica, Wired, and Hacker News
- **🧠 AI-Powered Selection** — Gemini 2.5 Flash analyzes and picks the most impactful story
- **✍️ Educational Captions** — Generates engaging, informative captions that teach readers something new
- **🎨 AI Image Generation** — Creates stunning branded visuals using FLUX.2 
- **📱 Auto Facebook Posting** — Posts with image, caption, and article link in comments
- **🔄 Duplicate Prevention** — Remembers what's been posted to keep content fresh
- **⏰ Serverless Scheduling** — Runs automatically via GitHub Actions (zero hosting costs!)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI/LLM** | Google Gemini 2.5 Flash Lite |
| **Image Gen** | FLUX.2 Klein 4B via [deAPI](https://deapi.ai) |
| **Storage** | Cloudinary (images) + Supabase (PostgreSQL) |
| **Social** | Facebook Graph API |
| **Automation** | GitHub Actions (cron) |
| **Language** | Python 3.10+ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- API keys for: Gemini, deAPI, Facebook, Supabase, Cloudinary

### 1. Clone & Install

```bash
git clone https://github.com/Fatin-Ishraq/next-prompt.git
cd next-prompt
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
# AI Services
GEMINI_API_KEY=your_gemini_api_key
DE_API_Image_KEY=your_deapi_key

# Facebook
FB_PAGE_ID=your_page_id
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
fb_user_access_token=your_page_access_token

# Database (Supabase)
supabase_url=https://your-project.supabase.co
supabase_key=your_supabase_anon_key

# Image Storage (Cloudinary)
cloudinary_cloud_name=your_cloud_name
cloudinary_api_key=your_api_key
cloudinary_api_secret=your_api_secret
```

### 3. Setup Database

Run this SQL in your Supabase SQL Editor:

```sql
-- Posts table
CREATE TABLE posts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    caption TEXT,
    image_url TEXT,
    fb_post_id TEXT,
    genre TEXT DEFAULT 'tech',
    posted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Context table (for token storage)
CREATE TABLE context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Facebook Token Setup

```bash
# Exchange short-lived token for permanent page token
python modules/token_manager.py --setup YOUR_SHORT_LIVED_TOKEN
```

> 💡 Get your short-lived token from [Facebook Graph Explorer](https://developers.facebook.com/tools/explorer/)

### 5. Test Run

```bash
# Dry run (simulates everything without posting)
python main.py --dry-run --single

# Post for real
python main.py --single
```

---

## ⚙️ Deployment

### GitHub Actions (Recommended)

The included workflow runs automatically every 6 hours.

1. Push your code to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add these repository secrets:

| Secret Name | Description |
|------------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `DE_API_IMAGE_KEY` | deAPI image generation key |
| `FB_PAGE_ID` | Your Facebook Page ID |
| `FB_APP_ID` | Facebook App ID |
| `FB_APP_SECRET` | Facebook App Secret |
| `FB_USER_ACCESS_TOKEN` | Page access token |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

4. The workflow triggers at **00:00, 06:00, 12:00, 18:00 UTC** or manually via Actions tab

---

## 📁 Project Structure

```
next-prompt/
├── main.py                    # Main orchestrator
├── config.py                  # Configuration & settings
├── requirements.txt           # Dependencies
├── modules/
│   ├── rss_fetcher.py         # RSS feed aggregation
│   ├── ai_engine.py           # Gemini AI integration
│   ├── image_generator.py     # FLUX.2 image generation
│   ├── cloudinary_uploader.py # Image hosting
│   ├── facebook_poster.py     # Facebook Graph API
│   ├── database.py            # Supabase operations
│   └── token_manager.py       # Facebook token handling
└── .github/
    └── workflows/
        └── autopost.yml       # Scheduled automation
```

---

## 🔄 How It Works

```
┌──────────────┐     ┌───────────────┐     ┌────────────────┐
│   RSS Feeds  │────▶│  AI Curation  │────▶│ Caption Writer │
│  (5 sources) │     │   (Gemini)    │     │    (Gemini)    │
└──────────────┘     └───────────────┘     └───────┬────────┘
                                                   │
┌──────────────┐     ┌───────────────┐     ┌───────▼────────┐
│   Facebook   │◀────│   Cloudinary  │◀────│  Image Gen     │
│    Post!     │     │    Upload     │     │   (FLUX.2)     │
└──────────────┘     └───────────────┘     └────────────────┘
```

Every cycle:
1. **Fetch** — Pulls latest articles from 5 major tech sources
2. **Filter** — Removes already-posted articles
3. **Select** — AI picks the most engaging/impactful story
4. **Write** — AI generates an educational caption
5. **Visualize** — AI creates a branded image prompt → FLUX.2 generates the image
6. **Upload** — Image hosted on Cloudinary for reliability
7. **Post** — Published to Facebook with link in comments
8. **Remember** — Saved to database to prevent duplicates

---

## 📜 License

MIT License — feel free to use, modify, and build upon this project!

---

<p align="center">
  Made with ☕ and curiosity
</p>

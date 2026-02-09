# AutoPost 🤖

> An AI-powered system that automatically curates tech news, generates educational content, creates branded images, and posts to Facebook.

**Built as a learning project** to explore automation, AI integration, and social media APIs.

## What It Does

```
RSS Feeds → AI Curation → Caption Generation → Image Creation → Facebook Post
```

Every 6 hours, AutoPost:
1. **Fetches** news from TechCrunch, The Verge, Ars Technica, Wired, Hacker News
2. **Selects** the most impactful story using Gemini AI
3. **Writes** an educational caption that teaches readers something new
4. **Creates** a branded image using FLUX.2 (via deAPI)
5. **Posts** to Facebook with the article link in comments
6. **Remembers** what was posted to avoid duplicates

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI/LLM | Google Gemini 2.5 Flash Lite |
| Image Generation | FLUX.2 Klein 4B (deAPI) |
| Image Storage | Cloudinary |
| Database | Supabase (PostgreSQL) |
| Social Media | Facebook Graph API |
| Scheduling | GitHub Actions |

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/autopost.git
cd autopost
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env`:

```env
# AI
GEMINI_API_KEY=your_key

# Image Generation
DE_API_Image_KEY=your_key

# Facebook
FB_PAGE_ID=your_page_id
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret

# Database
supabase_url=your_url
supabase_key=your_key

# Image Storage
cloudinary_cloud_name=your_name
cloudinary_api_key=your_key
cloudinary_api_secret=your_secret
```

### 3. Setup Database

Run in Supabase SQL Editor:

```sql
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

CREATE TABLE context (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Setup Facebook Token (One-Time)

```bash
# Get short-lived token from Graph Explorer, then:
python modules/token_manager.py --setup YOUR_SHORT_LIVED_TOKEN
```

This stores a permanent page token in Supabase.

### 5. Test Run

```bash
# Dry run (no posting)
python main.py --dry-run --single

# Real post
python main.py --single
```

## Deploy to GitHub Actions

1. Push to GitHub
2. Add secrets in Settings → Secrets → Actions
3. The workflow runs every 6 hours automatically

## Project Structure

```
autopost/
├── config.py              # Configuration & brand settings
├── main.py                # Orchestrator
├── modules/
│   ├── rss_fetcher.py    # RSS aggregation
│   ├── ai_engine.py      # Gemini AI integration
│   ├── image_generator.py # FLUX.2 image creation
│   ├── cloudinary_uploader.py
│   ├── facebook_poster.py
│   ├── database.py       # Supabase
│   └── token_manager.py  # Facebook token handling
└── .github/workflows/
    └── autopost.yml      # Scheduled automation
```

## What I Learned

- Building multi-service integrations (7+ APIs)
- AI prompt engineering for consistent output
- Token management and OAuth flows
- GitHub Actions for serverless scheduling
- Error handling for production reliability

## License

MIT - Use it, learn from it, build on it!

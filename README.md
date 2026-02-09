# AutoPost - Automated Facebook News Posting System 🤖

An AI-powered system that automatically curates tech news, generates engaging content, creates images, and posts to Facebook every 6 hours.

## Features

- 📡 **RSS Feed Aggregation** - Fetches from TechCrunch, The Verge, Ars Technica, Wired, Hacker News
- 🧠 **AI-Powered Curation** - Mistral Large 3 selects the best news and generates engaging captions
- 🎨 **Image Generation** - FLUX.2 Klein 4B BF16 creates minimalist tech illustrations
- ☁️ **Cloud Storage** - Cloudinary for permanent image hosting
- 📱 **Facebook Integration** - Automatic posting to Facebook Pages
- 💾 **Memory System** - Supabase tracks history and prevents duplicates
- ⏰ **Scheduled Posts** - Runs every 6 hours via GitHub Actions

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
# DeAPI (Image Generation)
DE_API_Image_KEY=your_deapi_key

# Facebook
fb_user_access_token=your_facebook_page_token
FB_PAGE_ID=your_page_id

# Supabase (Database)
supabase_url=your_supabase_url
supabase_key=your_supabase_key

# Mistral AI
mistral_api_key=your_mistral_key

# Cloudinary (Image Storage)
cloudinary_cloud_name=your_cloud_name
cloudinary_api_key=your_api_key
cloudinary_api_secret=your_api_secret

# Configuration
GENRE=tech
```

### 3. Set Up Supabase Database

Run this SQL in your Supabase Dashboard:

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

CREATE INDEX idx_posts_url ON posts(url);
CREATE INDEX idx_posts_posted_at ON posts(posted_at DESC);
CREATE INDEX idx_context_key ON context(key);
```

## Usage

### Test Configuration

```bash
python config.py
```

### Test Individual Modules

```bash
python modules/rss_fetcher.py
python modules/database.py
python modules/ai_engine.py
python modules/image_generator.py
python modules/cloudinary_uploader.py
python modules/facebook_poster.py
```

### Dry Run (No Facebook Posting)

```bash
python main.py --dry-run --single
```

### Single Post

```bash
python main.py --single
```

### Continuous Mode (Every 6 Hours)

```bash
python main.py
```

## GitHub Actions Deployment

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```

2. **Add Secrets** in GitHub Settings → Secrets and variables → Actions:
   - `DE_API_IMAGE_KEY`
   - `FB_USER_ACCESS_TOKEN`
   - `FB_PAGE_ID`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `MISTRAL_API_KEY`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

3. **Enable GitHub Actions** - The workflow runs automatically every 6 hours!

## Project Structure

```
autopost/
├── config.py                 # Configuration loader
├── main.py                   # Main orchestrator
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (local)
├── modules/
│   ├── rss_fetcher.py       # RSS feed aggregation
│   ├── database.py          # Supabase integration
│   ├── ai_engine.py         # Mistral AI integration
│   ├── image_generator.py  # deAPI image generation
│   ├── cloudinary_uploader.py # Cloudinary uploads
│   └── facebook_poster.py   # Facebook Graph API
└── .github/
    └── workflows/
        └── autopost.yml     # GitHub Actions workflow
```

## How It Works

1. **Fetch** - Gets latest tech news from RSS feeds
2. **Filter** - Removes already posted articles using Supabase
3. **Select** - Mistral AI picks the best story
4. **Create** - AI generates caption and image prompt
5. **Generate** - FLUX.2 creates a minimalist image
6. **Upload** - Stores image on Cloudinary
7. **Post** - Publishes to Facebook with link in comments
8. **Save** - Records to Supabase to avoid duplicates

## License

MIT

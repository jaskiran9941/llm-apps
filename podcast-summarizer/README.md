# 🎧 Podcast Summarizer & Daily Digest

An automated workflow that summarizes your favorite podcasts and sends you a daily email digest with:
- AI-powered summaries of new episodes
- Key points and takeaways
- Podcast recommendations based on your interests

## Features

- **Smart Transcript Fetching**: Checks for existing transcripts before transcribing
- **AI Summarization**: Uses Claude (Anthropic) for intelligent episode summaries
- **Automated Email Delivery**: Daily digests via SendGrid
- **Podcast Recommendations**: Discovers similar podcasts you might enjoy
- **GitHub Actions**: Fully automated, runs daily without any server
- **Configurable**: Easy-to-manage podcast list with tags

## Architecture

```
┌─────────────────┐
│  GitHub Actions │ (Scheduled daily)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Podcast Fetcher │ (Fetches RSS feeds)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Transcript Fetch │ (Existing → Whisper)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Summarizer  │ (Claude API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Email Sender   │ (SendGrid)
└─────────────────┘
```

## Setup Instructions

### 1. Clone and Configure

```bash
# Clone the repository (or copy the podcast-summarizer folder)
cd podcast-summarizer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Get API Keys

#### Anthropic API Key (Required)
1. Go to https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

#### OpenAI API Key (Optional - for transcription)
1. Go to https://platform.openai.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Create a new API key
5. Add to `.env`: `OPENAI_API_KEY=your_key_here`

**Note**: Only needed if podcasts don't have existing transcripts. Whisper costs ~$0.006/minute.

#### SendGrid API Key (Required)
1. Go to https://sendgrid.com/ and create a free account
2. Navigate to Settings → API Keys
3. Create a new API key with "Mail Send" permissions
4. Add to `.env`: `SENDGRID_API_KEY=your_key_here`

**Sender Email Setup**:
- Go to Settings → Sender Authentication
- Verify a single sender email address (free tier)
- Use this as your `FROM_EMAIL` in `.env`

### 3. Configure Your Podcasts

Edit `config/podcasts.json`:

```json
{
  "podcasts": [
    {
      "name": "Lex Fridman Podcast",
      "rss_url": "https://lexfridman.com/feed/podcast/",
      "enabled": true,
      "tags": ["technology", "science", "philosophy"]
    },
    {
      "name": "The Tim Ferriss Show",
      "rss_url": "https://rss.art19.com/tim-ferriss-show",
      "enabled": true,
      "tags": ["business", "productivity", "health"]
    }
  ],
  "settings": {
    "max_episodes_per_podcast": 1,
    "summary_length": "medium",
    "include_timestamps": true,
    "email_recipient": "your-email@example.com"
  }
}
```

**Finding RSS URLs**:
- Most podcast websites have an RSS link
- Search: "[Podcast Name] RSS feed"
- Check Apple Podcasts or Spotify podcast pages

### 4. Test with Streamlit (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the testing interface
streamlit run streamlit_app.py
```

This opens a web interface where you can:
- Enter API keys securely
- Test RSS feed parsing
- Test AI summarization
- Test email delivery
- Run the full workflow with preview

### 4b. Test via Command Line

```bash
# Test email configuration
cd src
python main.py --test-email

# Run the full workflow
python main.py
```

### 5. Deploy to GitHub Actions

#### Create a GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit: Podcast summarizer workflow"
git remote add origin https://github.com/YOUR_USERNAME/podcast-summarizer.git
git push -u origin main
```

#### Add Secrets to GitHub

Go to your repository → Settings → Secrets and variables → Actions

Add these **secrets**:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` (if using transcription)
- `SENDGRID_API_KEY`
- `FROM_EMAIL`
- `TO_EMAIL`

Optionally add this **variable**:
- `SUMMARY_LENGTH` (short, medium, or long)

#### Enable GitHub Actions

1. Go to Actions tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically at 9 AM UTC daily
4. Click "Run workflow" to test immediately

### 6. Customize Schedule

Edit `.github/workflows/daily-digest.yml`:

```yaml
on:
  schedule:
    # Change this cron expression
    # Format: minute hour day month day-of-week
    - cron: '0 9 * * *'  # 9 AM UTC = 1 AM PST / 4 AM EST
```

**Common schedules**:
- `'0 6 * * *'` - 6 AM UTC
- `'0 12 * * *'` - 12 PM UTC
- `'0 18 * * *'` - 6 PM UTC

## Configuration Options

### Summary Length

In `.env` or GitHub variables:
```bash
SUMMARY_LENGTH=medium  # Options: short, medium, long
```

- **short**: 2-3 bullet points
- **medium**: 5-7 detailed points (recommended)
- **long**: 10-15 comprehensive points

### Maximum Episodes

In `config/podcasts.json`:
```json
{
  "settings": {
    "max_episodes_per_podcast": 1  // Process this many recent episodes
  }
}
```

## Usage

### Managing Your Podcast List

Add/remove podcasts by editing `config/podcasts.json`:

```json
{
  "name": "Podcast Name",
  "rss_url": "https://podcast-url.com/feed.xml",
  "enabled": true,  // Set to false to temporarily disable
  "tags": ["tag1", "tag2"]  // Used for recommendations
}
```

### Manual Runs

Trigger manually via GitHub Actions:
1. Go to Actions tab
2. Select "Daily Podcast Digest"
3. Click "Run workflow"

Or run locally:
```bash
cd src
python main.py
```

### Viewing Logs

GitHub Actions → Select a workflow run → View job logs

## Cost Estimate

Based on moderate usage:

| Service | Cost |
|---------|------|
| SendGrid | Free (100 emails/day) |
| Anthropic Claude | ~$0.01-0.05 per episode |
| OpenAI Whisper | ~$0.18-0.30 per hour of audio |
| GitHub Actions | Free (2,000 minutes/month) |

**Typical daily cost**: $0.05-0.20 (depending on transcription needs)

## Troubleshooting

### No emails received

1. Check SendGrid sender verification
2. Verify `FROM_EMAIL` is verified in SendGrid
3. Check spam folder
4. Review GitHub Actions logs for errors

### Transcription fails

1. Ensure `OPENAI_API_KEY` is set
2. Check if podcast has direct audio URL
3. Verify audio file is accessible

### Episode not detected

1. Check RSS feed URL is correct
2. Verify episode is published in last 24 hours
3. Cache may have marked it processed - delete `cache/` folder

### GitHub Actions not running

1. Ensure workflows are enabled in repository settings
2. Check cron schedule syntax
3. Verify secrets are configured

## Advanced Features

### Custom Email Templates

Edit `src/email_sender.py` → `_markdown_to_html()` to customize styling.

### Additional Podcast Sources

Extend `src/podcast_fetcher.py` to support:
- YouTube channels
- Spotify playlists
- Custom APIs

### Custom Summarization Prompts

Edit `src/summarizer.py` → `summarize_episode()` to adjust summary style.

## Privacy & Data

- All processing runs in GitHub Actions
- No data is stored externally
- Processed episodes tracked in local cache (committed to repo)
- API keys never exposed in logs

## Contributing

Feel free to:
- Add new features
- Improve transcript detection
- Support additional email providers
- Enhance summarization prompts

## License

MIT License - feel free to use and modify!

## Support

For issues or questions:
1. Check GitHub Actions logs
2. Verify API key configuration
3. Test locally before deploying
4. Review podcast RSS feed validity

---

**Enjoy your automated podcast digests!** 🎧📧

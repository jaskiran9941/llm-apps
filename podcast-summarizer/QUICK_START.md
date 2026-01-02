# 🚀 Quick Start Guide

## Where to Add API Keys

### Option 1: Streamlit Testing Interface (Easiest)
```bash
streamlit run streamlit_app.py
```
Enter keys in the sidebar - no file editing needed!

### Option 2: Local Environment File
1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your keys:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-xxxxx
   OPENAI_API_KEY=sk-xxxxx          # Optional
   SENDGRID_API_KEY=SG.xxxxx
   FROM_EMAIL=noreply@yourdomain.com
   TO_EMAIL=your-email@example.com
   ```

### Option 3: GitHub Actions (For Automation)
Repository → Settings → Secrets and variables → Actions

Add each as a **New repository secret**:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` (optional)
- `SENDGRID_API_KEY`
- `FROM_EMAIL`
- `TO_EMAIL`

## Get Your API Keys

### 1. Anthropic (Required) - FREE TRIAL AVAILABLE
1. Visit: https://console.anthropic.com/
2. Sign up / Log in
3. Go to: API Keys
4. Click: Create Key
5. Copy the key (starts with `sk-ant-`)

**Cost**: ~$0.01-0.05 per episode summary

### 2. SendGrid (Required) - FREE TIER: 100 emails/day
1. Visit: https://sendgrid.com/
2. Sign up for free account
3. Go to: Settings → API Keys
4. Create API Key with "Mail Send" permissions
5. Copy the key (starts with `SG.`)
6. Go to: Settings → Sender Authentication
7. Verify your sender email address
8. Use verified email as `FROM_EMAIL`

### 3. OpenAI (Optional) - Only if podcasts lack transcripts
1. Visit: https://platform.openai.com/
2. Sign up / Log in
3. Go to: API Keys
4. Create new secret key
5. Copy the key (starts with `sk-`)

**Cost**: ~$0.18-0.30 per hour of audio transcribed

## Testing Order

### 1️⃣ Launch Streamlit
```bash
cd podcast-summarizer
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### 2️⃣ Enter API Keys
In the sidebar, paste:
- Anthropic API Key (required)
- SendGrid API Key (required)
- From Email (verified in SendGrid)
- To Email (your email)

### 3️⃣ Test RSS Feed
Go to "📡 Test RSS Feed" tab:
- Try: `https://lexfridman.com/feed/podcast/`
- Click "Fetch Episodes"
- Verify episodes appear

### 4️⃣ Test Summarization
Go to "🤖 Test Summarization" tab:
- Use same RSS URL
- Click "Fetch & Summarize Latest Episode"
- Check the summary quality

### 5️⃣ Test Email
Go to "📧 Test Email" tab:
- Click "Send Test Email"
- Check your inbox/spam folder

### 6️⃣ Full Workflow
Go to "📋 Full Workflow" tab:
- Click "Run Full Workflow"
- Preview the digest
- Optionally send via email

## Common Issues

### "No existing transcript found, transcribing with Whisper..."
- **Normal**: Podcast doesn't have a transcript
- **Need**: OpenAI API key to transcribe
- **OR**: The summary will use description only (might be limited)

### "Error: ANTHROPIC_API_KEY environment variable is required"
- **Fix**: Enter the key in Streamlit sidebar
- **Or**: Add to `.env` file

### "Failed to send email"
- **Check**: FROM_EMAIL is verified in SendGrid
- **Check**: SendGrid API key has "Mail Send" permissions
- **Check**: Not over free tier limit (100/day)

### "No episodes found"
- **Check**: RSS URL is correct
- **Check**: Episodes exist in last 24 hours
- **Try**: Increase hours slider in Full Workflow tab

## Next Steps

Once testing works:
1. Add your favorite podcasts to `config/podcasts.json`
2. Push to GitHub
3. Add secrets to GitHub repository
4. Enable GitHub Actions
5. Receive daily digests automatically!

## Example Podcast RSS URLs

Test with these popular podcasts:

| Podcast | RSS URL |
|---------|---------|
| Lex Fridman | https://lexfridman.com/feed/podcast/ |
| Tim Ferriss Show | https://rss.art19.com/tim-ferriss-show |
| Huberman Lab | https://feeds.megaphone.fm/hubermanlab |
| a16z Podcast | https://a16z.simplecast.com/episodes.rss |
| The Daily (NYT) | https://feeds.simplecast.com/54nAGcIl |

---

**Need Help?** Check the full README.md for detailed troubleshooting.

"""Configuration for Trend Scout."""
import os
from dotenv import load_dotenv

load_dotenv()

# Topics to track - customize these
TOPICS = [
    "AI agents",
    "LLM applications",
    "developer tools",
    "startups funding",
]

# Subreddits to monitor per topic
SUBREDDIT_MAP = {
    "AI agents": ["MachineLearning", "LocalLLaMA", "artificial", "LangChain"],
    "LLM applications": ["MachineLearning", "LocalLLaMA", "ChatGPT", "ClaudeAI"],
    "developer tools": ["programming", "webdev", "devops", "SideProject"],
    "startups funding": ["startups", "Entrepreneur", "SaaS", "venturecapital"],
}

# How many results per source
MAX_RESULTS_PER_SOURCE = 10

# Email settings
DIGEST_EMAIL = os.getenv("DIGEST_EMAIL", "")
DIGEST_TIME = os.getenv("DIGEST_TIME", "08:00")

# Database
DATABASE_PATH = "trend_scout.db"

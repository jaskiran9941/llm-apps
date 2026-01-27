# 🔍 Web Search RAG

A Perplexity-style web search application built with Streamlit that uses Retrieval-Augmented Generation (RAG) to answer questions by searching the web and generating AI-powered responses with citations.

## 🌟 Features

- **Web Search Integration**: Searches DuckDuckGo for relevant information
- **AI-Powered Answers**: Uses OpenAI's GPT models to generate comprehensive answers
- **Source Citations**: Provides inline citations [1], [2], [3] linking to sources
- **Configurable Settings**:
  - Choose between GPT-4 (more accurate) or GPT-3.5 (faster, cheaper)
  - Adjust number of search results (3-10)
  - Control creativity with temperature slider (0.0-1.0)
- **Search History**: Keeps track of recent searches
- **Clean UI**: Beautiful Streamlit interface with two-column layout

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jaskiran9941/llm-apps.git
   cd llm-apps/rag-apps/web-search-rag
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 🎯 Usage

1. **Enter your question** in the search bar
2. **Click Search** to get results
3. **View the AI-generated answer** with citations in the left column
4. **Explore sources** in the right column (expandable cards)
5. **Adjust settings** in the sidebar to customize behavior

### Example Queries

- "What are the latest developments in AI?"
- "How does RAG differ from fine-tuning?"
- "Best practices for building Streamlit apps"
- "What happened in tech news this week?"

## 🏗️ How It Works

```
User Query
    ↓
1. Search Web (DuckDuckGo)
   → Returns search result snippets
    ↓
2. Format Results + Query into Prompt
   → "Based on these results, answer: [query]"
    ↓
3. Send to OpenAI GPT
   → Generate answer with citations [1], [2], [3]
    ↓
4. Display Answer + Sources
```

## 📊 Cost Estimates

**Per search:**
- Search: Free (DuckDuckGo)
- GPT-4: ~$0.01 per search
- GPT-3.5: ~$0.001 per search

**100 searches/day:**
- GPT-4: ~$30/month
- GPT-3.5: ~$3/month

## ⚙️ Configuration

Edit `.env` file:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-key-here
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI GPT-4 / GPT-3.5-turbo
- **Search**: DuckDuckGo (HTML version)
- **Parsing**: BeautifulSoup4
- **HTTP**: Requests

## 📝 Project Structure

```
web-search-rag/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example       # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- The `.gitignore` file excludes `.env` by default
- Use `.env.example` as a template

## 🐛 Troubleshooting

### "Search error: rate limit"
DuckDuckGo has rate limits. Add delays between searches or consider using SerpAPI (paid).

### "Could not fetch content"
Some websites block scrapers. This is expected - the app continues with available sources.

### Slow responses
- Use GPT-3.5 instead of GPT-4 (10x faster)
- Reduce number of search results to 3
- Lower temperature for more focused answers

## 🚀 Future Enhancements

- [ ] Add conversation memory for follow-up questions
- [ ] Implement deep web scraping for full article content
- [ ] Add image search results
- [ ] Save search history to database
- [ ] Real-time answer streaming
- [ ] Source quality ranking with confidence scores
- [ ] Export results to PDF/Markdown

## 📄 License

MIT License - feel free to use this project for learning and building!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📧 Contact

Created by Jaskiran Singh
- GitHub: [@jaskiran9941](https://github.com/jaskiran9941)

---

**Built with ❤️ using Streamlit + OpenAI**

# 🚀 Quick Start - Memory Chatbot

Get your memory-based chatbot running in under 5 minutes!

## Prerequisites Check

Before you start, make sure you have:

```bash
# Check Docker
docker --version
# Need: Docker 20.10+

# Check Python
python3 --version
# Need: Python 3.8+
```

Don't have these? See [installation links](#installation-links) below.

## 3-Step Setup

### 1️⃣ Start Qdrant Vector Database

```bash
cd memory-chatbot
docker-compose up -d
```

**Verify**: Open http://localhost:6334 - you should see Qdrant dashboard

### 2️⃣ Install Python Dependencies

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR: venv\Scripts\activate  # On Windows

# Install packages
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
streamlit run app.py
```

**Browser opens automatically at http://localhost:8501**

## First Use

1. **Get OpenAI API Key**
   - Go to: https://platform.openai.com/api-keys
   - Create new key
   - Copy it (starts with `sk-`)

2. **In the App Sidebar**:
   - Paste your API key
   - Enter a username (e.g., "alice")

3. **Start Chatting**:
   ```
   You: My name is Alice and I love coding in Python
   Bot: [Responds and remembers]

   You: What's my name?
   Bot: Your name is Alice
   ```

## Test It Works

**Memory Test**:
```
Tell it: "My favorite color is blue"
Then ask: "What's my favorite color?"
Expected: "Your favorite color is blue"
```

**Multi-User Test**:
```
1. Username: alice → Tell it your favorite food
2. Username: bob → Ask about favorite food
   Expected: Bob doesn't know Alice's food
```

## What You Built

You now have a chatbot that:
- ✅ Remembers conversations across sessions
- ✅ Finds relevant memories using AI search
- ✅ Isolates memory by user
- ✅ Stores everything locally (privacy!)
- ✅ Exports/imports memories as JSON

## Project Structure

```
memory-chatbot/
├── app.py               # Main Streamlit UI
├── config.py            # Settings & environment
├── memory_manager.py    # Memory operations
├── docker-compose.yml   # Qdrant setup
├── requirements.txt     # Python packages
└── README.md           # Full documentation
```

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Chat interface, memory integration | 360 |
| `memory_manager.py` | Store/retrieve memories | 254 |
| `config.py` | Configuration management | 119 |

## How It Works (Simple Explanation)

1. **User sends message** → Streamlit captures it
2. **Search memories** → Find similar past conversations
3. **Build context** → Combine memories with new question
4. **Ask GPT-4o** → Get personalized response
5. **Store conversation** → Save for future use

This is called **RAG** (Retrieval-Augmented Generation).

## Explore Features

**In the sidebar:**
- 📊 Memory Statistics → See total memories
- 📖 View All Memories → Browse what's stored
- 💾 Export Memories → Download as JSON
- 🗑️ Clear Memories → Start fresh
- 🔄 Clear Conversation → Reset chat display

## Next Steps

### Learn by Doing
1. ✅ Get it running (you're here!)
2. 📖 Read through `app.py` - understand the flow
3. 🔍 Check Qdrant UI (http://localhost:6334) - see the vectors
4. 🧪 Test different scenarios (see TESTING_CHECKLIST.md)
5. 🎨 Modify the code - make it yours!

### Understanding the Code

**Start here**: `app.py`
- Lines 1-100: Setup and configuration
- Lines 100-200: Chat interface
- Lines 200-300: Memory and AI integration

**Then**: `memory_manager.py`
- See how memories are stored and retrieved
- Understand vector search

**Finally**: `config.py`
- Simple configuration management
- Environment variables

### Extend It

Try adding:
- 🎨 Custom UI theme
- 📊 Memory visualization charts
- 🔍 Advanced search filters
- 💬 Conversation threading
- 🖼️ Image memory support

See README.md → Future Enhancements for ideas.

## Common Commands

```bash
# Start everything
docker-compose up -d
source venv/bin/activate
streamlit run app.py

# Stop everything
# Ctrl+C (stop Streamlit)
docker-compose down
deactivate

# View logs
docker-compose logs qdrant

# Check what's running
docker ps
```

## Troubleshooting

### "Port already in use"
```bash
docker-compose down
docker-compose up -d
```

### "Invalid API key"
- Check it starts with `sk-`
- No extra spaces
- Try entering in UI instead of .env

### "Failed to initialize memory"
```bash
# Make sure Qdrant is running
docker ps | grep qdrant

# If not, start it
docker-compose up -d
```

### "Module not found"
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Installation Links

Need to install prerequisites?

- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- **Python**: https://www.python.org/downloads/
- **OpenAI API Key**: https://platform.openai.com/api-keys

## Documentation

- 📘 **Full README**: `README.md` - Complete documentation
- 📝 **Setup Guide**: `SETUP_GUIDE.md` - Detailed setup steps
- ✅ **Testing**: `TESTING_CHECKLIST.md` - Validation checklist

## Quick Reference

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-your-key-here
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=memory_chatbot
```

### Qdrant URLs
- **API**: http://localhost:6333
- **Dashboard**: http://localhost:6334

### App URL
- **Streamlit**: http://localhost:8501

## Learning Resources

**Understand the concepts**:
- Vector databases → Store AI memories
- Embeddings → Convert text to numbers
- Semantic search → Find by meaning, not keywords
- RAG pattern → Enhance AI with custom knowledge

**Want deep dive?** See README.md → Key Concepts

## Success Checklist

You're ready when:
- [ ] Qdrant running (check http://localhost:6334)
- [ ] App loads (check http://localhost:8501)
- [ ] Can send messages and get responses
- [ ] Bot remembers information you tell it
- [ ] Different usernames have separate memories
- [ ] Memories survive app restart

**All checked?** Congratulations! You built a production-ready memory chatbot! 🎉

## Support

Stuck? Check in order:
1. This QUICKSTART.md (you are here)
2. SETUP_GUIDE.md (detailed steps)
3. README.md (full documentation)
4. TESTING_CHECKLIST.md (validation)

## Ready to Learn More?

**Beginner**: Read through the code with comments
**Intermediate**: Modify features and experiment
**Advanced**: Add new capabilities (see Future Enhancements in README.md)

---

**Now start chatting and see AI memory in action!** 🧠✨

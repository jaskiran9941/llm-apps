# Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

Follow these steps to get your memory chatbot running:

### Step 1: Start Qdrant (Vector Database)

```bash
docker-compose up -d
```

**Verify**: Open http://localhost:6334 in your browser - you should see the Qdrant dashboard.

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- streamlit (UI framework)
- openai (GPT-4o API)
- mem0ai (memory framework)
- python-dotenv (environment variables)
- qdrant-client (vector database client)

### Step 4: Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

**Don't have an API key?** Get one from: https://platform.openai.com/api-keys

### Step 5: Run the Application

```bash
streamlit run app.py
```

The app will automatically open in your browser at http://localhost:8501

### Step 6: Start Chatting

1. Enter your OpenAI API key in the sidebar (if not in .env)
2. Enter a username (e.g., "alice")
3. Start chatting!

## 🧪 Testing the Memory

Try this conversation to test memory:

```
You: My name is Alice and I love Python programming
Bot: [Responds and stores this in memory]

You: What's my name?
Bot: Your name is Alice

You: What do I love?
Bot: You love Python programming
```

## 🔍 Checking Everything Works

### Verify Qdrant is Running

```bash
# Check containers
docker ps

# You should see: memory_chatbot_qdrant

# Test API
curl http://localhost:6333
```

### Verify Python Dependencies

```bash
pip list | grep -E "streamlit|openai|mem0ai|qdrant"
```

Should show all packages installed.

### Check Application Files

```bash
ls -l *.py
# Should show: app.py, config.py, memory_manager.py
```

## 🐛 Common Issues

### Issue: "Port 6333 already in use"

**Solution**: Another Qdrant instance is running
```bash
docker-compose down
docker-compose up -d
```

### Issue: "Invalid API key"

**Solution**: Check your OpenAI API key
- Must start with `sk-`
- No extra spaces
- Key is active on OpenAI platform

### Issue: "Failed to initialize memory system"

**Solution**: Qdrant is not running
```bash
docker-compose up -d
# Wait 10 seconds for startup
streamlit run app.py
```

### Issue: "ModuleNotFoundError"

**Solution**: Virtual environment not activated or dependencies not installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Checking Memory Storage

### View in Qdrant UI
1. Open http://localhost:6334
2. Click "Collections"
3. You should see "memory_chatbot" collection
4. Click it to see your stored memories

### View in Application
- Click "📖 View All Memories" in sidebar
- Check "📊 Memory Statistics" in sidebar

## 🛑 Stopping Everything

```bash
# Stop the Streamlit app
# Press Ctrl+C in the terminal

# Stop Qdrant
docker-compose down

# Deactivate virtual environment
deactivate
```

## 🔄 Restarting Later

```bash
# Start Qdrant
docker-compose up -d

# Activate virtual environment
source venv/bin/activate

# Run app
streamlit run app.py
```

## 📝 Next Steps

After getting it working:

1. ✅ Test with different usernames (user isolation)
2. ✅ Export your memories (download JSON)
3. ✅ Try different models (GPT-4-turbo, etc.)
4. ✅ Check the Qdrant web UI to see vectors
5. ✅ Read through the code to understand how it works
6. ✅ Try extending it with new features!

## 💡 Tips

- **Persistence**: Your memories survive app restarts (stored in Qdrant)
- **Multi-user**: Each username has completely separate memories
- **Privacy**: All data stays local (in your Qdrant container)
- **Experimentation**: Feel free to modify the code and see what happens!

## 🎓 Learning Path

1. **Start Simple**: Get it working, test basic memory
2. **Explore Code**: Read through app.py, understand the flow
3. **Inspect Memories**: Use Qdrant UI to see how vectors are stored
4. **Modify Prompts**: Change system prompts in app.py
5. **Add Features**: Try implementing one of the future enhancements
6. **Understand RAG**: Read the "How It Works" section in README.md

## 📚 Documentation

- Full documentation: `README.md`
- Code comments: Check inline comments in all `.py` files
- Configuration: See `.env.example` for all options

---

**Need Help?** Check the Troubleshooting section in README.md

**Ready to Learn More?** Read the Key Concepts section in README.md

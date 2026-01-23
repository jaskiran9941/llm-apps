# 🚀 Production LLM Memory Application

Clean, production-ready chatbot with real memory capabilities.

## 🎯 What This Is

A **real, working** LLM application that demonstrates:
- **Episodic Memory**: Conversation history
- **Semantic Memory**: Knowledge retrieval from documents
- **Side-by-side comparison**: WITH vs WITHOUT memory

**No demos, no educational fluff** - just functional memory-enhanced chat.

---

## ⚡ Quick Start

### 1. Get Your API Key
```bash
# Get from: https://console.anthropic.com/
# Add to .env file:
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 2. Run the App
```bash
python3 -m streamlit run app_production.py
```

### 3. Load Knowledge Base
- Click "Load Documents" in sidebar
- Wait ~10 seconds
- Start chatting!

---

## 📁 Files

- **`app_production.py`** - Main production app (custom RAG)
- **`app_mem0.py`** - Alternative using Mem0 library
- **`memory/semantic_simple.py`** - Lightweight RAG implementation

---

## 🧠 How Memory Works

### Episodic Memory (Conversation History)
```python
# Stores last N turns of conversation
# Default: 10 turns
# Adjustable in sidebar
```

**Example:**
```
User: "I'm planning a trip"
Bot: "Great! Where to?"
User: "What should I pack?"  # Bot remembers "trip" from earlier
Bot: "For your trip, pack..."
```

### Semantic Memory (Knowledge Retrieval)
```python
# 1. Document → Chunks (500 words each)
# 2. Chunks → Embeddings (384-d vectors)
# 3. Store in memory
# 4. Query → Find similar chunks
# 5. Add to LLM context
```

**Example:**
```
Document: "TechCorp offers 15 vacation days"
User: "How many vacation days?"
System: Retrieves relevant chunk
Bot: "TechCorp offers 15 vacation days per year"
```

---

## 🔧 Configuration

### Sidebar Settings

**Conversation History**: 3-20 turns
- How many previous messages to remember
- Higher = better context, more tokens

**Documents to Retrieve**: 1-10
- How many relevant chunks to fetch
- Higher = more context, may include noise

**Similarity Threshold**: 0.0-1.0
- Minimum match quality
- Higher = fewer, better matches

**Temperature**: 0.0-1.0
- Response creativity
- 0 = focused, 1 = creative

---

## 📊 Memory Implementation

### Custom RAG (app_production.py)

**Pros:**
- Full control
- Transparent
- No external dependencies
- Lightweight

**Cons:**
- Manual management
- Basic features

**Use when:**
- You want full control
- Learning how RAG works
- Simple use case

### Mem0 (app_mem0.py)

**Pros:**
- Automatic memory extraction
- Managed lifecycle
- Advanced features
- Production-ready

**Cons:**
- External dependency
- Less control
- Learning curve

**Use when:**
- Production deployment
- Multiple users
- Advanced memory needs

---

## 🚀 Using Mem0

### Install
```bash
pip install mem0ai
```

### Run
```bash
python3 -m streamlit run app_mem0.py
```

### Features
- **Automatic memory extraction** from conversations
- **Long-term memory** across sessions
- **User-specific isolation**
- **Memory search** and retrieval
- **Memory management** (view, delete, update)

---

## 💡 Real-World Use Cases

### Customer Support Bot
```python
# Remembers:
- Previous issues
- Customer preferences
- Account details
- Past solutions
```

### Personal Assistant
```python
# Remembers:
- Your schedule
- Preferences
- Ongoing projects
- Important dates
```

### Knowledge Base Q&A
```python
# Retrieves from:
- Company docs
- Policies
- Procedures
- FAQs
```

---

## 🔄 How It Compares

### WITHOUT Memory (Right Side)
```
User: "How many vacation days?"
Bot: "Varies by company, typically 10-15 days"
```
- Generic
- No context
- Each question independent

### WITH Memory (Left Side)
```
User: "How many vacation days?"
Bot: "TechCorp offers 15 vacation days per year"
```
- Specific
- Uses knowledge base
- Remembers conversation

**The difference is dramatic!**

---

## 📈 Performance

### Token Usage
- **WITH Memory**: Higher (includes context)
- **WITHOUT Memory**: Lower (just question)

### Response Quality
- **WITH Memory**: Accurate, contextual
- **WITHOUT Memory**: Generic, limited

### Latency
- **WITH Memory**: ~2-3s (retrieval + generation)
- **WITHOUT Memory**: ~1-2s (generation only)

---

## 🛠️ Customization

### Add Your Own Documents

1. Place `.txt` files in `knowledge_base/sample_docs/`
2. Click "Load Documents"
3. Start asking questions!

### Change Memory Settings

Edit `config/config.py`:
```python
MAX_CONVERSATION_HISTORY = 20  # More history
TOP_K_RETRIEVAL = 5  # More docs
SIMILARITY_THRESHOLD = 0.8  # Stricter matching
```

### Switch Models

In sidebar or `config/config.py`:
```python
DEFAULT_MODEL = "claude-3-5-haiku-20241022"  # Fast
# or
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"  # Better
# or
DEFAULT_MODEL = "claude-opus-4-5-20251101"  # Best
```

---

## 🐛 Troubleshooting

### "No valid API key"
- Add key to `.env` file
- Or enter in sidebar
- Format: `ANTHROPIC_API_KEY=sk-ant-...`

### "Error loading documents"
- Check files exist in `knowledge_base/sample_docs/`
- Ensure `.txt` format
- Check file permissions

### Slow responses
- Lower `Documents to Retrieve`
- Reduce `Conversation History`
- Use Haiku model

### Memory not working
- Click "Load Documents" first
- Check similarity threshold (try 0.5)
- Verify documents loaded successfully

---

## 📝 Next Steps

### Production Deployment

1. **Add user authentication**
2. **Isolate user memories**
3. **Scale vector storage** (Pinecone, Weaviate)
4. **Add monitoring** (logging, metrics)
5. **Implement rate limiting**

### Enhanced Features

1. **File upload** for custom docs
2. **Multi-modal** (images, PDFs)
3. **Voice interface**
4. **Memory analytics**
5. **Export conversations**

---

## 🎯 Key Differences from Demo

**Demo Version:**
- ❌ Pre-recorded responses
- ❌ Educational content
- ❌ Step-by-step explanations
- ✅ Shows what it WOULD do

**Production Version:**
- ✅ Real API calls
- ✅ Actual memory
- ✅ Live retrieval
- ✅ Functional app

---

## 💰 Cost Estimation

Using Haiku (cheapest):
- **Input**: $0.25 / 1M tokens
- **Output**: $1.25 / 1M tokens

Typical conversation (10 turns):
- ~5,000 tokens total
- **Cost**: ~$0.01

With memory:
- +2-3x tokens (context)
- **Cost**: ~$0.02-0.03

**Still very affordable!**

---

## 🔐 Security Notes

- **API key**: Keep `.env` in `.gitignore`
- **User data**: Isolate per user in production
- **Documents**: Sanitize uploads
- **Rate limiting**: Prevent abuse

---

## 📚 Resources

- **Anthropic API**: https://docs.anthropic.com/
- **Mem0**: https://docs.mem0.ai/
- **RAG Patterns**: https://python.langchain.com/docs/use_cases/question_answering/

---

## ✅ Ready to Use!

The app is **live and functional**. Just add your API key and start chatting!

**Production-ready** • **No fluff** • **Real memory**

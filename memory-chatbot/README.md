# 🧠 Memory-Based LLM Chatbot

A personalized AI chatbot with persistent memory capabilities using OpenAI GPT-4o, Mem0, and Qdrant vector database. This project demonstrates how to build context-aware AI applications using the RAG (Retrieval-Augmented Generation) pattern.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Key Concepts](#key-concepts)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Learning Resources](#learning-resources)

## 🎯 Overview

This project implements a chatbot that remembers previous conversations and user preferences using vector embeddings and semantic search. Unlike traditional chatbots that treat each interaction independently, this application maintains persistent memory across sessions, enabling truly personalized interactions.

### Learning Objectives

By working with this project, you will learn:

- Vector database operations and semantic search
- RAG (Retrieval-Augmented Generation) implementation
- Memory management in LLM applications
- Multi-tenant architecture (user isolation)
- Context engineering for LLMs
- Docker integration for services
- Building interactive AI UIs with Streamlit

## ✨ Features

- **Persistent Memory**: Conversations are stored and retrieved across sessions
- **Semantic Search**: Relevant memories are found using vector similarity
- **User Isolation**: Each user has separate memory storage
- **Memory Analytics**: View statistics and insights about stored memories
- **Export/Import**: Download memories as JSON for backup or analysis
- **Multiple Models**: Support for GPT-4o, GPT-4-turbo, and more
- **Modern UI**: Clean, chat-style interface built with Streamlit
- **Memory Visibility**: See which memories were used to generate responses

## 🏗️ Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Streamlit UI (app.py)           │
├─────────────────────────────────────────┤
│  • Chat Interface                       │
│  • Memory Statistics                    │
│  • User Management                      │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│    Memory Manager (memory_manager.py)   │
├─────────────────────────────────────────┤
│  • Search Memories                      │
│  • Add Memories                         │
│  • Export/Clear Operations              │
└──────┬──────────────────────────────────┘
       │
       ├────────────────┬─────────────────┐
       ▼                ▼                 ▼
┌────────────┐   ┌────────────┐   ┌────────────┐
│    Mem0    │   │   Qdrant   │   │  OpenAI    │
│  Framework │   │   Vector   │   │    API     │
│            │   │     DB     │   │  (GPT-4o)  │
└────────────┘   └────────────┘   └────────────┘
```

### Data Flow

1. **User Input** → Streamlit captures user message
2. **Memory Search** → Relevant memories retrieved from Qdrant via Mem0
3. **Context Building** → Memories combined with user query
4. **LLM Generation** → OpenAI generates response with context
5. **Memory Storage** → New conversation stored in Qdrant
6. **Response Display** → User sees response + retrieved memories

## 📦 Prerequisites

Before you begin, ensure you have:

- **Docker Desktop** (for running Qdrant)
  - [Install Docker](https://www.docker.com/products/docker-desktop/)
- **Python 3.8+**
  - Check: `python --version`
- **OpenAI API Key**
  - Get one from: [OpenAI Platform](https://platform.openai.com/api-keys)
- **Git** (optional, for cloning)

## 🚀 Installation

### Step 1: Clone or Download

```bash
# If you have the project files, navigate to the directory
cd memory-chatbot

# Or clone if available
# git clone <repository-url>
# cd memory-chatbot
```

### Step 2: Set Up Qdrant Vector Database

Start Qdrant using Docker Compose:

```bash
docker-compose up -d
```

Verify Qdrant is running:
- API: http://localhost:6333
- Web UI: http://localhost:6334/dashboard

You should see the Qdrant web interface with no collections yet (they'll be created automatically).

### Step 3: Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
QDRANT_HOST=localhost
QDRANT_PORT=6333
COLLECTION_NAME=memory_chatbot
```

Alternatively, you can enter the API key directly in the Streamlit UI sidebar.

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at http://localhost:8501

## 💡 Usage

### First Time Setup

1. **Enter API Key**: In the sidebar, paste your OpenAI API key
2. **Enter Username**: Provide a username (e.g., "john", "alice")
3. **Start Chatting**: Type a message in the chat input

### Example Interactions

#### Teaching Preferences

```
User: My favorite color is blue
Bot: I'll remember that your favorite color is blue!

User: I work as a software engineer
Bot: Great! I'll keep in mind that you're a software engineer.
```

#### Using Memory

```
User: What's my favorite color?
Bot: Your favorite color is blue.

User: What do I do for work?
Bot: You work as a software engineer.
```

### Memory Management

- **View Statistics**: Check total memories and last update time in sidebar
- **View All Memories**: Click "📖 View All Memories" to see everything stored
- **Export Memories**: Download all memories as JSON for backup
- **Clear Memories**: Reset all memories for your user (requires confirmation)
- **Clear Conversation**: Clear only the current chat display (memories persist)

### Multi-User Testing

Test user isolation by using different usernames:

```
Username: alice
Alice: My favorite food is pizza

Username: bob
Bob: What's my favorite food?
Bot: I don't have that information (Alice's memories are separate)
```

## 🔬 How It Works

### The RAG Pattern

This application implements the **Retrieval-Augmented Generation (RAG)** pattern:

1. **Retrieval**: Search for relevant information from stored memories
2. **Augmentation**: Add retrieved information to the prompt context
3. **Generation**: LLM generates response using both query and context

### Memory Flow Explained

#### Storing Memories

```python
# When user sends: "My favorite color is blue"

1. User message → Stored in session
2. LLM generates response
3. Both messages → Converted to embedding vector
4. Vector stored in Qdrant with user_id
5. Text stored in Mem0 for retrieval
```

#### Retrieving Memories

```python
# When user asks: "What's my favorite color?"

1. Query → Converted to embedding vector
2. Vector search in Qdrant (finds similar memories)
3. Top K results retrieved (default: 5)
4. Memories added to prompt context
5. LLM uses context to answer accurately
```

### Vector Embeddings

- Each memory is converted to a high-dimensional vector (embedding)
- Similar meanings → Similar vectors
- Vector search finds semantically similar memories, not just keyword matches

**Example**:
- "favorite color is blue" and "I like the color blue" → Similar vectors
- Enables semantic understanding beyond exact words

## 📁 Project Structure

```
memory-chatbot/
├── app.py                    # Main Streamlit application (270 lines)
│   ├── UI components
│   ├── Chat interface
│   ├── Memory retrieval and display
│   └── OpenAI integration
│
├── memory_manager.py         # Memory operations abstraction (210 lines)
│   ├── MemoryManager class
│   ├── CRUD operations for memories
│   ├── Search and statistics
│   └── Export functionality
│
├── config.py                 # Configuration management (110 lines)
│   ├── Config class
│   ├── Environment variable loading
│   └── Validation logic
│
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Qdrant container configuration
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
│
└── qdrant_storage/          # Created by Docker (vector data)
    └── collections/
        └── memory_chatbot/  # Your memories stored here
```

## 🎓 Key Concepts

### 1. Vector Databases

Qdrant is a vector database optimized for similarity search:

- Stores high-dimensional vectors (embeddings)
- Fast approximate nearest neighbor search
- Supports filtering and metadata
- Perfect for RAG applications

**Why Vector DB?**
Traditional databases use exact matching (SQL WHERE clauses). Vector databases find *similar* items using distance metrics, enabling semantic search.

### 2. Embeddings

Embeddings are numerical representations of text:

```python
"Hello world" → [0.123, -0.456, 0.789, ...]  # 1536 dimensions
```

- Created by embedding models (e.g., OpenAI's text-embedding-ada-002)
- Similar meanings → Similar vectors
- Enable semantic similarity search

### 3. Semantic Search

Find information by meaning, not just keywords:

```
Query: "What's my preferred color?"
Matches: "favorite color is blue" (even though words differ)
```

Traditional search would miss this. Vector search finds it because the *meaning* is similar.

### 4. Context Injection

Enhance LLM prompts with retrieved information:

```python
# Without memory
User: What's my favorite color?
LLM: I don't have that information

# With memory (context injection)
System: [Context: User's favorite color is blue]
User: What's my favorite color?
LLM: Your favorite color is blue!
```

### 5. Multi-Tenancy

Each user has isolated memory:

- Memories tagged with `user_id`
- Searches filtered by `user_id`
- Privacy and personalization per user

## 🐛 Troubleshooting

### Qdrant Connection Failed

**Error**: "Failed to initialize memory system"

**Solutions**:
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running, start it
docker-compose up -d

# Check logs
docker-compose logs qdrant

# Verify accessibility
curl http://localhost:6333
```

### OpenAI API Errors

**Error**: "Invalid API key"

**Solutions**:
- Verify key starts with `sk-`
- Check key is active on OpenAI platform
- Ensure no extra spaces in `.env` file
- Try entering key directly in UI

### Port Already in Use

**Error**: "Port 6333 already allocated"

**Solutions**:
```bash
# Find process using port
lsof -i :6333

# Stop existing Qdrant
docker-compose down

# Or change port in docker-compose.yml
```

### Dependencies Installation Issues

**Error**: Package installation fails

**Solutions**:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Try installing packages individually
pip install streamlit openai mem0ai python-dotenv qdrant-client
```

### Streamlit Won't Start

**Error**: "ModuleNotFoundError" or import errors

**Solutions**:
```bash
# Verify virtual environment is activated
which python  # Should show path to venv

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Run with verbose errors
streamlit run app.py --logger.level=debug
```

## 🚀 Future Enhancements

Ideas to extend this project:

### Beginner Level
- [ ] Add conversation history export to PDF
- [ ] Implement memory search with filters (by date, type)
- [ ] Add user profiles with avatars
- [ ] Create preset conversation starters

### Intermediate Level
- [ ] Implement conversation threading (group related chats)
- [ ] Add memory importance scoring (prioritize key information)
- [ ] Create analytics dashboard (memory growth over time)
- [ ] Implement automatic memory summarization
- [ ] Add support for multiple languages

### Advanced Level
- [ ] Multi-modal memory (store images, documents)
- [ ] Memory sharing between users (collaborative memory spaces)
- [ ] Implement memory decay (time-based forgetting)
- [ ] Add RAG with multiple data sources (docs, websites)
- [ ] Build Chrome extension for capturing web content
- [ ] Integration with external tools (calendar, notes)

## 📚 Learning Resources

### Vector Databases
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Introduction to Vector Databases](https://www.pinecone.io/learn/vector-database/)

### RAG Pattern
- [What is RAG?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [RAG Best Practices](https://www.anthropic.com/index/contextual-retrieval)

### Embeddings
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Understanding Word Embeddings](https://jalammar.github.io/illustrated-word2vec/)

### Mem0 Framework
- [Mem0 Documentation](https://docs.mem0.ai/)
- [Mem0 GitHub](https://github.com/mem0ai/mem0)

### Streamlit
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Chat Elements Guide](https://docs.streamlit.io/library/api-reference/chat)

## 🎯 Success Checklist

Mark off as you complete:

- [ ] Qdrant container running successfully
- [ ] Application loads without errors
- [ ] Can enter API key and username
- [ ] Can send messages and receive responses
- [ ] Memories are stored (check sidebar stats)
- [ ] Memory retrieval works (bot remembers context)
- [ ] User isolation verified (different users have separate memories)
- [ ] Export memories works
- [ ] Clear memories works
- [ ] Understand RAG pattern and can explain it
- [ ] Can view memories in Qdrant web UI (http://localhost:6334)

## 📝 License

This is an educational project. Feel free to use, modify, and learn from it.

## 🤝 Contributing

This is a learning project, but suggestions and improvements are welcome!

## 📧 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Verify all prerequisites are installed
3. Check Docker and Qdrant are running
4. Review application logs for errors

---

**Happy Learning!** 🎓

Built with ❤️ using OpenAI GPT-4o, Mem0, Qdrant, and Streamlit

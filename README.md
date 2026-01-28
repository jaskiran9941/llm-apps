# LLM Apps

A collection of production-ready LLM applications covering RAG, multimodal AI, memory systems, audio processing, and more. Built with OpenAI, Claude, Gemini, Whisper, and open-source tools.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![LLMs](https://img.shields.io/badge/LLMs-OpenAI%20%7C%20Claude%20%7C%20Gemini-purple)

## Projects

### RAG Systems
| Project | Description | Stack |
|---------|-------------|-------|
| [rag-pipeline](rag-apps/rag-pipeline) | Complete RAG fundamentals - chunking, embeddings, vector search | OpenAI, ChromaDB |
| [conversational-rag](rag-apps/conversational-rag) | Multi-turn conversations with hybrid retrieval (semantic + BM25) | OpenAI, ChromaDB |
| [agentic-rag](rag-apps/agentic-rag) | Self-evaluating RAG with dynamic replanning | OpenAI, LangGraph |
| [multimodal-rag](rag-apps/multimodal-rag) | Text + images + tables + audio with Whisper transcription | OpenAI, Whisper |
| [rag-comparison](rag-apps/rag-comparison) | Side-by-side: Traditional vs Corrective vs Agentic RAG | OpenAI |
| [rag-evolution](rag-apps/rag-evolution) | 4-stage RAG progression from basic to vision-based | OpenAI, GPT-4V |
| [web-search-rag](rag-apps/web-search-rag) | Perplexity-style search with citations | OpenAI, DuckDuckGo |

### Memory & Context
| Project | Description | Stack |
|---------|-------------|-------|
| [llm-memory](llm-memory) | Episodic + semantic memory with 6 embedding providers | OpenAI, HuggingFace, Cohere |
| [memory-chatbot](memory-chatbot) | Persistent memory chatbot with Qdrant vector DB | OpenAI, Mem0, Qdrant |

### Audio & Multimodal
| Project | Description | Stack |
|---------|-------------|-------|
| [conversation-analyzer](conversation-analyzer) | Speaker diarization + tone/personality analysis | Deepgram, Gemini |
| [debate-partner](debate-partner) | Voice debate app: STT → LLM → TTS pipeline | Whisper, Claude, ElevenLabs |
| [podcast-summarizer](podcast-summarizer) | Automated podcast digests via email | Claude, SendGrid |
| [live-stream-analyzer](live-stream-analyzer) | Real-time stream analysis with Gemini Vision | Gemini 2.0, FFmpeg |

### Agents & Routing
| Project | Description | Stack |
|---------|-------------|-------|
| [stakeholder-router](stakeholder-router) | JSON classification + OOD detection + expert routing | OpenAI |
| [trend-scout](trend-scout) | Multi-source trend aggregator (Reddit + Web) | Gemini, Tavily, Composio |

### Utilities
| Project | Description | Stack |
|---------|-------------|-------|
| [transaction-reader](transaction-reader) | Gmail purchase analyzer with spending insights | Claude, Gmail API |
| [chat-personality-analyzer](chat-personality-analyzer) | Screenshot-based conversation analysis | Gemini Vision |
| [topic-demystifier](topic-demystifier) | Complex topics → comics, visuals, slides | OpenAI, DALL-E |
| [local-llm](local-llm) | Offline ChatGPT clone with React frontend | Ollama, FastAPI, React |

## Quick Start

Most projects follow this pattern:

```bash
cd <project-name>
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
streamlit run app.py  # Or python main.py
```

## Tech Stack

- **LLMs**: OpenAI GPT-4, Claude, Gemini, Ollama
- **Speech**: Whisper, Deepgram, ElevenLabs
- **Vector DBs**: ChromaDB, Qdrant, FAISS
- **Frameworks**: LangChain, LangGraph, Streamlit, FastAPI
- **Embeddings**: OpenAI, HuggingFace, Cohere, Voyage

## License

MIT

# 🚀 LLM Apps - Production-Ready AI Applications

> **Practical LLM applications showcasing local models, MCP integrations, and AI-driven workflows**
>
> A comprehensive collection of real-world AI applications built with cutting-edge LLM technologies. Each project demonstrates advanced patterns like multi-modal processing, memory management, voice integration, and autonomous reasoning.
>
> [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
> [![TypeScript](https://img.shields.io/badge/TypeScript-Latest-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
> [![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
> [![GitHub stars](https://img.shields.io/github/stars/jaskiran9941/llm-apps?style=flat-square)](https://github.com/jaskiran9941/llm-apps/stargazers)
>
> ---
>
> ## 📋 Table of Contents
>
> - [Features](#features)
> - - [Project Showcase](#project-showcase)
>   - - [Quick Start](#quick-start)
>     - - [Technologies](#technologies)
>       - - [Installation & Setup](#installation--setup)
>         - - [Project Categories](#project-categories)
>           - - [Use Cases](#use-cases)
>             - - [Contributing](#contributing)
>               - - [License](#license)
>                
>                 - ---
>
> ## ✨ Features
>
> 🎯 **Production-Ready Applications** - Fully functional, deployable AI solutions
> 🔄 **Multi-Modal Processing** - Text, audio, video, and image analysis
> 💾 **Memory & Context** - Advanced episodic and semantic memory systems
> 🗣️ **Voice Integration** - Speech recognition and text-to-speech capabilities
> 🤖 **MCP Integration** - Model Context Protocol implementations
> 🔌 **Local & Cloud Models** - Works with Ollama, Google Gemini, Claude APIs
> 🎨 **Streamlit UIs** - Beautiful, user-friendly interfaces
> ⚡ **Async Operations** - High-performance background processing
> 🛡️ **Guardrails** - Safety mechanisms and intelligent routing
>
> ---
>
> ## 🎬 Project Showcase
>
> ### Core Applications (14 Projects)
>
> #### 🎙️ **Audio & Voice Processing**
> - **[debate-partner](./debate-partner)** - AI-powered debate system with voice input/output
> - - **[podcast-summarizer](./podcast-summarizer)** - Extract actionable insights from podcasts
>   - - **[conversation-analyzer](./conversation-analyzer)** - Analyze conversation tone and personality from audio/video
>    
>     - #### 📊 **Multi-Modal Analysis**
>     - - **[live-stream-analyzer](./live-stream-analyzer)** - Real-time analysis of live streams with Gemini
>       - - **[chat-personality-analyzer](./chat-personality-analyzer)** - Personality analysis from conversation screenshots
>         - - **[multimodal-rag](./rag-apps)** - RAG system with audio support and topic detection
>          
>           - #### 💬 **Memory & Chat Systems**
>           - - **[llm-memory](./llm-memory)** - Episodic + semantic memory chat application
>             - - **[memory-chatbot](./memory-chatbot)** - Vector store integration with Qdrant
>               - - **[local-llm](./local-llm)** - Fully local LLM chat using Ollama
>                
>                 - #### 🔍 **Information Processing**
>                 - - **[trend-scout](./trend-scout)** - Multi-source tech trend aggregator (Reddit, web search)
>                   - - **[topic-demystifier](./topic-demystifier)** - AI-powered topic learning and explanation
>                     - - **[transaction-reader](./transaction-reader)** - Extract insights from financial transactions
>                      
>                       - #### 🧠 **Advanced Patterns**
>                       - - **[stakeholder-router](./stakeholder-router)** - Intelligent routing with guardrails
>                         - - **[mcp-apps](./mcp-apps)** - Model Context Protocol implementations
>                          
>                           - ---
>
> ## 🚀 Quick Start
>
> ### Installation
>
> ```bash
> # Clone the repository
> git clone https://github.com/jaskiran9941/llm-apps.git
> cd llm-apps
>
> # Create Python virtual environment
> python3 -m venv venv
> source venv/bin/activate  # On Windows: venv\Scripts\activate
>
> # Install dependencies (varies per project)
> cd [project-name]
> pip install -r requirements.txt
> ```
>
> ### Running an Application
>
> ```bash
> # Example: Run the chat personality analyzer
> cd chat-personality-analyzer
> streamlit run app.py
> ```
>
> ---
>
> ## 🛠️ Technologies
>
> ### Core Stack
> - **Python 3.8+** - Primary language
> - - **TypeScript** - Web components
>   - - **LLM Frameworks** - LangChain, LlamaIndex
>    
>     - ### AI & ML
>     - - **LLMs** - Claude, Gemini, Llama 2, Mistral
>       - - **Local Models** - Ollama integration
>         - - **Multi-Modal** - Vision APIs, Audio processing
>           - - **Vector Stores** - Qdrant, FAISS
>            
>             - ### Infrastructure
>             - - **Streamlit** - Web UI framework
>               - - **FastAPI** - API development
>                 - - **Async/Await** - Concurrent processing
>                   - - **Model Context Protocol (MCP)** - AI tool integration
>                    
>                     - ### APIs & Services
>                     - - **Google Gemini** - Vision and generative tasks
>                       - - **Anthropic Claude** - Advanced reasoning
>                         - - **OpenAI Whisper** - Speech recognition
>                           - - **Composio** - OAuth integration (Reddit, etc.)
>                            
>                             - ---
>
> ## 📦 Installation & Setup
>
> ### Prerequisites
> - Python 3.8 or higher
> - - Pip/Conda package manager
>   - - API keys (optional for cloud services)
>     -   - Google Gemini API key
>         -   - Claude API key (optional)
>             -   - OpenAI API key (for Whisper)
>              
>                 - ### Global Setup
>              
>                 - ```bash
>                   # Clone repository
>                   git clone https://github.com/jaskiran9941/llm-apps.git
>                   cd llm-apps
>
>                   # Create virtual environment
>                   python3 -m venv venv
>                   source venv/bin/activate
>
>                   # For individual projects
>                   cd [project-name]
>                   pip install -r requirements.txt
>                   ```
>
> ### API Key Configuration
>
> Create `.env` file in the project root:
>
> ```env
> # Google APIs
> GOOGLE_API_KEY=your_google_api_key_here
>
> # Claude (if using)
> ANTHROPIC_API_KEY=your_claude_key_here
>
> # OpenAI (for Whisper)
> OPENAI_API_KEY=your_openai_key_here
>
> # Composio (for OAuth integrations)
> COMPOSIO_API_KEY=your_composio_key_here
> ```
>
> ---
>
> ## 📂 Project Categories
>
> ### 🎓 Learning & Analysis
> - Extract and understand trends
> - - Analyze conversations and personalities
>   - - Demystify complex topics
>    
>     - ### 🤝 Interactive Systems
>     - - Debate partners and argumentation
>       - - Memory-based chatbots
>         - - Intelligent routing systems
>          
>           - ### 🔧 Integration & Automation
>           - - Local LLM deployment
>             - - Podcast processing pipelines
>               - - Transaction analysis workflows
>                
>                 - ### 🎬 Multi-Modal
>                 - - Live stream analysis
>                   - - Audio/video conversation analysis
>                     - - Visual document processing
>                      
>                       - ---
>
> ## 🎯 Use Cases
>
> - **Customer Service** - Intelligent conversation routing and analysis
> - - **Content Analysis** - Podcast/video summarization and trend detection
>   - - **Personal Assistant** - Memory-aware chatbots with context awareness
>     - - **Offline AI** - Fully local deployments with Ollama
>       - - **Market Research** - Trend aggregation and tech scouting
>         - - **Education** - Topic explanation and concept demystification
>           - - **Entertainment** - AI debate partners and interactive experiences
>            
>             - ---
>
> ## 📊 Repository Stats
>
> - **14 Production Projects**
> - - **76% Python, 20% TypeScript**
>   - - **41+ Commits**
>     - - **Active Development**
>      
>       - ---
>
> ## 🤝 Contributing
>
> Contributions are welcome! Here's how to get started:
>
> 1. **Fork the repository**
> 2. 2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
>    3. 3. **Make your changes** with clear commit messages
>       4. 4. **Push to your branch** (`git push origin feature/amazing-feature`)
>          5. 5. **Open a Pull Request**
>            
>             6. ### Code Standards
>             7. - Follow PEP 8 for Python
>                - - Include documentation strings
>                  - - Add requirements.txt for dependencies
>                    - - Create a project-specific README.md
>                     
>                      - ---
>
> ## 🗺️ Roadmap
>
> - [ ] Enhanced multi-modal RAG capabilities
> - [ ] - [ ] Real-time collaboration features
> - [ ] - [ ] Advanced memory optimization
> - [ ] - [ ] Extended model provider support
> - [ ] - [ ] Mobile app integration
> - [ ] - [ ] Advanced monitoring & logging
> - [ ] - [ ] Performance benchmarking suite
>
> - [ ] ---
>
> - [ ] ## 📚 Resources
>
> - [ ] - [LangChain Documentation](https://python.langchain.com/)
> - [ ] - [LlamaIndex Docs](https://docs.llamaindex.ai/)
> - [ ] - [Model Context Protocol](https://modelcontextprotocol.io/)
> - [ ] - [Streamlit Docs](https://docs.streamlit.io/)
> - [ ] - [Google Gemini API](https://ai.google.dev/)
> - [ ] - [Ollama Local Models](https://ollama.ai/)
>
> - [ ] ---
>
> - [ ] ## 📄 License
>
> - [ ] This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
>
> - [ ] ---
>
> - [ ] ## 👤 Author
>
> - [ ] **Jaskiran Singh**
> - [ ] - GitHub: [@jaskiran9941](https://github.com/jaskiran9941)
> - [ ] - Email: jaskiran.9941@gmail.com
>
> - [ ] ---
>
> - [ ] ## ⭐ Show Your Support
>
> - [ ] If you found this collection helpful, consider giving it a star! It helps other developers discover these practical AI applications.
>
> - [ ] <a href="https://github.com/jaskiran9941/llm-apps">⭐ Star on GitHub</a>

---

## 🔗 Connect

- [GitHub Profile](https://github.com/jaskiran9941)
- - [Issues & Discussions](https://github.com/jaskiran9941/llm-apps/issues)
 
  - ---

  **Last Updated**: January 2026 | Built with ❤️ for the AI community

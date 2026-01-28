# 🚀 LLM Apps - Production-Ready AI Applications

> Practical LLM applications showcasing local models, MCP integrations, and AI-driven workflows
>
> A comprehensive collection of real-world AI applications built with cutting-edge LLM technologies. Each project demonstrates advanced patterns like multi-modal processing, memory management, voice integration, and autonomous reasoning.
>
> [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
> [![TypeScript](https://img.shields.io/badge/TypeScript-Latest-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
> [![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
> [![GitHub stars](https://img.shields.io/github/stars/jaskiran9941/llm-apps?style=flat-square)](https://github.com/jaskiran9941/llm-apps/stargazers)
>
> ## 📋 Table of Contents
>
> - [Features](#features)
> - - [Projects](#projects)
>   - - [Quick Start](#quick-start)
>     - - [Tech Stack](#tech-stack)
>       - - [Installation](#installation)
>         - - [Use Cases](#use-cases)
>           - - [Contributing](#contributing)
>            
>             - ---
>
> ## ✨ Features
>
> - 🎯 **14 Production-Ready Applications** - Fully functional, deployable AI solutions
> - - 🔄 **Multi-Modal Processing** - Text, audio, video, and image analysis
>   - - 💾 **Memory Systems** - Episodic and semantic memory integration
>     - - 🗣️ **Voice Processing** - Speech recognition and text-to-speech
>       - - 🤖 **MCP Integration** - Model Context Protocol support
>         - - 🔌 **Flexible Models** - Ollama (local), Google Gemini, Anthropic Claude
>           - - 🎨 **Streamlit UIs** - Beautiful, user-friendly web interfaces
>             - - ⚡ **Async Operations** - High-performance processing
>               - - 🛡️ **Guardrails** - Safety mechanisms and intelligent routing
>                
>                 - ---
>
> ## 🎬 Projects Overview
>
> ### 🎙️ Audio & Voice
> - **debate-partner** - AI debate system with voice I/O
> - - **podcast-summarizer** - Extract insights from podcasts
>   - - **conversation-analyzer** - Analyze tone and personality from audio/video
>    
>     - ### 📊 Multi-Modal Analysis
>     - - **live-stream-analyzer** - Real-time stream analysis with Gemini
>       - - **chat-personality-analyzer** - Personality from conversation screenshots
>         - - **multimodal-rag** - RAG with audio support and topic detection
>          
>           - ### 💬 Memory & Chat
>           - - **llm-memory** - Episodic + semantic memory chat
>             - - **memory-chatbot** - Qdrant vector store integration
>               - - **local-llm** - Fully local LLM with Ollama
>                
>                 - ### 🔍 Information Processing
>                 - - **trend-scout** - Tech trends from Reddit and web search
>                   - - **topic-demystifier** - AI-powered topic learning
>                     - - **transaction-reader** - Financial transaction analysis
>                      
>                       - ### 🧠 Advanced Patterns
>                       - - **stakeholder-router** - Intelligent routing with guardrails
>                         - - **mcp-apps** - Model Context Protocol implementations
>                          
>                           - ---
>
> ## 🚀 Quick Start
>
> ### Installation
>
> ```bash
> # Clone repository
> git clone https://github.com/jaskiran9941/llm-apps.git
> cd llm-apps
>
> # Create virtual environment
> python3 -m venv venv
> source venv/bin/activate  # Windows: venv\Scripts\activate
>
> # Install project dependencies
> cd [project-name]
> pip install -r requirements.txt
> ```
>
> ### Running a Project
>
> ```bash
> # Example: Run the chat personality analyzer
> cd chat-personality-analyzer
> streamlit run app.py
> ```
>
> ---
>
> ## 🛠️ Tech Stack
>
> **Languages**: Python (76%), TypeScript (20%)
>
> **Core Frameworks**:
> - LangChain, LlamaIndex
> - - Streamlit, FastAPI
>   - - Qdrant, FAISS (vector stores)
>    
>     - **AI/ML**:
>     - - Claude, Gemini, Llama 2, Mistral
>       - - Ollama (local models)
>         - - Whisper (speech recognition)
>          
>           - **APIs**:
>           - - Google Gemini Vision
>             - - Anthropic Claude
>               - - OpenAI Whisper
>                 - - Composio (OAuth/integrations)
>                  
>                   - ---
>
> ## 📦 Installation & Setup
>
> ### Prerequisites
> - Python 3.8+
> - - pip/conda
>   - - (Optional) API keys for cloud services
>    
>     - ### API Keys
>    
>     - Create `.env` file in project root:
>    
>     - ```env
> GOOGLE_API_KEY=your_key_here
> ANTHROPIC_API_KEY=your_key_here
> OPENAI_API_KEY=your_key_here
> COMPOSIO_API_KEY=your_key_here
> ```
>
> ### Local LLM Setup (Ollama)
>
> ```bash
> # Install Ollama from https://ollama.ai/
> # Pull a model
> ollama pull llama2
> ollama pull mistral
>
> # Models run on http://localhost:11434
> ```
>
> ---
>
> ## 🎯 Use Cases
>
> - **Customer Service** - Intelligent conversation routing
> - - **Content Analysis** - Podcast/video summarization
>   - - **Personal Assistant** - Memory-aware chatbots
>     - - **Offline AI** - No-internet deployments
>       - - **Market Research** - Trend aggregation
>         - - **Education** - Topic explanation
>           - - **Entertainment** - Interactive AI experiences
>            
>             - ---
>
> ## 🤝 Contributing
>
> Contributions welcome! Here's how:
>
> 1. Fork the repo
> 2. 2. Create feature branch (`git checkout -b feature/name`)
>    3. 3. Make changes with clear commits
>       4. 4. Push to branch (`git push origin feature/name`)
>          5. 5. Open Pull Request
>            
>             6. ### Standards
>             7. - Follow PEP 8 (Python)
>                - - Include docstrings
>                  - - Add requirements.txt
>                    - - Create project README.md
>                     
>                      - ---
>
> ## 📄 License
>
> MIT License - see [LICENSE](LICENSE) file
>
> ---
>
> ## 👤 Author
>
> **Jaskiran Singh**
> - GitHub: [@jaskiran9941](https://github.com/jaskiran9941)
>
> - ---
>
> ## ⭐ Support
>
> If you found this helpful, please consider giving it a star! It helps others discover these practical AI applications.
>
> **[⭐ Star on GitHub](https://github.com/jaskiran9941/llm-apps)**
>
> ---
>
> Built with ❤️ for the AI community | Last Updated: January 2026

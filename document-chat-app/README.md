# Document Chat App

A beautiful Streamlit web application that allows you to upload PDF or text files and chat with them using AI. Ask questions and get answers based on your document's content.

## Features

- 🎨 Beautiful and intuitive Streamlit UI
- 📄 Upload PDF and text files
- 🧠 Intelligent document chunking for better context retrieval
- 🔍 Vector embeddings for semantic search
- 💬 Conversational AI that remembers context
- 📚 Source citations showing relevant document excerpts
- 🎯 Real-time chat interface
- 💾 Session state management

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Setup Instructions

1. **Clone or navigate to the project directory:**
   ```bash
   cd document-chat-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up your OpenAI API key:**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key
   - Alternatively, export it directly:
     ```bash
     export OPENAI_API_KEY='your_api_key_here'
     ```

6. **Run the Streamlit application:**
   ```bash
   streamlit run streamlit_app.py
   ```

7. **The app will automatically open in your browser at:**
   ```
   http://localhost:8501
   ```

## How to Use

1. **Enter Your API Key:**
   - Enter your OpenAI API key in the sidebar (or set it as an environment variable)

2. **Upload a Document:**
   - Click "Browse files" in the sidebar to select a PDF or TXT file
   - Click "📊 Process Document" button
   - Wait for the file to be processed (you'll see a success message with confetti!)

3. **Chat with Your Document:**
   - Type your question in the chat input at the bottom
   - Press Enter to send
   - The AI will answer based on the document content
   - Click "📚 View Sources" to see the relevant document excerpts

4. **Upload a New Document:**
   - Click "🔄 Upload New Document" to start over with a different file

5. **Clear Chat:**
   - Click "🗑️ Clear Chat History" to reset the conversation while keeping the same document

## Technology Stack

- **UI Framework:** Streamlit
- **AI/ML:** OpenAI GPT-3.5-turbo, LangChain
- **Vector Database:** ChromaDB
- **Document Processing:** PyPDF, LangChain document loaders
- **Embeddings:** OpenAI text-embedding-ada-002

## How It Works

1. **Document Processing:**
   - Uploaded files are parsed and split into manageable chunks
   - Each chunk is converted to vector embeddings using OpenAI's embedding model

2. **Vector Storage:**
   - Embeddings are stored in ChromaDB for efficient similarity search
   - When you ask a question, the most relevant chunks are retrieved

3. **Conversational AI:**
   - Your question and relevant document chunks are sent to GPT-3.5-turbo
   - The AI generates an answer based on the retrieved context
   - Chat history is maintained for follow-up questions

## Notes

- The app processes one document at a time
- Uploading a new document clears the previous one and resets the conversation
- Your API key is stored only in the session (not saved to disk)
- API costs apply based on OpenAI usage
- Chat history is maintained for better context in follow-up questions

## Troubleshooting

- **Import errors:** Make sure all dependencies are installed with `pip install -r requirements.txt`
- **OpenAI errors:** Verify your API key is entered correctly in the sidebar
- **Port already in use:** Run with a different port: `streamlit run streamlit_app.py --server.port 8502`
- **Streamlit issues:** Try clearing the cache with `streamlit cache clear`

## Future Enhancements

- Support for multiple documents
- Support for more file formats (DOCX, CSV, etc.)
- User authentication and session management
- Export chat history
- Advanced filtering and search options

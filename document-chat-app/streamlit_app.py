import streamlit as st
import os
import tempfile
import ssl
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
import shutil

# Disable SSL verification for learning purposes
# WARNING: Only use this in development/learning environments!
import warnings
warnings.filterwarnings('ignore')

# Disable SSL verification completely
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HTTPX_VERIFY'] = 'false'
ssl._create_default_https_context = ssl._create_unverified_context

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey patch httpx to disable SSL verification
try:
    import httpx
    original_client = httpx.Client
    original_async_client = httpx.AsyncClient

    class NoVerifyClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            kwargs['verify'] = False
            super().__init__(*args, **kwargs)

    class NoVerifyAsyncClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs['verify'] = False
            super().__init__(*args, **kwargs)

    httpx.Client = NoVerifyClient
    httpx.AsyncClient = NoVerifyAsyncClient
except ImportError:
    pass

# Page configuration
st.set_page_config(
    page_title="Document Chat Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .upload-text {
        text-align: center;
        padding: 2rem;
        border: 2px dashed #ccc;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    div[data-testid="stExpander"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_file' not in st.session_state:
    st.session_state.processed_file = None

def process_uploaded_file(uploaded_file):
    """Process the uploaded file and create vector store"""
    try:
        # Create a temporary directory for this session
        temp_dir = tempfile.mkdtemp()

        # Save uploaded file temporarily
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Load the document
        with st.spinner('📖 Reading your document...'):
            try:
                if uploaded_file.name.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path)

                documents = loader.load()
            except Exception as e:
                st.error(f"❌ **Failed to read document:** {str(e)}")
                return None, None, 0, None

        # Split into chunks
        with st.spinner('✂️ Splitting into chunks...'):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_documents(documents)

        # Create embeddings and vector store
        with st.spinner('🧠 Creating embeddings... This may take a moment.'):
            try:
                # Create custom HTTP client with SSL disabled
                import httpx
                http_client = httpx.Client(verify=False, timeout=30.0)

                embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    transport="rest",  # Use REST instead of gRPC
                    client_options={"api_endpoint": "generativelanguage.googleapis.com"}
                )

                # Create FAISS vector store (no persistence directory needed)
                vectorstore = FAISS.from_documents(
                    documents=chunks,
                    embedding=embeddings
                )
            except Exception as e:
                error_msg = str(e).lower()
                if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg or "403" in error_msg:
                    st.error("❌ **Google Gemini API Key Error**\n\n"
                           "Your API key is missing or invalid. Please:\n"
                           "1. Get your API key from https://aistudio.google.com/apikey\n"
                           "2. Enter it in the sidebar\n"
                           "3. Make sure Gemini API is enabled")
                elif "connection" in error_msg or "network" in error_msg or "timeout" in error_msg:
                    st.error("❌ **Connection Error**\n\n"
                           "Cannot connect to Google Gemini. Please check:\n"
                           "1. Your internet connection\n"
                           "2. Your firewall/VPN settings\n"
                           "3. Google AI service availability")
                elif "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
                    st.error("❌ **Rate Limit Error**\n\n"
                           "You've exceeded Gemini's rate limits. Please:\n"
                           "1. Wait a few moments and try again\n"
                           "2. Check your quota at https://aistudio.google.com")
                else:
                    st.error(f"❌ **Google Gemini API Error**\n\n{str(e)}")
                return None, None, 0, None

        # Create conversational chain
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                transport="rest"  # Use REST to avoid SSL issues
            )
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True,
                verbose=False
            )
        except Exception as e:
            st.error(f"❌ **Failed to create chat chain:** {str(e)}")
            return None, None, 0, None

        return vectorstore, qa_chain, len(chunks), temp_dir

    except Exception as e:
        st.error(f"❌ **Unexpected Error:** {str(e)}\n\nPlease try again or contact support.")
        return None, None, 0, None

def reset_conversation():
    """Reset the conversation and clear all session state"""
    st.session_state.messages = []
    st.session_state.vectorstore = None
    st.session_state.qa_chain = None
    st.session_state.chat_history = []
    st.session_state.processed_file = None

# Sidebar
with st.sidebar:
    st.title("📚 Document Chat")
    st.markdown("---")

    # API Key input
    api_key = st.text_input("Google Gemini API Key", type="password", help="Enter your Google Gemini API key")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

        # Test API key button
        if st.button("🔑 Test API Key"):
            with st.spinner("Testing API key..."):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    # Make a minimal API call
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Hi")
                    st.success("✅ API Key is valid! Connection to Google Gemini successful.")
                except Exception as e:
                    error_msg = str(e).lower()
                    if "api key" in error_msg or "authentication" in error_msg or "401" in error_msg or "403" in error_msg:
                        st.error("❌ **Invalid API Key**\n\nYour API key is incorrect. Please check it at https://aistudio.google.com/apikey")
                    elif "connection" in error_msg or "network" in error_msg or "timeout" in error_msg:
                        st.error("❌ **Network/Firewall Issue**\n\n"
                               "Cannot connect to Google Gemini servers. This could be:\n"
                               "- Corporate firewall blocking Google AI\n"
                               "- VPN/proxy issues\n"
                               "- Network connectivity problem\n\n"
                               f"Technical details: {str(e)}")
                    else:
                        st.error(f"❌ **Error:** {str(e)}")

    st.markdown("---")

    # File upload section
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'txt'],
        help="Upload a PDF or TXT file to chat with"
    )

    if uploaded_file is not None:
        # Check if this is a new file
        if st.session_state.processed_file != uploaded_file.name:
            if st.button("📊 Process Document", type="primary"):
                if not api_key:
                    st.error("⚠️ Please enter your Google Gemini API key first!")
                else:
                    # Reset previous conversation
                    reset_conversation()

                    # Process new file
                    vectorstore, qa_chain, num_chunks, temp_dir = process_uploaded_file(uploaded_file)

                    if vectorstore and qa_chain:
                        st.session_state.vectorstore = vectorstore
                        st.session_state.qa_chain = qa_chain
                        st.session_state.processed_file = uploaded_file.name
                        st.success(f"✅ File processed successfully!\n\n📄 {num_chunks} chunks created")
                        st.balloons()

    # Show current document info
    if st.session_state.processed_file:
        st.markdown("---")
        st.subheader("📄 Current Document")
        st.info(f"**{st.session_state.processed_file}**")

        if st.button("🔄 Upload New Document"):
            reset_conversation()
            st.rerun()

    st.markdown("---")

    # Settings
    with st.expander("⚙️ Settings"):
        st.markdown("""
        **Supported Formats:**
        - PDF (.pdf)
        - Text (.txt)

        **Features:**
        - Semantic search
        - Context-aware responses
        - Source citations
        - Chat history
        """)

    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        This app uses:
        - **Google Gemini 1.5 Flash** for chat
        - **Google Embeddings** for vectors
        - **LangChain** for RAG
        - **FAISS** for vector storage
        - **Streamlit** for UI
        """)

# Main chat interface
st.title("💬 Chat with Your Document")

# Instructions if no document is loaded
if not st.session_state.processed_file:
    st.markdown("""
    <div style='text-align: center; padding: 3rem; background-color: #f0f2f6; border-radius: 10px; margin: 2rem 0;'>
        <h2>👋 Welcome to Document Chat!</h2>
        <p style='font-size: 1.2rem; margin-top: 1rem;'>
            Get started by uploading a PDF or text file in the sidebar ⬅️
        </p>
        <p style='color: #666; margin-top: 1rem;'>
            Once uploaded, you can ask questions and get AI-powered answers based on your document's content.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Show example questions
    st.subheader("💡 Example Questions You Can Ask:")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        - 📋 What is this document about?
        - 🔍 Summarize the main points
        - 📊 What are the key findings?
        """)

    with col2:
        st.markdown("""
        - ❓ Explain [specific concept]
        - 📌 What does it say about [topic]?
        - 🎯 Find information on [subject]
        """)

else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}:**")
                        st.text(source)
                        st.markdown("---")

    # Chat input
    if prompt := st.chat_input("Ask a question about your document..."):
        # Check if we have a processed document
        if not st.session_state.qa_chain:
            st.error("Please upload and process a document first!")
        else:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        # Query the chain
                        result = st.session_state.qa_chain({
                            "question": prompt,
                            "chat_history": st.session_state.chat_history
                        })

                        # Extract answer and sources
                        answer = result['answer']
                        sources = [doc.page_content[:300] + "..." for doc in result['source_documents']]

                        # Update chat history
                        st.session_state.chat_history.append((prompt, answer))

                        # Keep only last 5 exchanges
                        if len(st.session_state.chat_history) > 5:
                            st.session_state.chat_history = st.session_state.chat_history[-5:]

                        # Display answer
                        st.markdown(answer)

                        # Display sources
                        if sources:
                            with st.expander("📚 View Sources"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**Source {i}:**")
                                    st.text(source)
                                    st.markdown("---")

                        # Add assistant message to chat
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                    except Exception as e:
                        error_msg_lower = str(e).lower()

                        # Provide specific error messages based on error type
                        if "api key" in error_msg_lower or "authentication" in error_msg_lower or "401" in error_msg_lower or "403" in error_msg_lower:
                            error_display = "❌ **API Key Error**\n\nYour Google Gemini API key is invalid or missing. Please check the key in the sidebar."
                        elif "connection" in error_msg_lower or "network" in error_msg_lower or "timeout" in error_msg_lower:
                            error_display = "❌ **Connection Error**\n\nCannot reach Google Gemini servers. Check your internet connection and try again."
                        elif "rate limit" in error_msg_lower or "429" in error_msg_lower:
                            error_display = "❌ **Rate Limit**\n\nToo many requests. Please wait a moment and try again."
                        elif "quota" in error_msg_lower or "insufficient" in error_msg_lower:
                            error_display = "❌ **Quota Exceeded**\n\nYou've exceeded your Gemini quota. Check your usage at https://aistudio.google.com"
                        else:
                            error_display = f"❌ **Error**\n\n{str(e)}"

                        st.error(error_display)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_display
                        })

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

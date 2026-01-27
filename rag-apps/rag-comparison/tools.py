"""Retrieval tools for the agentic RAG system - Python 3.14 compatible version using FAISS."""

import os
import pickle
from typing import List, Dict
from duckduckgo_search import DDGS
import config


def simple_text_splitter(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Simple text splitter that doesn't require langchain."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - chunk_overlap

    return chunks


def load_text_file(file_path: str) -> Dict:
    """Load a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {
            "content": content,
            "metadata": {"source": file_path}
        }
    except Exception as e:
        return {"content": "", "metadata": {"source": file_path, "error": str(e)}}


def load_pdf_file(file_path: str) -> Dict:
    """Load a PDF file."""
    try:
        import pypdf
        content = []
        with open(file_path, 'rb') as f:
            pdf = pypdf.PdfReader(f)
            for page in pdf.pages:
                content.append(page.extract_text())
        return {
            "content": "\n\n".join(content),
            "metadata": {"source": file_path, "pages": len(content)}
        }
    except Exception as e:
        return {"content": "", "metadata": {"source": file_path, "error": str(e)}}


class LocalDocumentRetriever:
    """Searches local vector database using FAISS - Python 3.14 compatible."""

    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.is_initialized = False

    def _init_embeddings(self):
        """Initialize embeddings lazily."""
        if self.embeddings is None:
            from langchain_openai import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                openai_api_key=config.OPENAI_API_KEY
            )

    def initialize(self):
        """Load or create the vector database using FAISS."""
        if not os.path.exists(config.DOCUMENTS_DIR):
            os.makedirs(config.DOCUMENTS_DIR)
            return {"status": "created_dir", "message": f"Created {config.DOCUMENTS_DIR}. Please add documents."}

        # Initialize embeddings
        self._init_embeddings()

        # Load documents manually
        documents = []

        for filename in os.listdir(config.DOCUMENTS_DIR):
            file_path = os.path.join(config.DOCUMENTS_DIR, filename)

            if not os.path.isfile(file_path):
                continue

            if filename.endswith('.pdf'):
                doc = load_pdf_file(file_path)
                if doc["content"]:
                    documents.append(doc)
            elif filename.endswith(('.txt', '.md')):
                doc = load_text_file(file_path)
                if doc["content"]:
                    documents.append(doc)

        if not documents:
            return {"status": "no_docs", "message": f"No documents found in {config.DOCUMENTS_DIR}"}

        # Split documents into chunks
        chunks = []
        for doc in documents:
            text_chunks = simple_text_splitter(
                doc["content"],
                chunk_size=config.CHUNK_SIZE,
                chunk_overlap=config.CHUNK_OVERLAP
            )
            for i, chunk_text in enumerate(text_chunks):
                chunks.append({
                    "page_content": chunk_text,
                    "metadata": {**doc["metadata"], "chunk": i}
                })

        # Create FAISS vector store
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document

            # Convert to Document objects
            docs = [Document(page_content=c["page_content"], metadata=c["metadata"]) for c in chunks]

            # Create FAISS index
            self.vector_store = FAISS.from_documents(
                documents=docs,
                embedding=self.embeddings
            )

            # Save to disk
            if not os.path.exists(config.CHROMA_PERSIST_DIR):
                os.makedirs(config.CHROMA_PERSIST_DIR)

            faiss_path = os.path.join(config.CHROMA_PERSIST_DIR, "faiss_index")
            self.vector_store.save_local(faiss_path)

            self.is_initialized = True
            return {
                "status": "success",
                "message": f"Initialized with {len(documents)} documents, {len(chunks)} chunks"
            }
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "message": f"Error creating vector store: {str(e)}\n{traceback.format_exc()}"
            }

    def load_existing(self):
        """Load existing FAISS vector database."""
        faiss_path = os.path.join(config.CHROMA_PERSIST_DIR, "faiss_index")

        if os.path.exists(faiss_path):
            try:
                self._init_embeddings()
                from langchain_community.vectorstores import FAISS

                self.vector_store = FAISS.load_local(
                    faiss_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.is_initialized = True
                return {"status": "loaded", "message": "Loaded existing vector database"}
            except Exception as e:
                import traceback
                return {"status": "error", "message": f"Error loading database: {str(e)}\n{traceback.format_exc()}"}
        return {"status": "not_found", "message": "No existing database found"}

    def search(self, query: str, k: int = None) -> Dict:
        """Search local documents."""
        if not self.is_initialized:
            return {
                "success": False,
                "error": "Vector database not initialized",
                "documents": []
            }

        k = k or config.MAX_DOCS_PER_RETRIEVAL

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)

            documents = []
            for doc, score in results:
                documents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": float(1 / (1 + score))  # Convert distance to similarity
                })

            return {
                "success": True,
                "documents": documents,
                "count": len(documents)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }


class WebSearchRetriever:
    """Searches the web using DuckDuckGo."""

    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, max_results: int = None) -> Dict:
        """Search the web."""
        max_results = max_results or config.MAX_DOCS_PER_RETRIEVAL

        try:
            results = list(self.ddgs.text(query, max_results=max_results))

            documents = []
            for result in results:
                documents.append({
                    "content": f"{result.get('title', '')}\n\n{result.get('body', '')}",
                    "metadata": {
                        "source": result.get('href', ''),
                        "title": result.get('title', '')
                    },
                    "url": result.get('href', '')
                })

            return {
                "success": True,
                "documents": documents,
                "count": len(documents)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "documents": []
            }


# Tool registry for the agent
TOOLS = {
    "search_local_docs": {
        "name": "search_local_docs",
        "description": "Search through local documents in the vector database. Use this for questions about your own documents, internal knowledge, or previously uploaded content.",
        "parameters": {
            "query": "The search query to find relevant documents"
        }
    },
    "search_web": {
        "name": "search_web",
        "description": "Search the web using DuckDuckGo. Use this for current events, general knowledge, or when local documents don't have the answer.",
        "parameters": {
            "query": "The search query to find relevant web pages"
        }
    }
}

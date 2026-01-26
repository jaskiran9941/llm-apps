"""Retrieval tools for the agentic RAG system."""

import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from duckduckgo_search import DDGS
import config


class LocalDocumentRetriever:
    """Searches local vector database."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY
        )
        self.vector_store = None
        self.is_initialized = False

    def initialize(self):
        """Load or create the vector database."""
        if not os.path.exists(config.DOCUMENTS_DIR):
            os.makedirs(config.DOCUMENTS_DIR)
            return {"status": "created_dir", "message": f"Created {config.DOCUMENTS_DIR}. Please add documents."}

        # Load documents
        documents = []

        # Load PDFs
        if any(f.endswith('.pdf') for f in os.listdir(config.DOCUMENTS_DIR)):
            pdf_loader = DirectoryLoader(
                config.DOCUMENTS_DIR,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            documents.extend(pdf_loader.load())

        # Load text files
        if any(f.endswith(('.txt', '.md')) for f in os.listdir(config.DOCUMENTS_DIR)):
            text_loader = DirectoryLoader(
                config.DOCUMENTS_DIR,
                glob="**/*.{txt,md}",
                loader_cls=TextLoader
            )
            documents.extend(text_loader.load())

        if not documents:
            return {"status": "no_docs", "message": f"No documents found in {config.DOCUMENTS_DIR}"}

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        splits = text_splitter.split_documents(documents)

        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
            collection_name=config.COLLECTION_NAME
        )

        self.is_initialized = True
        return {
            "status": "success",
            "message": f"Initialized with {len(documents)} documents, {len(splits)} chunks"
        }

    def load_existing(self):
        """Load existing vector database."""
        if os.path.exists(config.CHROMA_PERSIST_DIR):
            self.vector_store = Chroma(
                persist_directory=config.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings,
                collection_name=config.COLLECTION_NAME
            )
            self.is_initialized = True
            return {"status": "loaded", "message": "Loaded existing vector database"}
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
                    "relevance_score": float(1 - score)  # Convert distance to similarity
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

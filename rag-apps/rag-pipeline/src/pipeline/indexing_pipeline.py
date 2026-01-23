"""
Document indexing pipeline.

Orchestrates the full indexing process:
PDF → Load → Preprocess → Chunk → Embed → Store

This pipeline is responsible for preparing documents for retrieval.
"""

from pathlib import Path
from typing import Optional
from src.models import IndexingResult
from src.document_processing.pdf_loader import PDFLoader
from src.document_processing.preprocessor import TextPreprocessor
from src.document_processing.chunker import BaseChunker
from src.embeddings.embedding_manager import BaseEmbeddingManager
from src.vector_store.base_store import BaseVectorStore
from src.utils.logger import EducationalLogger
from src.utils.validators import validate_file_upload
import time

logger = EducationalLogger(__name__)


class IndexingPipeline:
    """
    End-to-end document indexing pipeline.

    This pipeline transforms raw PDFs into searchable vector embeddings:

    1. Load PDF → Extract text with page numbers
    2. Preprocess → Clean and normalize text
    3. Chunk → Split into manageable pieces
    4. Embed → Generate vector embeddings
    5. Store → Save to vector database

    Educational Note:
    ----------------
    The indexing pipeline is run once per document. It's important to:
    - Track costs (embedding generation costs money)
    - Handle errors gracefully (bad PDFs, extraction failures)
    - Provide feedback (show progress, statistics)

    Design decisions:
    - Modular: Each component is swappable via dependency injection
    - Observable: Extensive logging for debugging
    - Resilient: Error handling at each step
    """

    def __init__(
        self,
        pdf_loader: PDFLoader,
        preprocessor: TextPreprocessor,
        chunker: BaseChunker,
        embedding_manager: BaseEmbeddingManager,
        vector_store: BaseVectorStore
    ):
        """
        Initialize indexing pipeline.

        Args:
            pdf_loader: Component for loading PDFs
            preprocessor: Component for text preprocessing
            chunker: Component for text chunking
            embedding_manager: Component for embedding generation
            vector_store: Component for vector storage
        """
        self.pdf_loader = pdf_loader
        self.preprocessor = preprocessor
        self.chunker = chunker
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

        logger.log_step(
            "PIPELINE_INIT",
            "Indexing pipeline initialized",
            "Ready to process and index documents"
        )

    def index_document(
        self,
        file_path: Path,
        doc_id: Optional[str] = None
    ) -> IndexingResult:
        """
        Index a single document.

        This is the main entry point for document indexing.

        Args:
            file_path: Path to PDF file
            doc_id: Optional document ID (defaults to filename)

        Returns:
            IndexingResult with statistics and status
        """
        logger.info(f"{'='*60}")
        logger.info(f"Starting indexing pipeline for: {file_path.name}")
        logger.info(f"{'='*60}")

        start_time = time.time()
        total_cost = 0.0

        try:
            # Validate file
            validate_file_upload(file_path)

            # Step 1: Load PDF
            logger.log_step(
                "STEP 1",
                "Loading PDF",
                "Extracting text while preserving page numbers"
            )
            document = self.pdf_loader.load(file_path, doc_id)

            if not document.text.strip():
                raise ValueError("No text extracted from PDF")

            # Step 2: Preprocess
            logger.log_step(
                "STEP 2",
                "Preprocessing text",
                "Cleaning and normalizing for better embeddings"
            )
            document.text = self.preprocessor.preprocess(document.text)

            # Step 3: Chunk
            logger.log_step(
                "STEP 3",
                "Chunking document",
                f"Splitting into chunks for embedding and retrieval"
            )
            chunks = self.chunker.chunk(document)

            if not chunks:
                raise ValueError("No chunks created from document")

            logger.info(f"Created {len(chunks)} chunks")

            # Step 4: Generate embeddings
            logger.log_step(
                "STEP 4",
                f"Generating embeddings for {len(chunks)} chunks",
                "Converting text to vector representations"
            )

            embeddings = self.embedding_manager.embed_chunks(chunks)

            # Calculate embedding cost
            if hasattr(self.embedding_manager, 'total_cost'):
                embedding_cost = self.embedding_manager.total_cost
                total_cost += embedding_cost

            # Step 5: Store in vector database
            logger.log_step(
                "STEP 5",
                "Storing in vector database",
                "Saving embeddings for similarity search"
            )

            success = self.vector_store.add_documents(
                chunks=chunks,
                embeddings=embeddings
            )

            if not success:
                raise Exception("Failed to store documents in vector database")

            # Calculate total time
            total_time = time.time() - start_time

            logger.info(f"{'='*60}")
            logger.info(f"✅ Indexing completed successfully!")
            logger.info(f"   - Document: {file_path.name}")
            logger.info(f"   - Chunks: {len(chunks)}")
            logger.info(f"   - Cost: ${total_cost:.4f}")
            logger.info(f"   - Time: {total_time:.2f}s")
            logger.info(f"{'='*60}")

            # Return success result
            return IndexingResult(
                doc_id=document.doc_id,
                success=True,
                num_chunks=len(chunks),
                num_embeddings=len(embeddings),
                cost=total_cost,
                metadata={
                    "filename": file_path.name,
                    "source_path": str(file_path),
                    "num_pages": document.metadata.get("num_pages", 0),
                    "chunker_type": type(self.chunker).__name__,
                    "embedding_model": self.embedding_manager.model,
                    "processing_time": round(total_time, 2)
                }
            )

        except Exception as e:
            logger.error(f"❌ Indexing failed: {str(e)}")

            # Return failure result
            return IndexingResult(
                doc_id=doc_id or file_path.stem,
                success=False,
                num_chunks=0,
                num_embeddings=0,
                cost=total_cost,
                error_message=str(e),
                metadata={
                    "filename": file_path.name,
                    "source_path": str(file_path)
                }
            )

    def index_multiple(
        self,
        file_paths: list[Path]
    ) -> list[IndexingResult]:
        """
        Index multiple documents.

        Args:
            file_paths: List of PDF file paths

        Returns:
            List of IndexingResult objects
        """
        logger.info(f"Indexing {len(file_paths)} documents...")

        results = []
        for file_path in file_paths:
            result = self.index_document(file_path)
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r.success)
        total_chunks = sum(r.num_chunks for r in results)
        total_cost = sum(r.cost for r in results)

        logger.info(f"\n{'='*60}")
        logger.info(f"Batch Indexing Summary:")
        logger.info(f"   - Documents processed: {len(file_paths)}")
        logger.info(f"   - Successful: {successful}")
        logger.info(f"   - Failed: {len(file_paths) - successful}")
        logger.info(f"   - Total chunks: {total_chunks}")
        logger.info(f"   - Total cost: ${total_cost:.4f}")
        logger.info(f"{'='*60}\n")

        return results

    def reindex_document(
        self,
        file_path: Path,
        doc_id: str
    ) -> IndexingResult:
        """
        Reindex an existing document.

        Deletes old chunks and creates new ones. Useful when:
        - Changing chunk size
        - Updating document content
        - Switching chunking strategy

        Args:
            file_path: Path to PDF file
            doc_id: Existing document ID to replace

        Returns:
            IndexingResult
        """
        logger.info(f"Reindexing document: {doc_id}")

        # Delete existing chunks
        self.vector_store.delete_document(doc_id)
        logger.info(f"Deleted old chunks for {doc_id}")

        # Index with new settings
        return self.index_document(file_path, doc_id)

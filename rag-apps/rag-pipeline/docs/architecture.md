# System Architecture

## Overview

This RAG system follows a modular, extensible architecture based on well-established design patterns. The goal is to create a learning platform that's easy to understand while being production-ready and extensible for future enhancements.

## Design Principles

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Extensibility**: Easy to add new implementations (chunkers, retrievers, etc.)
3. **Testability**: Components are independently testable
4. **Observability**: Comprehensive logging and metrics
5. **Type Safety**: Pydantic models ensure data validity
6. **Configuration-Driven**: Easy to adjust parameters without code changes

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI Layer                        │
│  (app.py, components/document_manager, query_interface, etc.)  │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────┐          ┌────────────────────────┐
│  Indexing Pipeline     │          │   Query Pipeline       │
│  - Orchestrates        │          │   - Orchestrates       │
│    document ingestion  │          │     query execution    │
└────────┬───────────────┘          └──────────┬─────────────┘
         │                                     │
         ▼                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Components                           │
├────────────────┬──────────────┬──────────────┬──────────────┤
│ Document       │ Embeddings   │ Vector Store │ Generation   │
│ Processing     │              │              │              │
│                │              │              │              │
│ - PDFLoader    │ - OpenAI     │ - ChromaDB   │ - LLM Mgr    │
│ - Preprocessor │   Embeddings │              │ - RAG Gen    │
│ - Chunker      │              │              │              │
└────────────────┴──────────────┴──────────────┴──────────────┘
         │                │              │             │
         └────────────────┴──────────────┴─────────────┘
                          │
                          ▼
         ┌─────────────────────────────────────┐
         │        Foundation Layer              │
         │  - Models (Pydantic)                 │
         │  - Configuration                     │
         │  - Utilities (metrics, logging)      │
         └─────────────────────────────────────┘
```

## Component Details

### 1. Data Models (`src/models.py`)

**Purpose**: Define data contracts between components

**Models**:
- `Document`: Raw document with metadata
- `Chunk`: Text chunk with source tracking
- `SearchResult`: Retrieved chunk with similarity score
- `RetrievedChunk`: Enriched chunk for UI display
- `QueryResult`: Complete query result with metadata
- `IndexingResult`: Indexing operation result

**Benefits**:
- Type safety with Pydantic validation
- Automatic serialization/deserialization
- Clear API contracts
- Self-documenting code

### 2. Configuration (`config/`)

**settings.py**: Centralized configuration
- Environment variable support
- Sensible defaults
- Validation on startup
- Easy parameter tuning

**prompts.py**: Prompt templates
- System prompts for LLM behavior
- RAG-specific prompt templates
- Context formatting functions
- Educational prompts

**Benefits**:
- Single source of truth
- Easy experimentation
- Environment-specific configs
- No hardcoded values

### 3. Document Processing

#### PDFLoader (`src/document_processing/pdf_loader.py`)

**Responsibilities**:
- Extract text from PDFs
- Preserve page numbers
- Handle multiple PDF libraries (pdfplumber, PyPDF2)
- Error handling for corrupted files

**Design Pattern**: Adapter
- Wraps PDF libraries with consistent interface
- Fallback mechanism if primary method fails

#### Preprocessor (`src/document_processing/preprocessor.py`)

**Responsibilities**:
- Normalize whitespace
- Remove noise (headers, footers)
- Preserve semantic structure
- Clean special characters

**Configurability**:
- Enable/disable specific cleaning steps
- Preserve vs remove elements
- Domain-specific customization

#### Chunker (`src/document_processing/chunker.py`)

**Responsibilities**:
- Split documents into chunks
- Maintain metadata (page numbers, doc IDs)
- Add overlap for context continuity
- Generate unique chunk IDs

**Design Pattern**: Strategy
- `BaseChunker`: Abstract interface
- `FixedSizeChunker`: Sentence-aware fixed size
- `CharacterChunker`: Simple character-based
- Easy to add: `SemanticChunker`, `RecursiveChunker` (Project 2)

**Key Abstraction**:
```python
class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        pass
```

**Benefits**:
- Swap chunking strategies without changing pipelines
- Compare different approaches
- Add new strategies easily

### 4. Embeddings

#### BaseEmbeddingManager (`src/embeddings/embedding_manager.py`)

**Responsibilities**:
- Define embedding interface
- Enable provider swapping

**Key Methods**:
- `embed_text()`: Single text
- `embed_batch()`: Multiple texts (efficient)
- `get_embedding_dimension()`: Vector size

#### OpenAIEmbeddingManager (`src/embeddings/openai_embeddings.py`)

**Responsibilities**:
- Call OpenAI Embeddings API
- Batch processing for efficiency
- Retry logic for reliability
- Cost tracking
- Caching for performance

**Features**:
- Automatic retry with exponential backoff
- Batch size configuration
- Token counting
- Cost calculation

**Extensibility**: Easy to add other providers
- `CohereEmbeddingManager`
- `SentenceTransformerEmbeddingManager`
- `HuggingFaceEmbeddingManager`

### 5. Vector Store

#### BaseVectorStore (`src/vector_store/base_store.py`)

**Responsibilities**:
- Define vector storage interface
- Enable database swapping

**Key Methods**:
- `add_documents()`: Store embeddings
- `search()`: Similarity search
- `delete_document()`: Remove chunks
- `list_documents()`: Get all docs
- `get_stats()`: Usage statistics

#### ChromaVectorStore (`src/vector_store/chroma_store.py`)

**Responsibilities**:
- ChromaDB integration
- Persistent storage
- Metadata filtering
- Distance metric configuration

**Features**:
- Cosine similarity (default)
- Metadata filtering support
- Automatic collection management
- Stats and monitoring

**Extensibility**: Easy to add other stores
- `PineconeVectorStore`
- `WeaviateVectorStore`
- `FAISSVectorStore`

### 6. Retrieval

#### BaseRetriever (`src/retrieval/base_retriever.py`)

**Responsibilities**:
- Define retrieval interface
- Enable strategy swapping

**Key Methods**:
- `retrieve()`: Get relevant chunks
- `get_retriever_info()`: Configuration details

#### SemanticRetriever (`src/retrieval/semantic_retriever.py`)

**Responsibilities**:
- Embed query
- Search vector store
- Filter by similarity threshold
- Format results

**Process**:
1. Query → Embedding
2. Vector search (top-k)
3. Score filtering
4. Convert to RetrievedChunks

**Future Retrievers** (Projects 2-3):
- `HybridRetriever`: Semantic + BM25
- `ReRankingRetriever`: Two-stage retrieval
- `ContextualRetriever`: Parent-child chunks

### 7. Generation

#### LLMManager (`src/generation/llm_manager.py`)

**Responsibilities**:
- OpenAI API integration
- Token counting
- Cost calculation
- Retry logic
- Usage tracking

**Features**:
- Temperature control
- Max tokens configuration
- Automatic retry
- Comprehensive metrics

#### RAGGenerator (`src/generation/rag_generator.py`)

**Responsibilities**:
- Format context from chunks
- Construct RAG prompts
- Generate answers
- Track metadata

**Two Modes**:
1. **With RAG**: Use retrieved context
2. **Without RAG**: Pure LLM (for comparison)

**Process**:
1. Format chunks → context string
2. Construct prompt (system + context + query)
3. Call LLM
4. Return structured result

### 8. Pipelines

#### IndexingPipeline (`src/pipeline/indexing_pipeline.py`)

**Responsibilities**:
- Orchestrate document indexing
- Error handling
- Progress tracking
- Statistics collection

**Flow**:
```
PDF → Load → Preprocess → Chunk → Embed → Store
```

**Features**:
- Step-by-step logging
- Cost tracking
- Error recovery
- Batch processing support

#### QueryPipeline (`src/pipeline/query_pipeline.py`)

**Responsibilities**:
- Orchestrate query execution
- RAG vs non-RAG comparison
- Performance tracking

**Flow**:
```
Query → Embed → Retrieve → Format → Generate → Return
```

**Features**:
- Three query modes (RAG, non-RAG, comparison)
- Comprehensive logging
- Cost and latency tracking
- Metadata collection

### 9. Utilities

#### Metrics (`src/utils/metrics.py`)

**Responsibilities**:
- Token counting (tiktoken)
- Cost calculation
- Latency measurement
- Metrics collection

**Features**:
- `count_tokens()`: Accurate token counting
- `calculate_embedding_cost()`: Embedding pricing
- `calculate_llm_cost()`: LLM pricing
- `Timer`: Context manager for timing
- `MetricsCollector`: Aggregate statistics

#### Logger (`src/utils/logger.py`)

**Responsibilities**:
- Structured logging
- Educational context
- Step tracking

**Features**:
- `EducationalLogger`: Logs with explanations
- `log_step()`: Track pipeline steps
- `log_metric()`: Track important metrics
- Configurable levels

#### Validators (`src/utils/validators.py`)

**Responsibilities**:
- Input validation
- Security (sanitize filenames)
- Configuration validation

**Validations**:
- File uploads (size, type, existence)
- Chunk configuration
- Query input
- Document IDs

### 10. UI Components

#### Main App (`ui/app.py`)

**Responsibilities**:
- Streamlit page configuration
- Component initialization
- Tab organization
- State management

**Tabs**:
1. Upload Documents
2. Query Interface
3. Experiments
4. Documentation

#### UI Components (`ui/components/`)

**document_manager.py**:
- Upload interface
- Document list
- Delete functionality
- Storage statistics

**query_interface.py**:
- Query input
- Results display
- Retrieved chunks visualization
- RAG vs non-RAG comparison

**config_panel.py**:
- Parameter sliders
- Cost calculator
- System information
- Educational tooltips

## Data Flow

### Indexing Flow

```
1. User uploads PDF
   ↓
2. UI calls IndexingPipeline.index_document()
   ↓
3. PDFLoader extracts text
   ↓
4. TextPreprocessor cleans text
   ↓
5. Chunker splits into chunks
   ↓
6. EmbeddingManager generates embeddings
   ↓
7. VectorStore saves embeddings + metadata
   ↓
8. IndexingResult returned to UI
   ↓
9. Statistics displayed to user
```

### Query Flow

```
1. User enters question
   ↓
2. UI calls QueryPipeline.query()
   ↓
3. Retriever:
   - Embeds query
   - Searches vector store
   - Returns top-k chunks
   ↓
4. RAGGenerator:
   - Formats context
   - Constructs prompt
   - Calls LLM
   ↓
5. QueryResult returned to UI
   ↓
6. Answer, chunks, metadata displayed
```

## Extension Points

### Adding New Chunking Strategy

1. Create class inheriting from `BaseChunker`
2. Implement `chunk()` method
3. Use in `IndexingPipeline`

```python
class SemanticChunker(BaseChunker):
    def chunk(self, document: Document) -> List[Chunk]:
        # Your implementation
        pass
```

### Adding New Retrieval Strategy

1. Create class inheriting from `BaseRetriever`
2. Implement `retrieve()` method
3. Use in `QueryPipeline`

```python
class HybridRetriever(BaseRetriever):
    def retrieve(self, query: str, top_k: int) -> List[RetrievedChunk]:
        # Semantic + BM25 combination
        pass
```

### Adding New Vector Store

1. Create class inheriting from `BaseVectorStore`
2. Implement all abstract methods
3. Use in pipelines

```python
class PineconeVectorStore(BaseVectorStore):
    # Implement interface
    pass
```

## Dependencies

### Core Dependencies

- **streamlit**: Web UI framework
- **openai**: LLM and embeddings
- **chromadb**: Vector storage
- **pydantic**: Data validation
- **python-dotenv**: Environment management

### Document Processing

- **PyPDF2**: PDF extraction
- **pdfplumber**: Alternative PDF extraction

### Utilities

- **tiktoken**: Token counting
- **tenacity**: Retry logic

### Testing

- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking support

## Performance Considerations

### Optimization Strategies

1. **Caching**:
   - Embedding cache (avoid re-embedding same text)
   - Streamlit component caching
   - Query result caching (future)

2. **Batching**:
   - Batch embed multiple chunks
   - Reduces API round trips
   - Lower costs

3. **Async Operations** (future):
   - Parallel chunk processing
   - Concurrent API calls
   - Faster indexing

4. **Vector Store Optimization**:
   - Appropriate similarity metric
   - Index configuration
   - Batch operations

### Scalability

**Current Limits**:
- Documents: 1000s (ChromaDB local)
- Chunks: 100,000s
- Queries: OpenAI rate limits

**Future Improvements**:
- Cloud vector DB (Pinecone)
- Distributed processing
- Query caching
- Load balancing

## Security

### Current Measures

1. **Input Validation**:
   - File type checking
   - Size limits
   - Filename sanitization

2. **API Key Management**:
   - Environment variables
   - Not in code
   - .env in .gitignore

3. **Data Isolation**:
   - Per-collection storage
   - Metadata filtering
   - Document deletion

### Future Enhancements

- User authentication
- Rate limiting
- Audit logging
- Encrypted storage

## Monitoring and Observability

### Current Features

1. **Logging**:
   - Structured logging
   - Educational context
   - Step tracking

2. **Metrics**:
   - Token usage
   - Costs
   - Latency
   - Success rates

3. **UI Feedback**:
   - Progress bars
   - Statistics
   - Error messages

### Future Enhancements

- Prometheus metrics
- Application logging
- Performance dashboards
- Alert system

## Testing Strategy

### Unit Tests

- Individual component testing
- Mocked dependencies
- Fast execution

### Integration Tests

- End-to-end flows
- Real components
- Example documents

### Test Coverage

- Target: 80%+
- Critical paths: 100%
- UI: Manual testing

## Deployment

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run ui/app.py
```

### Production Considerations

- Docker containerization
- Environment-specific configs
- Secrets management
- Monitoring setup
- Backup strategy

## Future Architecture

### Projects 2-4 Will Add

1. **Advanced Chunking**:
   - Semantic chunker
   - Recursive chunker
   - Structure-aware chunker

2. **Hybrid Retrieval**:
   - BM25 + semantic
   - Query rewriting
   - Re-ranking

3. **Context Enhancement**:
   - Parent-child chunks
   - Sliding windows
   - Query expansion

4. **Production Features**:
   - Caching layer
   - Async processing
   - Multi-user support
   - Analytics dashboard

The architecture is designed to accommodate these enhancements with minimal changes to existing code.

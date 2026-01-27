# Demo Script for Conversational RAG

Use this script to demonstrate the key features of the Conversational RAG application.

## Setup (Before Demo)

1. Have the app running: `streamlit run app.py`
2. Upload a sample PDF document (e.g., a research paper or technical documentation)
3. Process the document with default settings

## Feature Demonstrations

### 1. Basic Question Answering

**Show**: How the system answers straightforward questions

```
You: What is the main topic of this document?
You: What are the key findings mentioned?
You: Who are the authors?
```

**Point Out**:
- Clear, grounded answers
- Source citations in expandable sections
- Page numbers and relevance scores

### 2. Follow-up Questions (Core Feature)

**Show**: Context-aware conversation flow

```
You: What methodology was used in this research?
Bot: [Explains the methodology]

You: Tell me more about that
Bot: [Provides additional methodology details]

You: What else did they try?
Bot: [Mentions alternative approaches]

You: Why did they choose that approach?
Bot: [Explains the reasoning]
```

**Point Out**:
- "Tell me more" understands context
- No need to repeat the topic
- Natural conversation flow
- Maintains coherence across turns

### 3. Query Enhancement Visualization

**Show**: How vague follow-ups are enhanced

```
You: What are the limitations?
Bot: [Lists limitations]

You: clarify the first one
Bot: [Elaborates on first limitation]
```

**Point Out**:
- "Clarify the first one" refers to previous answer
- System maintains conversation context
- Query enhancement happens automatically

### 4. Hybrid Retrieval

**Demonstrate**: Adjust the alpha slider

**Scenario 1: Semantic (alpha = 1.0)**
```
You: What concepts are similar to X?
```
→ Shows semantic understanding

**Scenario 2: Keyword (alpha = 0.0)**
```
You: Find mentions of "neural network"
```
→ Shows exact term matching

**Scenario 3: Balanced (alpha = 0.5)**
```
You: Explain the neural network architecture
```
→ Shows best of both worlds

**Point Out**:
- Different retrieval strategies
- Configurable balance
- RRF fusion combines results

### 5. Source Citation

**Show**: Expandable source panels

**Point Out**:
- Each answer shows retrieved chunks
- Page numbers for verification
- Relevance scores (0-1)
- Can trace answers back to source

### 6. Conversation Management

**Actions**:
1. Show conversation history in sidebar (message count)
2. Ask several questions to build history
3. Click "Clear Conversation"
4. Start fresh conversation

**Point Out**:
- Persistent conversation state
- Easy reset for new topics
- Statistics tracking

### 7. Settings Configuration

**Walk Through**:

**Chunk Size**: 256 vs 1024
- Small: More precise, more chunks
- Large: More context, fewer chunks

**Top K**: 3 vs 10
- Fewer: Faster, focused
- More: Comprehensive, slower

**Model Selection**: GPT-4 vs GPT-3.5
- GPT-4: Better quality
- GPT-3.5: Faster, cheaper

## Advanced Scenarios

### Multi-turn Deep Dive

```
You: What problem does this paper solve?
Bot: [Explains the problem]

You: Why is that important?
Bot: [Explains significance]

You: What solutions existed before?
Bot: [Describes prior work]

You: How is this different?
Bot: [Compares approaches]

You: What are the results?
Bot: [Presents findings]
```

**Point Out**:
- Natural conversation flow
- Each question builds on previous
- System maintains full context

### Comparison Questions

```
You: What are the advantages mentioned?
Bot: [Lists advantages]

You: What about disadvantages?
Bot: [Lists disadvantages]

You: Compare them
Bot: [Provides comparison]
```

## Common Follow-up Patterns Detected

Show that these all work:
- "tell me more"
- "what else?"
- "clarify that"
- "explain that"
- "elaborate"
- "continue"
- "what about [previous topic]?"
- "how so?"
- "why is that?"

## Troubleshooting Demo

### What Happens When Context Isn't Enough?

```
You: What does the author think about quantum computing?
```

If not in document:
```
Bot: "The provided context doesn't contain information about quantum computing..."
```

**Point Out**: System admits when it doesn't know

### Grounding in Sources

Show that answers reference the sources:
```
Bot: "According to Source 2 on page 5..."
Bot: "As mentioned in the methodology section..."
```

## Key Takeaways for Audience

1. **Natural Conversations**: Chat like you would with a person
2. **Follow-up Aware**: No need to repeat context
3. **Grounded Answers**: Always based on document content
4. **Transparent**: See exactly which sources were used
5. **Configurable**: Adjust settings for your use case

## Technical Deep Dive (For Technical Audiences)

### Architecture Overview
- Hybrid retrieval (semantic + keyword)
- Reciprocal Rank Fusion (RRF)
- Query enhancement with conversation history
- GPT-4 with conversation-aware prompts

### Code Walkthrough
1. Query enhancement logic (conversational_retriever.py)
2. Hybrid fusion algorithm (hybrid_fusion.py)
3. System prompt design (conversational_generator.py)

### Metrics to Discuss
- Retrieval scores (cosine similarity + BM25)
- RRF fusion scores
- Number of chunks processed
- Conversation length

## Q&A Preparation

**Q: Does it remember previous conversations?**
A: Currently session-based. Each session is independent. Can be extended to persistent storage.

**Q: Can it handle multiple documents?**
A: Currently single document. Architecture supports multiple with minor changes.

**Q: What about images in PDFs?**
A: Text-only currently. Vision RAG is a future enhancement.

**Q: How accurate is it?**
A: Always grounded in document content. Shows sources for verification.

**Q: What's the cost?**
A: Depends on document size and usage. Embeddings are one-time, chat is per-query.

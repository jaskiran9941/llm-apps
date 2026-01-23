# Stakeholder Router Guardrail System

An advanced AI routing system demonstrating JSON-based classification, OOD detection, and ambiguity handling for product development queries.

## Overview

The Stakeholder Router is a learning project that showcases:

- **JSON Classification**: Reliable categorization using structured outputs
- **Routing & Orchestration**: Smart routing to domain-specific experts
- **OOD Detection**: Guardrails to reject inappropriate or unrelated queries
- **Ambiguity Handling**: Multiple strategies for handling unclear queries
- **Expert Sub-Agents**: Specialized domain experts (Pricing & UX)
- **Transparent AI UX**: Observable routing decisions and AI behavior

## Key Features

### 1. Multi-Layer Routing

```
User Query
  → OOD Detection (Guardrail)
    → JSON Classification
      → Ambiguity Handling
        → Expert Routing
          → Response Aggregation
```

### 2. Confidence-Based Routing

- **High Confidence (>0.8)**: Route directly to single expert
- **Medium Confidence (0.5-0.8)**: Handle based on ambiguity strategy
- **Low Confidence (<0.5)**: Treat as ambiguous, ask clarification

### 3. Ambiguity Strategies

- **Ask Clarifying**: Present questions to disambiguate before routing
- **Route Both**: Send to both experts and compare perspectives
- **Pick Primary**: Use keyword heuristics to choose most likely expert

## Architecture

### Components

```
stakeholder-router/
├── src/
│   ├── config/
│   │   └── settings.py              # Pydantic configuration
│   ├── router/
│   │   ├── classifier.py            # JSON-based classifier
│   │   ├── orchestrator.py          # Main routing logic
│   │   └── guardrails.py            # OOD & ambiguity handling
│   ├── experts/
│   │   ├── base_expert.py           # Base expert class
│   │   ├── pricing_expert.py        # Pricing domain expert
│   │   └── ux_expert.py             # UX design expert
│   └── utils/
│       ├── llm_client.py            # LLM abstraction
│       └── prompts.py               # Centralized prompts
├── app.py                           # Streamlit UI
├── examples/
│   ├── test_queries.json            # Test cases
│   └── sabotage_scenarios.json      # Edge cases
└── tests/                           # Unit tests
```

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key

### Installation

```bash
# Navigate to project directory
cd stakeholder-router

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the Application

```bash
# Start Streamlit UI
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src
```

## Usage Examples

### Clear Pricing Query

**Input:** "How should we price our B2B SaaS product?"

**Expected Flow:**
1. Passes OOD detection
2. Classified as "pricing" with high confidence (>0.8)
3. Routed to Pricing Expert
4. Returns pricing strategy advice

### Clear UX Query

**Input:** "How can we improve the onboarding flow?"

**Expected Flow:**
1. Passes OOD detection
2. Classified as "ux" with high confidence (>0.8)
3. Routed to UX Expert
4. Returns UX design recommendations

### Ambiguous Query

**Input:** "How do we design the pricing page?"

**Expected Flow:**
1. Passes OOD detection
2. Classified as "ambiguous" (confidence 0.5-0.7)
3. Ambiguity handling based on strategy:
   - **ask_clarifying**: Presents questions like:
     - "Are you asking about visual design and layout?"
     - "Or about pricing tier structure and display?"
   - **route_both**: Routes to both experts, shows both perspectives
   - **pick_primary**: Analyzes keywords, picks most likely expert

### OOD Query

**Input:** "What's the weather today?"

**Expected Flow:**
1. Detected as OOD (unrelated)
2. Returns: "I'm designed to help with product pricing and UX design questions..."
3. Query rejected, no expert routing

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional (defaults shown)
DEFAULT_ROUTING_STRATEGY=ask_clarifying
CONFIDENCE_THRESHOLD_HIGH=0.8
CONFIDENCE_THRESHOLD_LOW=0.5
ENABLE_OOD_DETECTION=true
ALLOW_MULTI_EXPERT=true
DEFAULT_MODEL=claude-sonnet-4-20250514
```

### Runtime Configuration (via Streamlit UI)

- **Ambiguity Strategy**: Choose between ask_clarifying, route_both, pick_primary
- **OOD Detection**: Enable/disable pre-routing guardrail
- **Confidence Thresholds**: Adjust high/low confidence boundaries

## Key Learning Objectives

### 1. JSON-Based Classification

The system uses Claude with structured prompts to enforce JSON-only responses:

```python
{
  "category": "pricing" | "ux" | "ambiguous" | "ood",
  "confidence": 0.0-1.0,
  "reasoning": "Explanation of decision",
  "clarifying_questions": ["Optional questions if ambiguous"]
}
```

**Benefits:**
- Reliable, parseable outputs
- No hallucination in routing decisions
- Transparent reasoning
- Confidence calibration

### 2. OOD Detection

Two-layer approach:

1. **Keyword Pre-Filter**: Fast rejection of obvious OOD queries
2. **LLM-Based Detection**: Nuanced detection for edge cases

**Categories:**
- `unrelated`: Completely off-topic
- `jailbreak`: Prompt injection attempts
- `inappropriate`: Harmful or policy-violating requests

### 3. Ambiguity Handling

Demonstrates different UX approaches to ambiguous queries:

| Strategy | When to Use | User Experience |
|----------|-------------|-----------------|
| ask_clarifying | User clarity is paramount | More interactive, requires follow-up |
| route_both | Comprehensive answers needed | More tokens, richer perspective |
| pick_primary | Speed over perfection | Faster, may miss nuances |

### 4. Observable AI Behavior

The Streamlit UI makes all routing decisions visible:

- Classification results (category, confidence, reasoning)
- OOD detection outcomes
- Ambiguity resolution strategy
- Expert routing decisions
- Complete JSON traces

This enables **AI UX observation**: How does the model behave in edge cases? How well-calibrated are confidence scores? When does it ask for clarification vs. make a decision?

## Test Scenarios

### Example Test Cases

See `examples/test_queries.json` for comprehensive test cases across:

- Clear pricing queries
- Clear UX queries
- Ambiguous queries
- OOD queries
- Edge cases

### Sabotage Scenarios

See `examples/sabotage_scenarios.json` for intentional edge cases:

- Ambiguity stress tests
- OOD detection challenges
- Boundary cases
- Confidence calibration tests
- Strategy comparisons
- Failure mode observation

## Testing

Run tests to verify behavior:

```bash
# Test classifier
pytest tests/test_classifier.py -v

# Test guardrails
pytest tests/test_guardrails.py -v

# All tests with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## Design Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Classifier Output | JSON-only structured responses | Parseable, transparent, no hallucinations |
| Expert Isolation | Separate class instances | Clear separation of concerns |
| Ambiguity Strategy | Configurable at runtime | Demonstrates different UX behaviors |
| OOD Detection | Pre-routing guardrail layer | Fail fast for inappropriate queries |
| UI Framework | Streamlit | Fast prototyping, built-in interactivity |
| Routing Logic | Direct implementation | Simpler than LangGraph, more transparent |

## Known Limitations

1. **No Task-Based Sub-Agents**: Originally planned to use Claude Code's Task system for expert isolation, but implemented as direct class instances for simplicity
2. **Simple Confidence Estimation**: Expert confidence scores use basic heuristics rather than calibrated probabilities
3. **No Memory/State**: Each query is independent, no conversation history
4. **Limited Domain Coverage**: Only two domains (pricing, UX)
5. **Keyword-Based Heuristics**: Pick primary strategy uses simple keyword matching

## Future Enhancements

- [ ] Add conversation history and context
- [ ] Implement proper confidence calibration
- [ ] Add more domain experts (Marketing, Engineering, etc.)
- [ ] Use embedding-based similarity for ambiguity detection
- [ ] Add response caching for common queries
- [ ] Implement feedback loop for improving routing
- [ ] Add A/B testing framework for comparing strategies

## Related Projects

This project draws patterns from:

- **ai-daily-assistant**: Multi-provider support, tool registry
- **product-market-fit**: Quality gates, iterative refinement
- **multi-agent-podcast-system**: Message protocol, orchestration

## License

MIT License - See LICENSE file for details

## Contributing

This is a learning project. Feel free to:

- Add new test scenarios
- Implement additional experts
- Experiment with routing strategies
- Improve UI/UX
- Add documentation

## Questions & Feedback

For questions or feedback about this learning project, please open an issue on GitHub.

---

**Key Takeaway**: This project demonstrates that effective AI routing requires multiple layers (classification, guardrails, ambiguity handling) and that making routing decisions transparent helps understand and improve AI behavior.

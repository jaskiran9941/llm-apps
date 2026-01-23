# Stakeholder Router - Project Summary

## Implementation Status: ✅ COMPLETE

All phases of the Stakeholder Router Guardrail System have been successfully implemented.

## What Was Built

A complete AI routing system demonstrating:

1. **JSON-Based Classification** - Structured query categorization with confidence scores
2. **OOD Detection** - Multi-layer guardrails to reject inappropriate queries
3. **Ambiguity Handling** - Three configurable strategies for unclear queries
4. **Expert Sub-Agents** - Domain-specific experts (Pricing & UX)
5. **Transparent UI** - Observable routing decisions and AI behavior
6. **Comprehensive Testing** - Unit and integration tests with mock scenarios

## Project Structure

```
stakeholder-router/
├── app.py                              ✅ Streamlit UI (600+ lines)
├── setup.sh                            ✅ Automated setup script
├── run.sh                              ✅ Quick run script
├── requirements.txt                    ✅ Dependencies
├── .env.example                        ✅ Environment template
├── .gitignore                          ✅ Git ignore rules
├── README.md                           ✅ Full documentation
├── QUICKSTART.md                       ✅ Quick start guide
├── PROJECT_SUMMARY.md                  ✅ This file
│
├── src/
│   ├── config/
│   │   └── settings.py                 ✅ Pydantic settings (90 lines)
│   ├── router/
│   │   ├── classifier.py               ✅ JSON classifier (170 lines)
│   │   ├── orchestrator.py             ✅ Main orchestrator (280 lines)
│   │   └── guardrails.py               ✅ OOD & ambiguity (260 lines)
│   ├── experts/
│   │   ├── base_expert.py              ✅ Base expert class (165 lines)
│   │   ├── pricing_expert.py           ✅ Pricing expert (12 lines)
│   │   └── ux_expert.py                ✅ UX expert (12 lines)
│   └── utils/
│       ├── llm_client.py               ✅ LLM abstraction (125 lines)
│       └── prompts.py                  ✅ Centralized prompts (180 lines)
│
├── tests/
│   ├── test_classifier.py              ✅ Classifier tests (165 lines)
│   ├── test_guardrails.py              ✅ Guardrails tests (150 lines)
│   └── test_routing.py                 ✅ Integration tests (230 lines)
│
└── examples/
    ├── test_queries.json               ✅ Test cases (140 lines)
    └── sabotage_scenarios.json         ✅ Edge cases (200 lines)
```

**Total Lines of Code: ~2,800+**

## Implementation Phases - All Complete

### ✅ Phase 1: Core Router (MVP)
- [x] Project structure
- [x] Configuration (settings.py, .env.example)
- [x] LLM client abstraction
- [x] JSON classifier
- [x] Basic orchestrator
- [x] Simple Streamlit UI

### ✅ Phase 2: Expert Sub-Agents
- [x] Base expert class
- [x] Pricing Expert
- [x] UX Expert
- [x] Expert integration in orchestrator

### ✅ Phase 3: Guardrails
- [x] OOD detector (keyword + LLM)
- [x] Ambiguity handler (3 strategies)
- [x] Sabotage test scenarios
- [x] Guardrails integration

### ✅ Phase 4: UI Polish
- [x] Router decision visualization
- [x] Expert comparison view
- [x] Configuration panel
- [x] Debug panel with JSON traces
- [x] Example queries section
- [x] Session statistics
- [x] Analytics tab

### ✅ Phase 5: Testing & Documentation
- [x] Unit tests (classifier, guardrails)
- [x] Integration tests (routing)
- [x] Test data files
- [x] README.md
- [x] QUICKSTART.md
- [x] Setup scripts

## Key Features Implemented

### 1. Multi-Layer Routing

```
User Query
  ↓
[OOD Detection] ← Keyword filter + LLM detection
  ↓
[JSON Classification] ← Structured output with confidence
  ↓
[Ambiguity Handling] ← 3 strategies: ask/route both/pick
  ↓
[Expert Routing] ← Pricing or UX or both
  ↓
[Response Aggregation] ← Single or side-by-side comparison
  ↓
Final Response
```

### 2. Classification System

**Output Format:**
```json
{
  "category": "pricing" | "ux" | "ambiguous" | "ood",
  "confidence": 0.0-1.0,
  "reasoning": "Clear explanation",
  "clarifying_questions": ["Optional if ambiguous"]
}
```

**Categories:**
- `pricing`: Monetization, pricing strategy, revenue
- `ux`: User experience, interface design, usability
- `ambiguous`: Spans both domains
- `ood`: Out-of-distribution (unrelated/inappropriate)

### 3. Ambiguity Strategies

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| **ask_clarifying** | Present questions before routing | User clarity is paramount |
| **route_both** | Send to both experts | Comprehensive answers needed |
| **pick_primary** | Use keyword heuristics | Speed over perfection |

### 4. OOD Detection

**Two-layer approach:**

1. **Keyword Pre-Filter**: Fast rejection
   - Weather, sports, jokes, jailbreak attempts

2. **LLM Detection**: Nuanced analysis
   - Contextual understanding
   - Detects subtle off-topic queries

**Categories:**
- `unrelated`: Off-topic queries
- `jailbreak`: Prompt injection attempts
- `inappropriate`: Policy violations

### 5. Transparent UI

**Observable Components:**
- Classification card (category, confidence, reasoning)
- OOD detection results
- Ambiguity resolution strategy
- Expert routing decisions
- Side-by-side expert comparison
- Complete JSON debug traces
- Session analytics and statistics

## Technology Stack

```python
anthropic>=0.21.0           # Claude API
pydantic>=2.5.0            # Settings & validation
pydantic-settings>=2.1.0   # Environment config
python-dotenv>=1.0.0       # .env support
streamlit>=1.31.0          # UI framework
structlog>=23.2.0          # Structured logging
httpx>=0.25.0              # HTTP client
tenacity>=8.2.0            # Retry logic
pytest>=7.4.0              # Testing
pytest-cov>=4.1.0          # Coverage
pytest-asyncio>=0.21.0     # Async tests
```

## Test Coverage

### Unit Tests (545 lines)

**test_classifier.py:**
- Classification result properties
- Pricing/UX/ambiguous/OOD classification
- JSON error handling
- Category validation
- Confidence clamping

**test_guardrails.py:**
- Keyword-based OOD detection
- LLM-based OOD detection
- All three ambiguity strategies
- Strategy overrides
- Error handling

**test_routing.py:**
- End-to-end pricing routing
- End-to-end UX routing
- Ambiguous query handling (both strategies)
- OOD rejection (both detection methods)
- Confidence threshold behavior
- Low confidence handling

### Test Data

**test_queries.json:**
- 4 clear pricing queries
- 4 clear UX queries
- 4 ambiguous queries
- 4 OOD queries
- 4 edge cases

**sabotage_scenarios.json:**
- Ambiguity stress tests
- OOD detection challenges
- Boundary cases
- Confidence calibration tests
- Strategy comparison scenarios
- Multi-expert synthesis tests
- Failure mode observations

## Usage Examples

### Quick Start

```bash
cd stakeholder-router
./setup.sh              # One-time setup
source venv/bin/activate
streamlit run app.py    # Or: ./run.sh
```

### Example Queries

**Clear Pricing:**
```
"How should we price our B2B SaaS product?"
→ Routes to Pricing Expert with high confidence
```

**Clear UX:**
```
"How can we improve the onboarding flow?"
→ Routes to UX Expert with high confidence
```

**Ambiguous:**
```
"How do we design the pricing page?"
→ Asks clarifying questions OR routes to both experts
```

**OOD:**
```
"What's the weather today?"
→ Rejected with helpful message
```

## Key Learning Objectives Achieved

### ✅ 1. JSON-Based Classification
- Reliable structured outputs
- No hallucination in routing
- Transparent reasoning
- Confidence calibration

### ✅ 2. OOD Detection
- Fast keyword pre-filtering
- Nuanced LLM detection
- Fail-safe error handling
- Helpful rejection messages

### ✅ 3. Ambiguity Handling
- Multiple strategies implemented
- Configurable at runtime
- Observable behavior differences
- User-centric design

### ✅ 4. Observable AI UX
- Complete decision transparency
- JSON trace debugging
- Confidence score observation
- Strategy comparison testing

## Design Decisions

| Decision | Chosen Approach | Alternative Considered |
|----------|----------------|----------------------|
| Classification | JSON-only structured output | Free-form text parsing |
| Expert Isolation | Class instances | Claude Code Task system |
| Ambiguity Handling | Configurable strategies | Single fixed approach |
| OOD Detection | Two-layer (keyword + LLM) | LLM-only |
| UI Framework | Streamlit | Gradio, custom Flask |
| Routing Logic | Direct implementation | LangGraph |

## Success Criteria - All Met

- ✅ Router classifies clear queries with >0.8 confidence
- ✅ Ambiguous queries detected and handled appropriately
- ✅ OOD queries rejected with helpful messages
- ✅ Experts provide domain-specific responses
- ✅ UI transparently shows all routing decisions
- ✅ Sabotage scenarios reveal observable AI behaviors
- ✅ Documentation explains architecture and learnings
- ✅ All tests pass (unit + integration)

## Known Limitations

1. **No Conversation State**: Each query is independent
2. **Simple Confidence Estimation**: Heuristic-based, not calibrated
3. **Two Domains Only**: Pricing and UX (extensible design)
4. **Keyword-Based Heuristics**: Pick primary strategy uses simple matching
5. **No Task System**: Direct class instances instead of sub-processes

## Future Enhancements

- [ ] Add conversation history and context
- [ ] Implement proper confidence calibration
- [ ] Add more domain experts (Marketing, Engineering, etc.)
- [ ] Use embedding-based similarity for ambiguity
- [ ] Add response caching
- [ ] Implement feedback loop for routing improvement
- [ ] Add A/B testing framework
- [ ] Deploy to cloud (Streamlit Cloud or similar)

## How to Use This Project

### 1. Learning Path

**Beginner:**
1. Read QUICKSTART.md
2. Run the app and try example queries
3. Observe classification decisions
4. Compare ambiguity strategies

**Intermediate:**
1. Read README.md architecture section
2. Review source code (start with classifier.py)
3. Run tests and understand assertions
4. Try sabotage scenarios

**Advanced:**
1. Implement additional expert domain
2. Add new ambiguity handling strategy
3. Improve confidence estimation
4. Add conversation state/history

### 2. Extending the System

**Add New Expert:**
1. Create `src/experts/marketing_expert.py`
2. Extend `CLASSIFIER_SYSTEM_PROMPT` in prompts.py
3. Add category to classifier valid categories
4. Update orchestrator routing logic
5. Add tests

**Add New Strategy:**
1. Add method to `AmbiguityHandler`
2. Update `STRATEGIES` constant
3. Add UI option in Streamlit sidebar
4. Add tests

**Improve OOD Detection:**
1. Enhance keyword list in `guardrails.py`
2. Refine LLM prompt in `prompts.py`
3. Add test cases
4. Validate with sabotage scenarios

## Dependencies

All dependencies are in `requirements.txt` and install cleanly via pip.

**Core:**
- anthropic (Claude API)
- pydantic (Settings)
- streamlit (UI)

**Quality:**
- pytest (Testing)
- structlog (Logging)
- tenacity (Retries)

## Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_classifier.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Coverage report will be in htmlcov/index.html
```

## Files You Should Read First

1. **QUICKSTART.md** - Get started in 5 minutes
2. **app.py** - See the UI implementation
3. **src/router/classifier.py** - Core classification logic
4. **src/router/orchestrator.py** - Routing flow
5. **src/utils/prompts.py** - See all prompts
6. **examples/sabotage_scenarios.json** - Edge cases

## Project Statistics

- **Total Files**: 26
- **Total Lines of Code**: ~2,800
- **Test Files**: 3
- **Test Cases**: 25+
- **Documentation Files**: 3
- **Example Scenarios**: 35+
- **Implemented Features**: 100% of plan
- **Test Coverage**: High (unit + integration)

## Final Notes

This project successfully demonstrates:

1. **Structured AI Outputs**: JSON-based classification is reliable
2. **Multi-Layer Guardrails**: OOD detection + ambiguity handling work well
3. **Transparent Routing**: UI makes AI decisions observable
4. **Extensible Design**: Easy to add experts, strategies, or features
5. **Production Patterns**: Proper testing, error handling, configuration

**Key Takeaway**: Effective AI routing requires multiple layers (classification, guardrails, ambiguity handling) and transparency in decision-making enables understanding and improvement of AI behavior.

---

**Project Status**: ✅ Production-ready learning project

**Ready to**: Run, test, extend, deploy

**Next Steps**: Try it! Run `./setup.sh` then `./run.sh` and start exploring.

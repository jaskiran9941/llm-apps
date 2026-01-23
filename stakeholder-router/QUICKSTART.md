# Stakeholder Router - Quick Start Guide

Get the Stakeholder Router running in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation Steps

### 1. Navigate to Project Directory

```bash
cd stakeholder-router
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

On macOS/Linux:
```bash
echo "ANTHROPIC_API_KEY=your_actual_api_key_here" > .env
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app should automatically open in your browser at `http://localhost:8501`

## First Steps in the UI

### 1. Verify Configuration

Check the sidebar - you should see:
- ✅ API Key Configured

If you see ❌ API Key Missing, double-check your `.env` file.

### 2. Try a Clear Pricing Query

In the chat input, try:
```
How should we price our B2B SaaS product?
```

**Expected Result:**
- Category: PRICING
- Confidence: >0.8
- Routes to Pricing Expert
- Receives pricing strategy advice

### 3. Try a Clear UX Query

Try:
```
How can we improve the onboarding flow?
```

**Expected Result:**
- Category: UX
- Confidence: >0.8
- Routes to UX Expert
- Receives UX design recommendations

### 4. Try an Ambiguous Query

Try:
```
How do we design the pricing page?
```

**Expected Result (with default "ask_clarifying" strategy):**
- Category: AMBIGUOUS
- Confidence: 0.5-0.7
- Presents clarifying questions:
  - "Are you asking about visual design and layout?"
  - "Or about pricing tier structure and display?"

### 5. Try an OOD Query

Try:
```
What's the weather today?
```

**Expected Result:**
- Detected as OOD (Out-of-Distribution)
- Rejected with helpful message
- Not routed to any expert

## Exploring Configurations

### Change Ambiguity Strategy

In the sidebar under "Configuration":

1. **Ask Clarifying** (default):
   - Presents questions before routing
   - More interactive UX

2. **Route Both**:
   - Sends query to both experts
   - Shows perspectives side-by-side
   - More comprehensive answers

3. **Pick Primary**:
   - Uses keyword analysis
   - Faster, single expert response

Try the same ambiguous query with different strategies to see the difference!

### Adjust Confidence Thresholds

Use the sliders in the sidebar:

- **High Confidence Threshold** (default 0.8): Above this → direct routing
- **Low Confidence Threshold** (default 0.5): Below this → treat as ambiguous

### Test Pre-Loaded Examples

In the sidebar under "Example Queries":

1. Select a category:
   - Clear Pricing Queries
   - Clear UX Queries
   - Ambiguous Queries
   - OOD Queries
   - Edge Cases

2. Pick an example from the dropdown

3. Click "Load Example"

4. The query will be automatically submitted

## Understanding the UI

### Classification Card

Shows the routing decision:
- 🔵 PRICING
- 🟢 UX
- 🟡 AMBIGUOUS
- 🔴 OOD

Plus:
- Confidence score
- Reasoning
- Clarifying questions (if any)

### Expert Responses

When routed to experts, you'll see:
- Expert name
- Confidence score
- Detailed response
- Sources mentioned (if any)

### Debug Panel

Click "Debug Info (JSON)" expander to see:
- Complete classification JSON
- Routing metadata
- Full response structure

### Analytics Tab

After processing several queries:
- View query history table
- See confidence distribution chart
- Track category breakdown

## Common Issues

### "API Key Missing" Error

**Solution:**
1. Check `.env` file exists in project root
2. Verify format: `ANTHROPIC_API_KEY=sk-ant-...`
3. No quotes needed around the key
4. Restart Streamlit if you just added it

### Import Errors

**Solution:**
```bash
# Make sure you're in the project directory
cd stakeholder-router

# Verify virtual environment is activated
which python  # Should show path to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Rate Limit Errors

**Solution:**
- The system uses retry logic automatically
- If you hit rate limits, wait a moment between queries
- Consider adding delays for batch testing

## Next Steps

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src
```

### Explore Sabotage Scenarios

Go to the "Test Scenarios" tab in the UI to see intentional edge cases designed to challenge the router.

### Read Full Documentation

Check out `README.md` for:
- Architecture details
- Design decisions
- Key learning objectives
- Future enhancements

## Quick Tips

1. **Start Simple**: Test clear queries first to verify setup
2. **Observe Confidence**: Notice how confidence scores relate to query clarity
3. **Try Edge Cases**: Test boundary queries to see routing behavior
4. **Compare Strategies**: Same query + different strategies = different UX
5. **Check Debug Info**: JSON traces show exactly what the classifier sees

## Example Query Sequence

Try this sequence to see the full system in action:

```
1. "How should we price our premium tier?"
   → Clear pricing (high confidence)

2. "What color should our signup button be?"
   → Clear UX (high confidence)

3. "How do we design the pricing page?"
   → Ambiguous (medium confidence)

4. "What's the capital of France?"
   → OOD (rejected)

5. "Should we show annual vs monthly pricing toggle?"
   → Ambiguous boundary case
```

## Support

For issues:
1. Check this Quick Start guide
2. Review README.md
3. Check test files for examples
4. Open an issue on GitHub

---

**You're ready to go!** Start with clear queries to verify setup, then explore edge cases and ambiguity handling strategies.

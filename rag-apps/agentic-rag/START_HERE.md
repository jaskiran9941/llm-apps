# 🚀 START HERE

## What You Just Got

A **truly agentic RAG system** that:
- 🧠 Makes autonomous decisions about retrieval
- ⚖️ Evaluates its own work
- 🔄 Adapts strategy when things don't work
- 📊 Shows you its complete reasoning process

Unlike the 4 GitHub repos we analyzed (which just had conditional logic), this actually implements autonomous agent behavior.

## 3-Minute Quick Start

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Add Your OpenAI Key
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key:
# OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run It
```bash
streamlit run app.py
```

That's it! The app will open in your browser.

## First Steps in the UI

1. **Click "Initialize Knowledge Base"** (sidebar)
   - This loads the sample document about agentic AI
   - You can add your own PDFs/text files to `documents/` folder

2. **Ask a question**:
   - Try: "What is an agentic AI system?" (tests local search)
   - Try: "What is quantum computing?" (tests web search)
   - Try: "What causes auroras?" (tests multi-step reasoning)

3. **View the reasoning**:
   - After each answer, click "View Agent's Reasoning Process"
   - Watch how the agent thinks, decides, evaluates, and adapts

## See the Difference

Want to understand what makes this "truly agentic"?

```bash
python demo_comparison.py
```

This shows side-by-side:
- Traditional RAG (simple pipeline)
- Conditional RAG (the "agentic" marketing version)
- Truly Agentic RAG (what we built)

## Test It

```bash
python test_agent.py
```

Runs automated tests showing the agent's decision-making process.

## Learn More

- **`QUICKSTART.md`** - Detailed setup guide
- **`COMPARISON.md`** - Why other "agentic" RAG isn't actually agentic
- **`ARCHITECTURE.md`** - How it works under the hood
- **`PROJECT_SUMMARY.md`** - Complete overview

## Key Concepts to Understand

### 1. ReAct Loop
```
Think → Act → Observe → Reflect → Decide
```

The agent repeatedly:
- **Thinks** about what it needs
- **Acts** by calling a tool
- **Observes** the results
- **Reflects** on quality
- **Decides** whether to continue

### 2. Self-Evaluation

After each retrieval, the agent scores its results:
- Score >= 7/10 → Good enough, generate answer
- Score < 7/10 → Try again with different approach

### 3. Dynamic Replanning

The agent doesn't follow a script. It decides:
- Which tool to use (local docs vs web)
- What query to use (can refine from original question)
- Whether to try again (based on self-evaluation)

## Customization

Edit `config.py`:

```python
MAX_ITERATIONS = 3        # How many times agent tries
EVALUATION_THRESHOLD = 7  # Quality bar (out of 10)
LLM_MODEL = "gpt-4o-mini" # Which model to use
```

## Add Your Own Documents

```bash
# Add PDFs, .txt, or .md files
cp your-document.pdf documents/

# Re-initialize in the UI
# Click "Initialize Knowledge Base" again
```

## Common Questions

**Q: Why is it slower than simple RAG?**
A: It makes multiple LLM calls (planning, evaluation, generation). Quality over speed.

**Q: Why does it cost more?**
A: ~$0.01 per query vs ~$0.003 for simple RAG. The 3-5x cost gets you much better answers.

**Q: When should I use this vs simple RAG?**
A: Use this when answer quality matters more than speed/cost. Great for research, complex queries, synthesis.

**Q: Can I add more tools?**
A: Yes! Edit `tools.py` and add new retrieval sources (SQL, APIs, etc.)

## What to Try

1. **Add your own documents**
   - Drop PDFs in `documents/` folder
   - Ask questions about them
   - Watch agent search locally first, then web if needed

2. **Adjust the threshold**
   - Lower `EVALUATION_THRESHOLD` in `config.py`
   - Agent will be pickier, try more iterations

3. **Add a new tool**
   - Edit `tools.py`
   - Add a new retriever (e.g., Wikipedia API, SQL database)
   - Agent will automatically consider it

4. **Compare different questions**
   - Simple questions: agent finds answer quickly
   - Complex questions: agent does multi-step research

## Troubleshooting

**Error: "OPENAI_API_KEY not found"**
```bash
# Make sure .env exists and has your key
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

**Error: "Vector database not initialized"**
- Click "Initialize Knowledge Base" in sidebar first

**Agent keeps searching but never satisfied**
- Lower `EVALUATION_THRESHOLD` in `config.py`
- Or add more relevant documents

**Want faster responses**
- Use `gpt-4o-mini` instead of `gpt-4` in `config.py`
- Reduce `MAX_ITERATIONS` to 2

## Next Steps

1. ✅ Run the app and try it out
2. ✅ Add your own documents
3. ✅ Watch the reasoning traces
4. ✅ Read `COMPARISON.md` to understand the difference
5. ✅ Experiment with different configurations
6. ✅ Build something awesome!

## Need Help?

- Check the documentation files
- Read the code (it's well-commented)
- Experiment with `config.py` settings

---

**Now go run it!** 🚀

```bash
streamlit run app.py
```

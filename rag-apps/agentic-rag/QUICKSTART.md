# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Set Up API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-...
```

## 3. Add Documents (Optional)

Add any PDFs, .txt, or .md files to the `documents/` folder:

```bash
# Example: download a sample PDF
curl -o documents/sample.pdf https://arxiv.org/pdf/2103.14030.pdf
```

Or skip this step to test web-only search.

## 4. Run the App

```bash
streamlit run app.py
```

## 5. Try It Out

1. Click "Initialize Knowledge Base" in the sidebar (if you added documents)
2. Ask a question like:
   - "What is quantum computing?" (web search)
   - "Explain the content in the uploaded documents" (local search)
   - "What are the latest AI developments?" (web search)

## Watch the Agent Think

After each answer, click "View Agent's Reasoning Process" to see:
- 💭 What the agent was thinking
- 🎯 Which tools it chose
- 👀 What it found
- 🤔 How it evaluated the results
- 🔄 Why it tried again (or stopped)

## Example Interaction

**You**: "What is quantum entanglement?"

**Agent's Internal Process**:
```
Iteration 1:
💭 THOUGHT: Need to find explanation of quantum entanglement
🎯 ACTION: search_local_docs("quantum entanglement")
👀 OBSERVATION: No relevant documents found
🤔 REFLECTION: Local docs don't have this. Score: 2/10
               Need to search the web instead.

Iteration 2:
💭 THOUGHT: Previous local search failed. Try web search.
🎯 ACTION: search_web("quantum entanglement explanation")
👀 OBSERVATION: Retrieved 5 web pages
🤔 REFLECTION: Found comprehensive Wikipedia and physics articles.
               Score: 9/10. Sufficient to answer!
```

**Agent's Answer**: "Quantum entanglement is a phenomenon where..."

## Configuration

Edit `config.py` to customize:
- `MAX_ITERATIONS = 3` - How many times agent will try
- `EVALUATION_THRESHOLD = 7` - Quality bar (out of 10)
- `LLM_MODEL` - Which model to use

## Tips

1. **For better local search**: Add more documents to `documents/`
2. **For faster responses**: Use `gpt-4o-mini` instead of `gpt-4`
3. **To see more reasoning**: Lower `EVALUATION_THRESHOLD` so agent tries more approaches
4. **To save API costs**: Reduce `MAX_ITERATIONS` to 2

## Troubleshooting

**"Vector database not initialized"**
- Click "Initialize Knowledge Base" button first

**"No documents found"**
- Add PDF/text files to `documents/` folder
- Or just use web search (agent will automatically fall back)

**API errors**
- Check your `.env` file has correct `OPENAI_API_KEY`
- Verify you have OpenAI credits

**Agent keeps searching**
- Lower `EVALUATION_THRESHOLD` in config.py
- Or increase `MAX_ITERATIONS` if questions are complex

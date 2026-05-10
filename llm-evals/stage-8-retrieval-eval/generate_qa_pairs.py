"""
generate_qa_pairs.py

Synthetically generates (query, gold_chunk_id) pairs for retrieval evaluation.

Pipeline per chunk (Ch7 §7.2):
  1. Extract a specific, verifiable fact from the chunk
  2. Write a discriminative question answerable only by that fact
  3. Generate a "hard" question with overlapping terminology across chunks
  4. Score realism of each question (1-5); keep only score >= 4
  5. Save all passing pairs to data/qa_pairs.json

Requires: OPENAI_API_KEY in stage-1-chatbot/.env
          litellm installed in stage-1-chatbot/.venv
"""

import json
import os
import sys
import time

# ---------------------------------------------------------------------------
# Environment setup — load .env from stage-1-chatbot
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, "..", "stage-1-chatbot", ".env")

# Add venv site-packages to path for imports
VENV_SITE = os.path.join(
    SCRIPT_DIR, "..", "stage-1-chatbot", ".venv", "lib"
)
for entry in os.scandir(VENV_SITE):
    sp = os.path.join(entry.path, "site-packages")
    if os.path.isdir(sp) and sp not in sys.path:
        sys.path.insert(0, sp)

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ENV_PATH)

import litellm  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODEL = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")
CHUNKS_PATH = os.path.join(SCRIPT_DIR, "data", "chunks.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "qa_pairs.json")

REALISM_THRESHOLD = 4      # Minimum realism score (out of 5) to keep a pair
QUESTIONS_PER_CHUNK = 2    # How many questions to attempt per chunk
REQUEST_DELAY_S = 0.5      # Delay between LLM calls to avoid rate limits


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def llm_call(prompt: str, temperature: float = 0.7) -> str:
    """Make a single LLM call and return the response text."""
    response = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()


def extract_fact(chunk: dict) -> str:
    """
    Step 1: Extract a specific, verifiable fact from a chunk.

    We want a concrete piece of information — a number, a rule, a requirement —
    not a general summary. Concrete facts make discriminative questions.
    """
    prompt = f"""You are helping build an evaluation dataset for an eBay Live customer support chatbot.

Here is a chunk from the eBay Live knowledge base, from the section "{chunk['section_name']}":

---
{chunk['raw_content']}
---

Extract ONE specific, verifiable fact from this chunk. The fact should be:
- Concrete: a number, a specific rule, a deadline, a requirement, or a named feature
- Not vague or general (e.g., not "eBay Live supports auctions" — that is too general)
- Something a user could specifically ask about

Respond with just the fact as a single sentence. Do not explain or prefix it."""

    return llm_call(prompt, temperature=0.3)


def generate_question(chunk: dict, fact: str, hard: bool = False) -> str:
    """
    Step 2: Write a discriminative question for the extracted fact.

    If hard=True, write a question with terminology that overlaps with other
    sections but can only be answered from this specific chunk.
    """
    if hard:
        style_instruction = """Write a question that:
1. Uses vocabulary or concepts that ALSO appear in other sections (e.g., mentions "sellers" when the fact is about buyers, or mentions "bidding" when the fact is about requirements)
2. Can ONLY be correctly answered using this specific fact
3. Would confuse a retriever that relies on simple keyword overlap
4. Sounds like a natural, realistic user question"""
    else:
        style_instruction = """Write a question that:
1. Can ONLY be answered using this exact fact
2. Does NOT copy words directly from the fact (paraphrase instead)
3. Sounds like something a real eBay Live user would ask in customer support
4. Does not mention the section name"""

    prompt = f"""You are building an evaluation dataset for an eBay Live customer support chatbot.

The knowledge base section is: "{chunk['section_name']}"

A specific fact from that section:
Fact: {fact}

{style_instruction}

Respond with just the question. Do not prefix it or explain it."""

    return llm_call(prompt, temperature=0.8)


def score_realism(question: str) -> int:
    """
    Step 3: Score a question's realism on a 1-5 scale.

    1 = Clearly machine-generated, no real user would ask this
    2 = Awkward phrasing, unlikely to appear in a real support queue
    3 = Plausible but stilted
    4 = Realistic, sounds like a real user
    5 = Highly realistic, could appear in a real support queue

    Keep questions with score >= REALISM_THRESHOLD.
    """
    prompt = f"""You are evaluating the realism of a customer support question for an eBay Live chatbot.

Score this question on a 1-5 scale:
1 = Clearly machine-generated or extractive (copies words from a policy document)
2 = Awkward phrasing, unlikely in a real support queue
3 = Plausible but stilted or overly formal
4 = Realistic, sounds like a real eBay Live user
5 = Highly realistic, could appear verbatim in a real support queue

Question: "{question}"

Respond with ONLY the number (1, 2, 3, 4, or 5). No explanation."""

    result = llm_call(prompt, temperature=0.0)
    # Parse just the digit
    for char in result:
        if char.isdigit():
            return int(char)
    return 3  # Default to middle if parsing fails


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------

def generate_pairs_for_chunk(chunk: dict) -> list[dict]:
    """
    Generate up to QUESTIONS_PER_CHUNK QA pairs for a single chunk.
    Returns a list of passing (score >= threshold) pairs.
    """
    pairs = []
    attempts = [
        {"hard": False, "label": "standard"},
        {"hard": True, "label": "hard"},
    ]

    for attempt in attempts[:QUESTIONS_PER_CHUNK]:
        try:
            # Step 1: Extract fact
            fact = extract_fact(chunk)
            time.sleep(REQUEST_DELAY_S)

            # Step 2: Generate question
            question = generate_question(chunk, fact, hard=attempt["hard"])
            time.sleep(REQUEST_DELAY_S)

            # Step 3: Score realism
            score = score_realism(question)
            time.sleep(REQUEST_DELAY_S)

            pair = {
                "question": question,
                "answer_chunk_id": chunk["id"],
                "answer_section": chunk["section_name"],
                "fact": fact,
                "realism_score": score,
                "question_type": attempt["label"],
                "passes_filter": score >= REALISM_THRESHOLD,
            }
            pairs.append(pair)

            status = "KEEP" if pair["passes_filter"] else "DROP"
            print(
                f"    [{status}] score={score}  [{attempt['label']}]  {question[:70]}..."
                if len(question) > 70
                else f"    [{status}] score={score}  [{attempt['label']}]  {question}"
            )

        except Exception as e:
            print(f"    [ERROR] {e}")
            continue

    return pairs


def main() -> None:
    # Load chunks
    chunks_path = os.path.normpath(CHUNKS_PATH)
    if not os.path.exists(chunks_path):
        print(
            f"ERROR: chunks.json not found at:\n  {chunks_path}\n"
            "Run chunk_knowledge_base.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print("=" * 65)
    print("Synthetic QA Pair Generation")
    print(f"Model:        {MODEL}")
    print(f"Chunks:       {len(chunks)}")
    print(f"Per chunk:    {QUESTIONS_PER_CHUNK} questions attempted")
    print(f"Keep filter:  realism score >= {REALISM_THRESHOLD}/5")
    print("=" * 65)
    print()

    all_pairs: list[dict] = []

    for i, chunk in enumerate(chunks):
        print(f"[{i+1}/{len(chunks)}]  {chunk['id']}  {chunk['section_name']}")
        pairs = generate_pairs_for_chunk(chunk)
        all_pairs.extend(pairs)
        print()

    # Summary
    passing = [p for p in all_pairs if p["passes_filter"]]
    dropped = [p for p in all_pairs if not p["passes_filter"]]

    print("=" * 65)
    print("Generation Summary")
    print("=" * 65)
    print(f"Total generated:  {len(all_pairs)}")
    print(f"Passing filter:   {len(passing)}")
    print(f"Dropped:          {len(dropped)}")
    print()

    # Save ALL pairs (including dropped) so you can inspect them
    output_path = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_pairs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_pairs)} pairs to:\n  {output_path}")
    print(f"({len(passing)} will be used in evaluation — passes_filter=true)")
    print()

    # Print a sample of passing questions
    if passing:
        print("Sample passing questions:")
        for pair in passing[:5]:
            print(f"  [{pair['answer_chunk_id']}] {pair['question']}")


if __name__ == "__main__":
    main()

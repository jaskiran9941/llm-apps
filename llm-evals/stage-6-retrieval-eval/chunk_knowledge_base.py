"""
chunk_knowledge_base.py

Reads the eBay Live system prompt and splits it into section-based chunks.
Each chunk corresponds to one ## header section in the markdown file.

We skip the role/rules sections at the end (Your Role, Rules) because those
describe the chatbot's behaviour, not facts a retriever should surface.

Output: data/chunks.json
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(
    SCRIPT_DIR,
    "..",
    "stage-1-chatbot",
    "backend",
    "system_prompt.md",
)
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "chunks.json")

# Sections to EXCLUDE — they describe chatbot behaviour, not KB facts
SKIP_SECTIONS = {"Your Role", "Rules"}


def load_system_prompt(path: str) -> str:
    """Read the raw system prompt markdown."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def parse_sections(text: str) -> list[dict]:
    """
    Split the document on ## headers.

    Returns a list of dicts:
        {
            "section_name": str,
            "content": str,          # full text including the header line
            "raw_content": str,      # text below the header (no header line)
        }
    """
    # Pattern: a line that starts with exactly ##  (not ### or deeper)
    header_pattern = re.compile(r"^## (.+)$", re.MULTILINE)

    # Find all header positions
    headers = list(header_pattern.finditer(text))

    if not headers:
        raise ValueError("No ## headers found in the system prompt.")

    sections = []
    for i, match in enumerate(headers):
        section_name = match.group(1).strip()
        start = match.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        full_content = text[start:end].strip()
        # Raw content is everything after the first newline (below the header)
        first_newline = full_content.find("\n")
        raw_content = full_content[first_newline:].strip() if first_newline != -1 else ""
        sections.append(
            {
                "section_name": section_name,
                "content": full_content,
                "raw_content": raw_content,
            }
        )
    return sections


def build_chunks(sections: list[dict]) -> list[dict]:
    """
    Convert parsed sections into chunk records, skipping role/rules sections.

    Chunk schema:
        {
            "id": "chunk_00",
            "section_name": str,
            "content": str,          # full text including ## header
            "raw_content": str,      # text below the header
            "word_count": int,
        }
    """
    chunks = []
    idx = 0
    for section in sections:
        if section["section_name"] in SKIP_SECTIONS:
            continue
        chunk_id = f"chunk_{idx:02d}"
        word_count = len(section["content"].split())
        chunks.append(
            {
                "id": chunk_id,
                "section_name": section["section_name"],
                "content": section["content"],
                "raw_content": section["raw_content"],
                "word_count": word_count,
            }
        )
        idx += 1
    return chunks


def print_summary(chunks: list[dict]) -> None:
    """Print a human-readable summary of the chunked KB."""
    word_counts = [c["word_count"] for c in chunks]
    avg_wc = sum(word_counts) / len(word_counts) if word_counts else 0

    print("=" * 60)
    print("Knowledge Base Chunking Summary")
    print("=" * 60)
    print(f"Total chunks:      {len(chunks)}")
    print(f"Total words:       {sum(word_counts)}")
    print(f"Average chunk size: {avg_wc:.0f} words")
    print(f"Min chunk size:    {min(word_counts)} words")
    print(f"Max chunk size:    {max(word_counts)} words")
    print()
    print(f"{'ID':<12} {'Words':>6}  Section")
    print("-" * 60)
    for chunk in chunks:
        print(f"  {chunk['id']:<10} {chunk['word_count']:>6}  {chunk['section_name']}")
    print("=" * 60)


def main() -> None:
    # Resolve and validate paths
    kb_path = os.path.normpath(KB_PATH)
    output_path = os.path.normpath(OUTPUT_PATH)

    if not os.path.exists(kb_path):
        print(f"ERROR: Knowledge base not found at:\n  {kb_path}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load, parse, and chunk
    text = load_system_prompt(kb_path)
    sections = parse_sections(text)
    chunks = build_chunks(sections)

    if not chunks:
        print("ERROR: No chunks were produced. Check SKIP_SECTIONS and the KB format.", file=sys.stderr)
        sys.exit(1)

    # Save
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(chunks)} chunks to:\n  {output_path}\n")
    print_summary(chunks)


if __name__ == "__main__":
    main()

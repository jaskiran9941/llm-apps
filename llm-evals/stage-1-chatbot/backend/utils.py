from __future__ import annotations

import os
from pathlib import Path
from typing import Final, List, Dict

import litellm
from dotenv import load_dotenv

load_dotenv()

_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"
SYSTEM_PROMPT: Final[str] = _PROMPT_PATH.read_text().strip()

MODEL_NAME: Final[str] = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")


def get_response(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if not messages or messages[0]["role"] != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    completion = litellm.completion(model=MODEL_NAME, messages=messages)
    reply = completion["choices"][0]["message"]["content"].strip()
    return messages + [{"role": "assistant", "content": reply}]

"""
eBay Live Agent Backend

Extends the Stage 1 single-turn chatbot with tool calling via a ReAct loop.

Architecture:
  User query
      → LLM decides: answer directly OR call a tool
      → If tool call: execute tool, feed result back to LLM
      → LLM generates final response

Every step is recorded in a structured trace with:
  - state name
  - inputs to that state
  - tool arguments (if a tool was called)
  - tool result (if a tool was called)
  - LLM output
  - success flag

Public API:
  get_agent_response(query: str) -> dict
      Returns {"response": str, "trace": dict}

The trace structure matches the format described in README.md §Part 5.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path setup: use the Stage 1 venv and .env
# ---------------------------------------------------------------------------
STAGE1_DIR = Path(__file__).parent.parent / "stage-1-chatbot"
ENV_PATH = STAGE1_DIR / ".env"

# Load .env from Stage 1
if ENV_PATH.exists():
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)

import litellm
from tools import TOOL_SCHEMAS, dispatch_tool

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_NAME: str = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")

# Maximum number of tool-call rounds before forcing a final response.
# Keeps the agent from looping indefinitely with high-agency prompting.
MAX_TOOL_ROUNDS: int = 3

SYSTEM_PROMPT = """You are a helpful customer support agent for eBay Live, eBay's interactive livestream shopping platform.

## What is eBay Live?
eBay Live is a livestream shopping experience where sellers host live video events and buyers can watch, interact, and purchase items in real time. It is currently in beta.

## Available Categories
- Collectibles: sports trading cards, collectible toys, comics, coins & bullion, CCG, sports memorabilia
- Luxury & Fashion: luxury watches, handbags, jewelry, apparel, sneakers, streetwear
- Toys

## Availability
Currently available in the US and Canada only.

## Your Agency Level
You are a MODERATE-LOW AGENCY agent. This means:
- If you can confidently identify the user's intent, call the appropriate tool immediately.
- If the intent is genuinely ambiguous, ask ONE clarifying question before proceeding.
- If the user's question is outside the scope of your tools, escalate to a human agent using escalate_to_human.
- Do NOT keep retrying multiple tools if the first attempt does not resolve the question — escalate instead.
- Answering directly from knowledge is acceptable for general questions clearly covered above.
  For account-specific or eligibility questions, always use the appropriate tool.

## Tools Available
- check_category_eligibility(category): Is this product category supported on eBay Live?
- check_seller_eligibility(seller_id): Does this seller account meet hosting requirements?
- get_bidding_rules(topic): What are the rules for this bidding topic? Topics: soft_close, bid_retraction, max_bidding, payment
- escalate_to_human(reason, urgency): Open a human support ticket for out-of-scope issues.

## Rules
- Only state facts explicitly supported by your knowledge base or tool results.
- Never invent policies, fees, or eligibility decisions not backed by a tool call.
- If a question is outside what you know or can tool-call, say so clearly.
- Keep responses concise and friendly.
"""

# ---------------------------------------------------------------------------
# State names used in traces
# ---------------------------------------------------------------------------
STATE_PARSE_INTENT = "ParseIntent"
STATE_SELECT_TOOL = "SelectTool"
STATE_CALL_TOOL = "CallTool"
STATE_INTERPRET_RESULT = "InterpretResult"
STATE_GENERATE_RESPONSE = "GenerateResponse"


# ---------------------------------------------------------------------------
# Trace helpers
# ---------------------------------------------------------------------------

def _make_step(state: str, success: bool, **kwargs: Any) -> dict:
    """Create a single trace step dict."""
    return {"state": state, "success": success, **kwargs}


def _find_first_failure(states: list[dict]) -> str | None:
    """Return the name of the first failed state, or None if all succeeded."""
    for step in states:
        if not step.get("success", True):
            return step["state"]
    return None


# ---------------------------------------------------------------------------
# Core ReAct loop
# ---------------------------------------------------------------------------

def get_agent_response(query: str) -> dict:
    """
    Run the eBay Live agent on a single user query.

    Returns:
        {
            "response": str,          # Final natural-language response to the user
            "trace": {
                "states": list[dict], # One dict per pipeline state
                "first_failure_state": str | None,
                "overall_success": bool,
                "tool_calls_made": int,
                "tools_used": list[str]
            }
        }
    """
    states: list[dict] = []
    tools_used: list[str] = []
    tool_calls_made: int = 0

    # ------------------------------------------------------------------
    # State: ParseIntent
    # The LLM reads the query. We log this as a named state even though
    # the LLM doesn't return a structured intent object — the first LLM
    # call implicitly performs intent parsing AND tool selection together.
    # We record it as two logical states for traceability.
    # ------------------------------------------------------------------
    parse_success = True
    parse_details: dict = {"input": query}

    # Minimal intent heuristics (used only for trace labelling, not routing)
    intent_hints: dict[str, str] = {}
    query_lower = query.lower()
    if any(w in query_lower for w in ("seller", "sell", "host", "go live", "stream", "eligib")):
        intent_hints["user_type"] = "seller"
    elif any(w in query_lower for w in ("buyer", "buy", "bid", "win", "purchase", "payment")):
        intent_hints["user_type"] = "buyer"
    else:
        intent_hints["user_type"] = "unknown"

    parse_details["intent_hints"] = intent_hints
    states.append(_make_step(STATE_PARSE_INTENT, parse_success, **parse_details))

    # ------------------------------------------------------------------
    # Build the message list for the first LLM call
    # ------------------------------------------------------------------
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    final_response: str = ""
    tool_round: int = 0

    while tool_round <= MAX_TOOL_ROUNDS:
        # ------------------------------------------------------------------
        # LLM call — either initial response or continuation after tool result
        # ------------------------------------------------------------------
        try:
            completion = litellm.completion(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
            )
        except Exception as exc:
            # LLM call itself failed — record failure in GenerateResponse state
            states.append(
                _make_step(
                    STATE_GENERATE_RESPONSE,
                    False,
                    error=str(exc),
                    response=None,
                )
            )
            first_failure = _find_first_failure(states)
            return {
                "response": f"Sorry, I encountered an error: {exc}",
                "trace": {
                    "states": states,
                    "first_failure_state": first_failure,
                    "overall_success": False,
                    "tool_calls_made": tool_calls_made,
                    "tools_used": tools_used,
                },
            }

        choice = completion["choices"][0]
        message = choice["message"]
        finish_reason = choice.get("finish_reason", "stop")

        # ------------------------------------------------------------------
        # Did the LLM decide to call a tool?
        # ------------------------------------------------------------------
        raw_tool_calls = getattr(message, "tool_calls", None) or []

        if raw_tool_calls and finish_reason == "tool_calls":
            # Process the first tool call (we handle one per round for clarity)
            tc = raw_tool_calls[0]
            tool_name: str = tc.function.name
            try:
                tool_args: dict = json.loads(tc.function.arguments)
            except (json.JSONDecodeError, AttributeError) as exc:
                tool_args = {}
                # Record SelectTool as succeeded (LLM chose correctly),
                # CallTool as failed (argument parse error)
                states.append(
                    _make_step(
                        STATE_SELECT_TOOL,
                        True,
                        tool_name=tool_name,
                        args={},
                    )
                )
                states.append(
                    _make_step(
                        STATE_CALL_TOOL,
                        False,
                        tool_name=tool_name,
                        error=f"Could not parse tool arguments: {exc}",
                        raw_arguments=getattr(tc.function, "arguments", ""),
                    )
                )
                # Force exit from loop
                break

            tool_calls_made += 1
            if tool_name not in tools_used:
                tools_used.append(tool_name)

            # ------------------------------------------------------------------
            # State: SelectTool
            # ------------------------------------------------------------------
            states.append(
                _make_step(
                    STATE_SELECT_TOOL,
                    True,
                    tool_name=tool_name,
                    args=tool_args,
                )
            )

            # ------------------------------------------------------------------
            # State: CallTool — actually execute the function
            # ------------------------------------------------------------------
            try:
                tool_result: dict = dispatch_tool(tool_name, tool_args)
                call_success = "error" not in tool_result
                states.append(
                    _make_step(
                        STATE_CALL_TOOL,
                        call_success,
                        tool_name=tool_name,
                        result=tool_result,
                    )
                )
            except Exception as exc:
                tool_result = {"error": str(exc), "tool": tool_name}
                states.append(
                    _make_step(
                        STATE_CALL_TOOL,
                        False,
                        tool_name=tool_name,
                        error=str(exc),
                        result=tool_result,
                    )
                )

            # ------------------------------------------------------------------
            # Feed the tool result back to the LLM
            # Append the assistant's tool-call message and the tool result message
            # ------------------------------------------------------------------
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tc.function.arguments,
                            },
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result),
                }
            )

            # ------------------------------------------------------------------
            # State: InterpretResult
            # We do not have a separate LLM call for this — it happens implicitly
            # in the next iteration. We record it as a successful state here
            # (the actual check happens in GenerateResponse consistency validation).
            # ------------------------------------------------------------------
            states.append(
                _make_step(
                    STATE_INTERPRET_RESULT,
                    True,
                    tool_name=tool_name,
                    result_keys=list(tool_result.keys()),
                )
            )

            tool_round += 1
            continue  # Go back to the top of the loop for the LLM's next turn

        else:
            # ------------------------------------------------------------------
            # LLM chose NOT to call a tool — this is the final response
            # ------------------------------------------------------------------
            content = getattr(message, "content", None) or ""
            final_response = content.strip()

            # ------------------------------------------------------------------
            # State: GenerateResponse
            # Basic consistency check: if a tool was called with a binary result
            # (eligible / supported), verify the response doesn't contradict it.
            # ------------------------------------------------------------------
            consistency_ok = True
            consistency_note = ""

            for step in states:
                if step["state"] == STATE_CALL_TOOL and step.get("success"):
                    result = step.get("result", {})
                    resp_lower = final_response.lower()

                    # Check seller eligibility consistency
                    if result.get("tool") == "check_seller_eligibility":
                        eligible = result.get("eligible")
                        if eligible is True and any(
                            phrase in resp_lower
                            for phrase in ("not eligible", "don't qualify", "do not qualify", "ineligible")
                        ):
                            consistency_ok = False
                            consistency_note = "Response says ineligible but tool returned eligible=True"
                        elif eligible is False and any(
                            phrase in resp_lower
                            for phrase in ("you qualify", "you are eligible", "you're eligible", "great news")
                        ):
                            consistency_ok = False
                            consistency_note = "Response says eligible but tool returned eligible=False"

                    # Check category eligibility consistency
                    elif result.get("tool") == "check_category_eligibility":
                        supported = result.get("supported")
                        if supported is True and any(
                            phrase in resp_lower
                            for phrase in ("not supported", "not available", "not allowed")
                        ):
                            consistency_ok = False
                            consistency_note = "Response says not supported but tool returned supported=True"
                        elif supported is False and any(
                            phrase in resp_lower
                            for phrase in ("is supported", "is available", "you can sell")
                        ):
                            consistency_ok = False
                            consistency_note = "Response says supported but tool returned supported=False"

            states.append(
                _make_step(
                    STATE_GENERATE_RESPONSE,
                    consistency_ok,
                    response=final_response,
                    consistency_note=consistency_note if not consistency_ok else "",
                )
            )
            break

    # ------------------------------------------------------------------
    # If we exited the loop without a final response (hit MAX_TOOL_ROUNDS),
    # make one last call without tools to force a text answer.
    # ------------------------------------------------------------------
    if not final_response:
        messages.append(
            {
                "role": "user",
                "content": (
                    "Please provide a final answer to the user's original question "
                    "based on everything we've discussed."
                ),
            }
        )
        try:
            completion = litellm.completion(model=MODEL_NAME, messages=messages)
            final_response = (
                completion["choices"][0]["message"]["content"] or ""
            ).strip()
        except Exception as exc:
            final_response = f"I encountered an error preparing my response: {exc}"

        states.append(
            _make_step(
                STATE_GENERATE_RESPONSE,
                True,
                response=final_response,
                note="Forced response after reaching max tool rounds",
            )
        )

    # ------------------------------------------------------------------
    # Build and return the final trace
    # ------------------------------------------------------------------
    first_failure = _find_first_failure(states)
    overall_success = first_failure is None

    return {
        "response": final_response,
        "trace": {
            "states": states,
            "first_failure_state": first_failure,
            "overall_success": overall_success,
            "tool_calls_made": tool_calls_made,
            "tools_used": tools_used,
        },
    }


# ---------------------------------------------------------------------------
# CLI: run a single query from the command line for quick testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "What is eBay Live?",
        "Is seller_123 eligible to host an eBay Live stream?",
        "Are luxury watches available on eBay Live?",
        "How does the soft close rule work?",
        "Can I cancel my bid after I've placed it?",
    ]

    query = sys.argv[1] if len(sys.argv) > 1 else test_queries[1]
    print(f"\nQuery: {query}\n{'─' * 60}")

    result = get_agent_response(query)

    print(f"Response:\n{result['response']}\n")
    print("Trace:")
    for step in result["trace"]["states"]:
        status = "OK" if step["success"] else "FAIL"
        print(f"  [{status}] {step['state']}", end="")
        if step["state"] == STATE_SELECT_TOOL:
            print(f" → {step.get('tool_name')}({step.get('args', {})})", end="")
        elif step["state"] == STATE_CALL_TOOL:
            r = step.get("result", {})
            print(f" → {step.get('tool_name')}: {list(r.keys())}", end="")
        elif step["state"] == STATE_GENERATE_RESPONSE:
            note = step.get("consistency_note", "")
            if note:
                print(f" [consistency issue: {note}]", end="")
        print()

    print(f"\nFirst failure state: {result['trace']['first_failure_state']}")
    print(f"Overall success: {result['trace']['overall_success']}")
    print(f"Tool calls made: {result['trace']['tool_calls_made']}")
    print(f"Tools used: {result['trace']['tools_used']}")

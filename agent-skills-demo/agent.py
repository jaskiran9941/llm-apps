"""
Agent Orchestrator — The loop that makes an LLM autonomous.

The agent decides WHICH skill to use, WHEN to call tools, and HOW to
combine results. This is the key difference from a skill (which is just
a single prompt → single response).

Agent = LLM + Tools + Loop + Skills
"""

import json

from skills import apply_skill, SKILLS
from tools import TOOL_SCHEMAS, execute_tool

AGENT_SYSTEM_PROMPT = """\
You are an intelligent assistant that selects the best skill and tools to answer the user's query.

## Available Skills
{skills_list}

## Instructions
1. Analyze the user's query to determine which skill fits best.
2. Use the `select_skill` tool to pick a skill and explain your reasoning.
3. If the query contains code, use `analyze_code` to extract and format it first.
4. If the query needs research context, use `search_web` to gather information.
5. After gathering context with tools, provide your final response using the selected skill's format.

Always use at least the `select_skill` tool so the user can see your reasoning.
Think step by step about which skill and tools are most appropriate.
"""


def _build_skills_list() -> str:
    """Format skill descriptions for the agent system prompt."""
    lines = []
    for key, skill in SKILLS.items():
        lines.append(f"- **{key}**: {skill['description']} (Format: {skill['output_format']})")
    return "\n".join(lines)


class SkillAgent:
    """
    An agent that orchestrates skills and tools via a reasoning loop.

    The loop:
    1. Send messages to LLM with available tools
    2. If LLM calls tools → execute them, append results, continue
    3. If LLM responds without tools → done
    """

    def __init__(self, client, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model
        self.max_iterations = 5

    def run(self, user_query: str, conversation_history: list[dict] = None) -> dict:
        """
        Run the agent loop on a user query.

        Returns:
            dict with:
                - final_response: str
                - reasoning_trace: list of step dicts
                - total_tokens: int
                - skills_used: list of skill names
        """
        # Build messages
        system_msg = AGENT_SYSTEM_PROMPT.format(skills_list=_build_skills_list())
        messages = [{"role": "system", "content": system_msg}]

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": user_query})

        # Tracking
        trace = []
        total_tokens = 0
        skills_used = []
        selected_skill_name = None

        for iteration in range(1, self.max_iterations + 1):
            step = {
                "iteration": iteration,
                "action": None,
                "tool_calls": [],
                "tokens": 0,
            }

            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
            )

            choice = response.choices[0]
            step["tokens"] = response.usage.total_tokens
            total_tokens += response.usage.total_tokens

            # Case 1: LLM wants to call tools
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                step["action"] = "tool_calls"
                messages.append(choice.message)

                for tool_call in choice.message.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    result = execute_tool(fn_name, fn_args)

                    # Track skill selection
                    if fn_name == "select_skill":
                        selected_skill_name = fn_args["skill_name"]
                        skills_used.append(selected_skill_name)

                    # Log to trace
                    step["tool_calls"].append({
                        "tool": fn_name,
                        "args": fn_args,
                        "result": result,
                    })

                    # Append tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    })

                trace.append(step)

                # If a skill was selected, apply it and inject the result
                if selected_skill_name and selected_skill_name not in [
                    s.get("applied_skill") for s in trace
                ]:
                    skill_result = apply_skill(
                        selected_skill_name, user_query, self.client, self.model
                    )
                    total_tokens += skill_result["tokens"]

                    # Inject skill output as context
                    messages.append({
                        "role": "user",
                        "content": (
                            f"The {selected_skill_name} skill produced this analysis. "
                            f"Use it to form your final response:\n\n"
                            f"{skill_result['response']}"
                        ),
                    })

                    trace.append({
                        "iteration": f"{iteration} (skill)",
                        "action": "apply_skill",
                        "applied_skill": selected_skill_name,
                        "tokens": skill_result["tokens"],
                        "tool_calls": [],
                    })

                continue

            # Case 2: LLM responds directly (no more tool calls)
            step["action"] = "final_response"
            final_text = choice.message.content or ""
            trace.append(step)
            break

        else:
            # Hit max iterations
            final_text = "I've reached my maximum reasoning steps. Here's what I have so far."

        return {
            "final_response": final_text,
            "reasoning_trace": trace,
            "total_tokens": total_tokens,
            "skills_used": skills_used,
        }

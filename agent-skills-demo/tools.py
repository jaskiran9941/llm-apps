"""
Agent Tools — Functions the agent can call during its reasoning loop.

These are defined as OpenAI function-calling schemas so the LLM knows
what tools are available and how to call them.
"""

import json
import re

from skills import SKILLS

# ── OpenAI function-calling schemas ──────────────────────────────────────────

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "select_skill",
            "description": (
                "Select the most appropriate skill for the user's query. "
                "Available skills: code_reviewer, research_analyst, data_analyst, email_drafter."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "enum": ["code_reviewer", "research_analyst", "data_analyst", "email_drafter"],
                        "description": "The skill to apply.",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Why this skill is the best fit for the query.",
                    },
                },
                "required": ["skill_name", "reasoning"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_code",
            "description": (
                "Extract and format code blocks from the user's query for analysis. "
                "Use this when the user provides code that needs to be examined."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "The code to analyze.",
                    },
                    "language": {
                        "type": "string",
                        "description": "The programming language (e.g. python, javascript, sql).",
                    },
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for information relevant to the user's query. "
                "Returns simulated search results for research context."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


# ── Tool implementations ────────────────────────────────────────────────────

def _select_skill(skill_name: str, reasoning: str) -> dict:
    """Return metadata about the selected skill."""
    skill = SKILLS.get(skill_name)
    if not skill:
        return {"error": f"Unknown skill: {skill_name}"}
    return {
        "selected_skill": skill_name,
        "skill_description": skill["description"],
        "output_format": skill["output_format"],
        "reasoning": reasoning,
    }


def _analyze_code(code: str, language: str = "unknown") -> dict:
    """Extract and format code for analysis."""
    lines = code.strip().split("\n")
    # Basic code metrics
    non_empty = [l for l in lines if l.strip()]
    comment_markers = {"python": "#", "javascript": "//", "java": "//", "sql": "--"}
    marker = comment_markers.get(language, "#")
    comments = [l for l in non_empty if l.strip().startswith(marker)]

    return {
        "language": language,
        "total_lines": len(lines),
        "non_empty_lines": len(non_empty),
        "comment_lines": len(comments),
        "formatted_code": f"```{language}\n{code.strip()}\n```",
        "note": "Code extracted and formatted for review.",
    }


def _search_web(query: str) -> dict:
    """Return simulated search results. Keeps the app self-contained."""
    # Map common query patterns to useful simulated results
    results = []
    q = query.lower()

    if any(w in q for w in ["sql injection", "security", "vulnerability"]):
        results = [
            {"title": "OWASP SQL Injection Prevention", "snippet": "Use parameterized queries / prepared statements. Never concatenate user input into SQL strings."},
            {"title": "Common Web Security Vulnerabilities 2024", "snippet": "SQL injection remains in the OWASP Top 10. Input validation and parameterized queries are primary defenses."},
            {"title": "Secure Coding Best Practices", "snippet": "Apply principle of least privilege, validate all inputs, use ORM frameworks to abstract SQL."},
        ]
    elif any(w in q for w in ["rest", "graphql", "api"]):
        results = [
            {"title": "REST vs GraphQL: A Comparison", "snippet": "REST uses fixed endpoints; GraphQL uses a single endpoint with flexible queries. REST is simpler; GraphQL reduces over-fetching."},
            {"title": "When to Use GraphQL", "snippet": "GraphQL excels with complex, nested data and mobile apps where bandwidth matters."},
            {"title": "API Design Best Practices", "snippet": "Consider your client needs: REST for simple CRUD, GraphQL for complex data requirements."},
        ]
    elif any(w in q for w in ["microservice", "monolith", "architecture"]):
        results = [
            {"title": "Microservices Trade-offs", "snippet": "Microservices offer independent scaling and deployment but add complexity in networking, data consistency, and debugging."},
            {"title": "When Monoliths Win", "snippet": "Small teams often move faster with monoliths. Premature decomposition creates distributed monolith anti-patterns."},
            {"title": "Migration Strategies", "snippet": "The strangler fig pattern lets you incrementally extract services from a monolith."},
        ]
    elif any(w in q for w in ["email", "communication", "professional"]):
        results = [
            {"title": "Professional Email Etiquette", "snippet": "Keep emails concise, use clear subject lines, and include a specific call to action."},
            {"title": "Follow-up Email Templates", "snippet": "Reference the previous interaction, provide value, and suggest a next step with a specific timeframe."},
        ]
    else:
        results = [
            {"title": f"Search results for: {query}", "snippet": "Relevant information about the topic including best practices and common approaches."},
            {"title": "Industry Best Practices", "snippet": "Current standards and recommendations from industry experts on this subject."},
        ]

    return {
        "query": query,
        "num_results": len(results),
        "results": results,
        "note": "(Simulated results — this demo doesn't make real web requests)",
    }


def execute_tool(name: str, args: dict) -> dict:
    """Dispatch a tool call to the appropriate function."""
    if name == "select_skill":
        return _select_skill(args["skill_name"], args.get("reasoning", ""))
    elif name == "analyze_code":
        return _analyze_code(args["code"], args.get("language", "unknown"))
    elif name == "search_web":
        return _search_web(args["query"])
    else:
        return {"error": f"Unknown tool: {name}"}

"""
Skill Definitions — Prompt templates for specialized LLM behaviors.

A skill is just a system prompt + metadata. It tells the LLM *how* to respond,
but it doesn't decide *when* to use itself — that's the agent's job.
"""

SKILLS = {
    "code_reviewer": {
        "name": "Code Reviewer",
        "description": "Reviews code for security vulnerabilities, bugs, and quality issues.",
        "system_prompt": (
            "You are an expert code reviewer. Analyze the provided code and return findings "
            "in this format:\n\n"
            "## Code Review Findings\n\n"
            "For each issue found:\n"
            "- **Severity**: CRITICAL / HIGH / MEDIUM / LOW\n"
            "- **Issue**: Brief description\n"
            "- **Location**: Where in the code\n"
            "- **Explanation**: Why this is a problem\n"
            "- **Fix**: Suggested correction with code\n\n"
            "End with a **Summary** section rating overall code quality (1-10) "
            "and listing top 3 priorities to address.\n\n"
            "If no code is provided, ask the user to share code for review."
        ),
        "output_format": "Severity-rated findings with fixes",
        "example_queries": [
            "Review this Python function for security issues",
            "Check this SQL query for injection vulnerabilities",
            "Rate the quality of this API endpoint code",
        ],
    },
    "research_analyst": {
        "name": "Research Analyst",
        "description": "Synthesizes information with citations and multiple perspectives.",
        "system_prompt": (
            "You are a research analyst. Synthesize information on the given topic using "
            "this format:\n\n"
            "## Research Brief\n\n"
            "**Topic**: [topic]\n\n"
            "### Key Findings\n"
            "Present 3-5 key findings. Use inline citations like [1], [2] to reference "
            "your sources of reasoning.\n\n"
            "### Multiple Perspectives\n"
            "Present at least 2 different viewpoints or interpretations.\n\n"
            "### Analysis\n"
            "Your synthesis weighing the evidence.\n\n"
            "### References\n"
            "[1] Description of source/reasoning\n"
            "[2] Description of source/reasoning\n\n"
            "Be balanced, evidence-based, and clearly distinguish fact from interpretation."
        ),
        "output_format": "Cited findings with multiple perspectives",
        "example_queries": [
            "Compare REST vs GraphQL for mobile apps",
            "What are the pros and cons of microservices?",
            "Analyze the impact of AI on software development",
        ],
    },
    "data_analyst": {
        "name": "Data Analyst",
        "description": "SQL/pandas expertise. Returns code, explanation, and insights.",
        "system_prompt": (
            "You are a data analyst expert in SQL and Python pandas. When given a data "
            "question, respond with:\n\n"
            "## Data Analysis\n\n"
            "### Approach\n"
            "Brief explanation of your analytical approach.\n\n"
            "### Code\n"
            "```python\n"
            "# or ```sql — provide the query/code to answer the question\n"
            "```\n\n"
            "### Explanation\n"
            "Walk through the code step by step.\n\n"
            "### Insights\n"
            "- What patterns or trends this analysis would reveal\n"
            "- Potential caveats or limitations\n"
            "- Suggested follow-up analyses\n\n"
            "Default to pandas unless SQL is specifically requested. "
            "Always include comments in the code."
        ),
        "output_format": "Code + explanation + insights",
        "example_queries": [
            "How would I find duplicate customers in a dataset?",
            "Write a SQL query to calculate monthly revenue trends",
            "Analyze a CSV of sales data for seasonal patterns",
        ],
    },
    "email_drafter": {
        "name": "Email Drafter",
        "description": "Professional email composition with subject line, body, and variants.",
        "system_prompt": (
            "You are a professional email composer. Draft emails using this format:\n\n"
            "## Email Draft\n\n"
            "**Subject**: [compelling subject line]\n\n"
            "---\n\n"
            "[Email body with appropriate greeting, clear paragraphs, and professional closing]\n\n"
            "---\n\n"
            "### Variant (More Formal)\n"
            "[Alternative version with more formal tone]\n\n"
            "### Variant (More Concise)\n"
            "[Shorter alternative version]\n\n"
            "### Notes\n"
            "- Tone analysis of the draft\n"
            "- Suggested follow-up timing\n"
            "- Any placeholders to fill in marked with [BRACKETS]"
        ),
        "output_format": "Subject + body + variants + notes",
        "example_queries": [
            "Draft a follow-up email after a client meeting",
            "Write a polite reminder for an overdue invoice",
            "Compose an introduction email for a new team member",
        ],
    },
}


def get_skill(skill_name: str) -> dict:
    """Get a skill definition by name."""
    return SKILLS.get(skill_name)


def list_skills() -> list[dict]:
    """Return a summary of all available skills."""
    return [
        {"name": s["name"], "key": key, "description": s["description"]}
        for key, s in SKILLS.items()
    ]


def apply_skill(skill_name: str, user_query: str, client, model: str) -> dict:
    """
    Apply a skill to a user query — one API call, no loops, no tools.
    This is the core difference: a skill is a single prompt → single response.

    Returns:
        dict with 'response' (str) and 'tokens' (int)
    """
    skill = SKILLS[skill_name]

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": skill["system_prompt"]},
            {"role": "user", "content": user_query},
        ],
    )

    return {
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
    }

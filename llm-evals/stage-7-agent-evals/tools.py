"""
eBay Live Agent Tools

Mock implementations simulating real eBay Live backend calls.
Each tool returns structured data matching what a real API would return.
In production these would call actual eBay APIs.

Four tools are available to the agent:
  - check_category_eligibility(category)   — is this category supported on eBay Live?
  - check_seller_eligibility(seller_id)    — does this seller meet hosting requirements?
  - get_bidding_rules(topic)               — what are the rules for this bidding topic?
  - escalate_to_human(reason, urgency)     — open a human-agent support ticket

Each function returns a dict that always includes a "tool" key so the LLM
(and trace logger) can identify which tool produced the result.
"""

from __future__ import annotations

SUPPORTED_CATEGORIES: dict[str, list[str]] = {
    "collectibles": [
        "sports trading cards",
        "collectible toys",
        "comics",
        "coins & bullion",
        "CCG",
        "sports memorabilia",
    ],
    "luxury_fashion": [
        "luxury watches",
        "handbags",
        "jewelry",
        "apparel",
        "sneakers",
        "streetwear",
    ],
    "toys": ["toys"],
}

SELLER_DATABASE: dict[str, dict] = {
    "seller_123": {
        "account_standing": "good",
        "transaction_count": 450,
        "categories": ["collectibles"],
        "has_prior_livestream": True,
    },
    "seller_456": {
        "account_standing": "good",
        "transaction_count": 12,
        "categories": ["luxury_fashion"],
        "has_prior_livestream": False,
    },
    "seller_789": {
        "account_standing": "restricted",
        "transaction_count": 200,
        "categories": ["collectibles"],
        "has_prior_livestream": False,
    },
    "new_seller": {
        "account_standing": "good",
        "transaction_count": 3,
        "categories": [],
        "has_prior_livestream": False,
    },
}


# ---------------------------------------------------------------------------
# Tool 1: Category eligibility
# ---------------------------------------------------------------------------

def check_category_eligibility(category: str) -> dict:
    """
    Check if a product category is supported on eBay Live.

    Args:
        category: The product category name to look up.

    Returns:
        {
            supported: bool,
            category_group: str | None,
            subcategories: list[str],
            tool: "check_category_eligibility"
        }

    Failure modes to watch for:
    - LLM passes brand name ("Rolex") instead of category ("luxury watches")
    - LLM passes overly broad term ("fashion") that doesn't match any group or subcategory
    - LLM passes misspelled or abbreviated category ("LW" for "luxury watches")
    """
    category_lower = category.lower().strip()

    # Exact match against group names and subcategory names
    for group, subcats in SUPPORTED_CATEGORIES.items():
        group_alias = group.replace("_", " ")
        all_names = [group_alias] + [s.lower() for s in subcats]
        if category_lower in all_names:
            return {
                "supported": True,
                "category_group": group,
                "subcategories": subcats,
                "tool": "check_category_eligibility",
            }

    # Fuzzy / substring match (handles "sports cards" matching "sports trading cards")
    for group, subcats in SUPPORTED_CATEGORIES.items():
        for subcat in subcats:
            if category_lower in subcat.lower() or subcat.lower() in category_lower:
                return {
                    "supported": True,
                    "category_group": group,
                    "subcategories": subcats,
                    "tool": "check_category_eligibility",
                }

    return {
        "supported": False,
        "category_group": None,
        "subcategories": [],
        "message": f"Category '{category}' is not currently supported on eBay Live.",
        "tool": "check_category_eligibility",
    }


# ---------------------------------------------------------------------------
# Tool 2: Seller eligibility
# ---------------------------------------------------------------------------

def check_seller_eligibility(seller_id: str) -> dict:
    """
    Check if a seller account is eligible to host eBay Live streams.

    Args:
        seller_id: The seller's eBay account ID.

    Returns:
        {
            eligible: bool,
            seller_id: str,
            requirements_met: dict,
            failed_requirements: list[str],
            recommendation: str,
            tool: "check_seller_eligibility"
        }

    Requirements checked:
    - account_in_good_standing: account_standing == "good"
    - sufficient_transaction_history: transaction_count >= 50
    - has_eligible_category: seller is enrolled in at least one supported category
    - prior_livestream_experience: seller has hosted a stream before

    Important: "Seller not found" is NOT the same as "Seller is ineligible".
    A missing seller_id means we cannot evaluate eligibility, not that they
    are definitively ineligible.
    """
    seller_id_clean = seller_id.strip()

    if seller_id_clean not in SELLER_DATABASE:
        return {
            "eligible": False,
            "seller_id": seller_id_clean,
            "reasons": ["Seller not found in system"],
            "requirements_met": {},
            "failed_requirements": ["seller_found"],
            "recommendation": (
                "We could not find this seller ID. Please verify the account ID "
                "and try again, or contact eBay support."
            ),
            "tool": "check_seller_eligibility",
        }

    seller = SELLER_DATABASE[seller_id_clean]

    requirements = {
        "account_in_good_standing": seller["account_standing"] == "good",
        "sufficient_transaction_history": seller["transaction_count"] >= 50,
        "has_eligible_category": len(seller["categories"]) > 0,
        "prior_livestream_experience": seller["has_prior_livestream"],
    }

    failed = [k for k, v in requirements.items() if not v]
    eligible = len(failed) == 0

    return {
        "eligible": eligible,
        "seller_id": seller_id_clean,
        "requirements_met": requirements,
        "failed_requirements": failed,
        "recommendation": (
            "You qualify to apply for eBay Live."
            if eligible
            else "Fill out the eBay Live Seller Interest Form to express interest. "
            "You do not yet meet all requirements to be approved immediately."
        ),
        "tool": "check_seller_eligibility",
    }


# ---------------------------------------------------------------------------
# Tool 3: Bidding rules
# ---------------------------------------------------------------------------

def get_bidding_rules(topic: str) -> dict:
    """
    Get specific bidding rules for a given topic.

    Args:
        topic: The bidding rule topic. Valid values:
               "soft_close", "bid_retraction", "max_bidding", "payment"

    Returns:
        {
            rules: list[str],
            relevant_to: str,
            tool: "get_bidding_rules"
        }

    Failure modes to watch for:
    - LLM passes a topic with no matching rules — tool returns empty rules list
    - LLM calls this tool for eligibility questions (wrong tool for that intent)
    - LLM ignores the returned rules and answers from static knowledge instead
    """
    rules_db: dict[str, dict] = {
        "soft_close": {
            "rules": [
                "If a bid is placed in the last 5 seconds, the auction extends by 5 more seconds.",
                "This prevents last-second sniping and gives all bidders a fair chance.",
                "The extension can repeat indefinitely as long as bids keep arriving in the final 5 seconds.",
            ],
            "relevant_to": "auction timing and anti-sniping",
        },
        "bid_retraction": {
            "rules": [
                "All bids are final and cannot be retracted.",
                "Cancellations for buyer's remorse are not allowed.",
                "Once you click Bid, you are committed to purchasing at that price if you win.",
            ],
            "relevant_to": "bid cancellation and finality",
        },
        "max_bidding": {
            "rules": [
                "Select 'Max bid' and enter the highest amount you are willing to pay.",
                "eBay bids incrementally on your behalf up to your maximum.",
                "You will receive an on-screen alert if another bidder exceeds your maximum.",
                "Your maximum bid amount is not visible to other bidders.",
            ],
            "relevant_to": "automatic proxy bidding",
        },
        "payment": {
            "rules": [
                "The winning bidder is automatically charged after the auction closes.",
                "Buyers have 4 days to complete payment.",
                "An in-app notification and eBay inbox message are sent when you win.",
                "Second Chance Offers are available if the original winner does not pay.",
            ],
            "relevant_to": "post-auction payment and fulfillment",
        },
    }

    topic_lower = topic.lower().strip()

    # Exact key match
    if topic_lower in rules_db:
        return {**rules_db[topic_lower], "tool": "get_bidding_rules"}

    # Keyword match (handles "soft close" matching "soft_close", etc.)
    for key, data in rules_db.items():
        key_words = key.replace("_", " ")
        if key_words in topic_lower or topic_lower in key_words:
            return {**data, "tool": "get_bidding_rules"}

    # No match
    return {
        "rules": [],
        "relevant_to": "unknown",
        "message": (
            f"No specific bidding rules found for topic '{topic}'. "
            "Valid topics are: soft_close, bid_retraction, max_bidding, payment."
        ),
        "tool": "get_bidding_rules",
    }


# ---------------------------------------------------------------------------
# Tool 4: Escalate to human
# ---------------------------------------------------------------------------

def escalate_to_human(reason: str, urgency: str = "normal") -> dict:
    """
    Escalate the conversation to a human support agent.

    Use this tool when:
    - The user's question cannot be answered by the other tools
    - The user has an account-specific issue requiring eBay access
    - The user expresses frustration or urgency
    - The agent has tried available tools and still cannot resolve the issue

    Args:
        reason: A brief description of why escalation is needed.
        urgency: "normal" (2-4 hour response) or "urgent" (< 30 minute response).

    Returns:
        {
            ticket_id: str,
            estimated_wait: str,
            message: str,
            reason: str,
            tool: "escalate_to_human"
        }
    """
    import random

    valid_urgencies = {"normal", "urgent"}
    if urgency not in valid_urgencies:
        urgency = "normal"

    ticket_id = f"LIVE-{random.randint(10000, 99999)}"
    estimated_wait = "2-4 hours" if urgency == "normal" else "< 30 minutes"

    return {
        "ticket_id": ticket_id,
        "estimated_wait": estimated_wait,
        "message": (
            f"A human eBay Live support agent will follow up with you. "
            f"Your ticket ID is {ticket_id}. Estimated response time: {estimated_wait}."
        ),
        "reason": reason,
        "urgency": urgency,
        "tool": "escalate_to_human",
    }


# ---------------------------------------------------------------------------
# Tool dispatch: call a tool by name with a dict of arguments
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS: dict[str, callable] = {
    "check_category_eligibility": check_category_eligibility,
    "check_seller_eligibility": check_seller_eligibility,
    "get_bidding_rules": get_bidding_rules,
    "escalate_to_human": escalate_to_human,
}


def dispatch_tool(tool_name: str, tool_args: dict) -> dict:
    """
    Call a tool by name with a dict of keyword arguments.

    Returns the tool result dict, or an error dict if the tool name is unknown.
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {
            "error": f"Unknown tool: '{tool_name}'",
            "available_tools": list(TOOL_FUNCTIONS.keys()),
            "tool": tool_name,
        }
    return TOOL_FUNCTIONS[tool_name](**tool_args)


# ---------------------------------------------------------------------------
# LiteLLM tool schemas (passed as `tools=` parameter)
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "check_category_eligibility",
            "description": (
                "Check whether a specific product category is supported on eBay Live. "
                "Use this when a buyer or seller asks whether their type of item can be sold "
                "or purchased during a livestream. For example: 'Can I sell sports cards on eBay Live?' "
                "or 'Are luxury watches available on eBay Live?'. "
                "Do NOT use this to check whether a specific seller account is eligible — "
                "use check_seller_eligibility for that."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": (
                            "The product category to check. Use the category name, not a brand name. "
                            "Examples: 'sports trading cards', 'luxury watches', 'sneakers', 'comics'. "
                            "Do not pass brand names like 'Rolex' or 'Nike' — pass the category instead."
                        ),
                    }
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_seller_eligibility",
            "description": (
                "Check whether a specific seller account is eligible to host eBay Live streams. "
                "Use this when a seller asks if they qualify, asks about requirements, or wants "
                "to know what is preventing them from getting approved. "
                "Requirements checked: account standing, transaction history (minimum 50 transactions), "
                "enrollment in an eligible category, and prior livestreaming experience. "
                "Note: 'Seller not found' means the ID could not be verified — it does NOT mean "
                "the seller is definitively ineligible."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "seller_id": {
                        "type": "string",
                        "description": (
                            "The seller's eBay account ID. Extract only the ID itself, "
                            "not surrounding words. For example, if the user says "
                            "'check account seller_123', pass 'seller_123', not 'account seller_123'."
                        ),
                    }
                },
                "required": ["seller_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bidding_rules",
            "description": (
                "Get specific bidding rules for a given auction topic. "
                "Use this when a user asks about a specific bidding mechanic: "
                "the soft close rule, bid retraction, max bidding / proxy bidding, or payment timing. "
                "Do NOT use this to check seller or category eligibility."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "The bidding topic to look up. Valid values are: "
                            "'soft_close' (last-second extension rule), "
                            "'bid_retraction' (can you cancel a bid), "
                            "'max_bidding' (proxy / automatic bidding), "
                            "'payment' (post-auction payment rules). "
                            "Use the closest matching value from this list."
                        ),
                    }
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": (
                "Escalate the conversation to a human eBay Live support agent. "
                "Use this when: the user's question cannot be answered by the available tools, "
                "the user needs account-specific help that requires eBay system access, "
                "the user is frustrated or the issue is urgent, or after attempting available "
                "tools the question still cannot be resolved. "
                "This is appropriate for questions outside eBay Live scope (e.g. general eBay disputes, "
                "billing issues, account suspensions)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Brief explanation of why escalation is needed.",
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["normal", "urgent"],
                        "description": (
                            "'normal' for standard 2-4 hour response time. "
                            "'urgent' for issues requiring < 30 minute response "
                            "(e.g. active stream problems, payment failures)."
                        ),
                    },
                },
                "required": ["reason"],
            },
        },
    },
]

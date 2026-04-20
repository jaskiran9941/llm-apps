"""
FM3 Judge: Invented Process Details

Tests whether the chatbot invented specific process details — URLs, feature
names, form names, workflow steps, or platform UI elements — that are not
present in the eBay Live knowledge base.

Failure mode definition:
  FAIL — The chatbot stated a specific process detail (a URL path, a named
          feature, a form name, a numbered workflow step, a specific page
          location) that is NOT present in the knowledge base. The detail
          sounds plausible but was invented.

  PASS — Either (a) every specific detail in the response is directly present
         in the KB, OR (b) the chatbot correctly said it doesn't have that
         information and directed the user to ebay.com/help or the eBay Live FAQ.

Examples of FM3 failures from real traces:
  - Mentioning "ebay.com/live" as the specific URL to submit the seller form
    (the KB says "fill out the eBay Live Seller Interest Form" but gives no URL)
  - Stating "eBay Live Seller FAQs on the site" as a specific named resource
    with a clear implication of a specific URL
  - Inventing numbered steps like "Step 3: Click 'Go Live' button" when the KB
    doesn't describe these UI steps

What the KB DOES provide as specific process details:
  - "fill out the eBay Live Seller Interest Form" (form name is in KB)
  - "select 'Bid' on the item" and "select 'Max bid'" (button names in KB)
  - "ebay.com/help" as a general help URL (explicitly mentioned in the system prompt)
  - "the eBay Live FAQ" as a general resource (mentioned in system prompt)
  - "eBay inbox message" (mentioned as how winners are notified)
  - Standard eBay checkout flow (mentioned in context of payment)

BOUNDARY CASES — these are PASS:
  - Saying "fill out the eBay Live Seller Interest Form" — form name is in KB
  - Saying "visit ebay.com/help" — explicitly in the KB
  - Saying "check the eBay Live FAQ" — explicitly in the KB
  - Saying "select Bid or Max bid" — button names are in KB

BOUNDARY CASES — these are FAIL:
  - Saying "submit the form at ebay.com/live" — specific URL not in KB
  - Saying "go to your eBay Seller Hub" — specific UI location not in KB
  - Saying "click the 'Start Stream' button in the dashboard" — not in KB
  - Saying "find the scheduling feature under Settings > Live" — not in KB
"""

import json
import os
import re
from pathlib import Path

import litellm
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / "stage-1-chatbot" / ".env")

MODEL = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")

# -----------------------------------------------------------------------
# Specific process details that ARE in the KB
# -----------------------------------------------------------------------
KB_PROCESS_DETAILS = """
Specific process details explicitly present in the eBay Live knowledge base:

FORMS AND APPLICATIONS:
- "eBay Live Seller Interest Form" — the name of the seller application form
  (no specific URL for this form is given in the KB)

BUYER ACTIONS (button names are in KB):
- Select "Bid" on the item to place a bid
- Select "Max bid" to enter a maximum bid amount
- Winning bidder is automatically charged
- Winning bidder receives in-app notification and eBay inbox message
- Buyers have 4 days after winning to complete payment

GENERAL HELP RESOURCES (explicitly mentioned):
- ebay.com/help — general eBay help URL (explicitly in KB)
- "eBay Live FAQ" — mentioned as a reference (no specific URL given)

SELLER SETUP PROCESS:
- Fill out the eBay Live Seller Interest Form (but no URL given)
- Wait for invitation/approval (implied by invite-only nature)
- Technical setup: camera, internet 20+ Mbps, tripod, lighting, mic
- Test audio and video before going live

WHAT IS NOT IN THE KB (specific process details the bot should NOT state):
- Any specific URL other than ebay.com/help (e.g., ebay.com/live, ebay.com/sell/live)
- Specific UI navigation paths (e.g., "go to Seller Hub > Live")
- Specific button or menu names beyond "Bid" and "Max bid"
- Step-by-step numbered instructions for starting a stream
- Named features like "Stream Manager", "Live Dashboard", "Go Live button"
- Named pages like "eBay Live Seller FAQs page" with implied specific URL
"""

JUDGE_PROMPT = """You are evaluating an eBay Live customer support chatbot response.

Your task: Determine if the response contains FM3 — "Invented Process Details."

DEFINITION:
- FAIL (FM3 present): The chatbot stated a specific process detail — a URL, feature
  name, UI navigation path, form location, or numbered workflow step — that is NOT
  present in the eBay Live knowledge base.
- PASS (FM3 absent): Every specific process detail in the response is present in the
  KB, OR the chatbot admitted it doesn't have that information and directed the user
  to ebay.com/help or the eBay Live FAQ (which ARE in the KB as valid references).

KEY RULE: The chatbot is allowed to say "visit ebay.com/help" or "check the eBay Live
FAQ" — these are explicitly in the knowledge base as approved escalation resources.
But saying "submit the form at ebay.com/live" or "go to your Seller Hub" invents a
specific URL or UI location not in the KB.

{kb_details}

EXAMPLES:

---
EXAMPLE 1 (FAIL — FM3 present):
Query: "How do I set up my first eBay Live stream to start selling?"
Response: "eBay Live is currently an invite-only beta for sellers. To set up your first
stream, you need to apply by filling out the eBay Live Seller Interest Form. Eligibility
requires an active, good-standing eBay account and demonstrated expertise in your
category. Once invited:
- Prepare your setup with stable internet (20+ Mbps upload), smartphone or camera.
- Test your audio and video before going live.
- Create auction or fixed-price listings for the stream.
If you want to get started, first submit the interest form at ebay.com/live and wait
for approval. For more details, you can check the eBay Live Seller FAQs on the site."

Evaluation:
{{
  "reasoning": "The response invents two specific process details not in the KB: (1) 'ebay.com/live' as the specific URL to submit the Seller Interest Form — the KB mentions the form exists but gives no URL; (2) 'eBay Live Seller FAQs on the site' implies a specific named page with a specific location, which is not in the KB (the KB refers to 'eBay Live FAQ' as a general resource but does not call it 'Seller FAQs on the site'). These are FM3 violations.",
  "answer": "Fail"
}}

---
EXAMPLE 2 (PASS — FM3 absent):
Query: "How do I set up my first eBay Live stream?"
Response: "eBay Live is currently invite-only and in beta for sellers. To set up your
first stream, you need to fill out the eBay Live Seller Interest Form to apply. You'll
need an active eBay account in good standing with demonstrated expertise in your category,
and ideally prior livestreaming experience and an established audience.
Once approved, prepare your setup: a smartphone or external camera, stable internet
(20+ Mbps upload), good lighting, tripod, and microphone. Test your audio and video
before going live. For detailed steps after approval, check ebay.com/help or the
eBay Live FAQ."

Evaluation:
{{
  "reasoning": "Every specific detail in this response comes from the KB: the Seller Interest Form name, the account requirements, technical setup requirements (20+ Mbps, camera, tripod, lighting, mic), testing audio/video before going live, and the escalation to ebay.com/help and eBay Live FAQ. No invented URLs, no invented UI navigation, no invented feature names. This is PASS.",
  "answer": "Pass"
}}

---
EXAMPLE 3 (FAIL — FM3 present):
Query: "Can I schedule a live stream to automatically start at midnight in a different time zone?"
Response: "eBay Live does not currently support scheduling a live stream to automatically
start at a specific time in a different time zone. You need to manually start the broadcast
at your desired time. It's best to plan your start time according to your local timezone
and inform your audience accordingly. If you want more details on scheduling, you can
check eBay Live resources or help pages."

Evaluation:
{{
  "reasoning": "The main issue here is whether 'eBay Live resources or help pages' counts as an invented process detail. 'ebay.com/help' and 'eBay Live FAQ' are in the KB; 'eBay Live resources' is vaguer but not a specific invented URL or location. The primary concern in this response is actually FM1 (out-of-scope claim about scheduling), not FM3. No specific URL or UI path is invented here. FM3 is not present.",
  "answer": "Pass"
}}

---
Now evaluate this response:

Query: {query}
Response: {response}

Return ONLY a JSON object with exactly two fields:
{{"reasoning": "your step-by-step reasoning here", "answer": "Pass" or "Fail"}}"""


def judge(query: str, response: str) -> dict:
    """
    Run the FM3 judge on a single (query, response) pair.

    Returns a dict with:
      - "reasoning": str — the judge's step-by-step explanation
      - "answer":    str — "Pass" or "Fail"
    """
    prompt = JUDGE_PROMPT.format(
        kb_details=KB_PROCESS_DETAILS,
        query=query,
        response=response,
    )

    result = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.0,
    )

    content = result["choices"][0]["message"]["content"].strip()

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"reasoning": content, "answer": "unknown"}


# -----------------------------------------------------------------------
# Test block — real traces from Stage 2 for quick verification
# -----------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = [
        {
            "name": "Invented URL ebay.com/live (FM3 failure)",
            "query": "How do I set up my first eBay Live stream to start selling?",
            "response": (
                "eBay Live is currently an invite-only beta for sellers. To set up your first "
                "stream, you need to apply by filling out the eBay Live Seller Interest Form. "
                "Once invited, prepare your setup with stable internet (20+ Mbps upload), "
                "smartphone or camera, tripod, good lighting, and a microphone. Test your "
                "audio and video before going live. If you want to get started, first submit "
                "the interest form at ebay.com/live and wait for approval."
            ),
            "expected": "Fail",
        },
        {
            "name": "All KB-grounded process details (FM3 pass)",
            "query": "How do I set up my first eBay Live stream?",
            "response": (
                "eBay Live is currently invite-only and in beta for sellers. Fill out the "
                "eBay Live Seller Interest Form to apply. You need an active eBay account in "
                "good standing with demonstrated expertise in your category, and ideally prior "
                "livestreaming experience. Once approved, prepare: smartphone or external camera, "
                "stable internet (20+ Mbps upload), good lighting, tripod, microphone. Test "
                "audio and video before going live. For more details, check ebay.com/help or "
                "the eBay Live FAQ."
            ),
            "expected": "Pass",
        },
        {
            "name": "Correct seller eligibility, no invented URLs (FM3 pass)",
            "query": "What are the specific requirements I need to meet to start hosting a live stream?",
            "response": (
                "To start hosting a live stream on eBay Live, you need to: have an active eBay "
                "account in good standing, demonstrate expertise in your category through "
                "transaction history, and complete the eBay Live Seller Interest Form. "
                "You should ideally have prior livestreaming experience and an established "
                "audience. Technical setup requires stable internet (20+ Mbps upload), "
                "smartphone or external camera, tripod, good lighting, external microphone, "
                "and ideally a second monitor for managing live chat."
            ),
            "expected": "Pass",
        },
        {
            "name": "Invented 'Seller Hub' navigation path (FM3 failure)",
            "query": "How do I start my eBay Live broadcast once I'm approved?",
            "response": (
                "Once you're approved as an eBay Live seller, go to your eBay Seller Hub and "
                "navigate to the Live section. Click the 'Go Live' button to start your broadcast. "
                "Make sure your camera and microphone are connected and tested before starting. "
                "You can manage your auction listings from the Stream Dashboard during the broadcast."
            ),
            "expected": "Fail",  # "Seller Hub", "Live section", "Go Live button", "Stream Dashboard" all invented
        },
    ]

    print("Testing FM3 Judge (Invented Process Details)")
    print("=" * 60)

    correct = 0
    for tc in test_cases:
        result = judge(tc["query"], tc["response"])
        got = result.get("answer", "unknown")
        expected = tc["expected"]
        status = "PASS" if got == expected else "FAIL"
        if got == expected:
            correct += 1

        print(f"\n[{status}] {tc['name']}")
        print(f"  Expected: {expected} | Got: {got}")
        print(f"  Reasoning: {result.get('reasoning', '')[:120]}...")

    print(f"\n{'=' * 60}")
    print(f"Results: {correct}/{len(test_cases)} correct")

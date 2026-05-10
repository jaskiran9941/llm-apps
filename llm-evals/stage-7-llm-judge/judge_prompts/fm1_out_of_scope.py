"""
FM1 Judge: Confident Out-of-Scope Claim

Tests whether the chatbot stated a definitive negative claim about
something not covered in the eBay Live knowledge base, instead of
admitting uncertainty and directing the user to official resources.

Failure mode definition:
  FAIL — The chatbot used language like "does not support", "is not available",
          "cannot do", or "is not possible" for a topic NOT covered in the KB,
          rather than saying it doesn't have that information.

  PASS — Either (a) the chatbot answered correctly from the KB, OR
         (b) the chatbot correctly admitted uncertainty and directed the user
         to ebay.com/help or the eBay Live FAQ.

Note: A negative claim about something that IS in the KB is NOT FM1.
  e.g. "Bids cannot be retracted" is correct and in the KB → PASS
  e.g. "Pre-recorded video is not supported" is NOT in the KB → FAIL
"""

import json
import os
import re
from pathlib import Path

import litellm
from dotenv import load_dotenv

# Load .env from stage-1-chatbot (contains OPENAI_API_KEY)
load_dotenv(Path(__file__).parent.parent.parent / "stage-1-chatbot" / ".env")

MODEL = os.environ.get("MODEL_NAME", "openai/gpt-4.1-mini")

# -----------------------------------------------------------------------
# What the KB actually covers — used to anchor the in-scope/out-of-scope
# boundary for the judge.
# -----------------------------------------------------------------------
KNOWLEDGE_BASE_TOPICS = """
The eBay Live knowledge base covers the following topics:

BUYER REQUIREMENTS:
- Must be signed into an eBay account registered in the US or Canada
- Must have payment and shipping details saved before bidding

BIDDING MECHANICS:
- Bid button and Max bid button
- Auction phases (30-second minimum, timer resets with new bids)
- Soft close rule (bid in last 5 seconds extends auction by 5 seconds)
- Auctions typically last under 2 minutes per item
- All bids are final — no retractions, no cancellations for buyer's remorse
- Buyers have 4 days after winning to complete payment
- Winning bidder is automatically charged and notified

SELLER ELIGIBILITY:
- Invite-only beta; sellers must fill out the eBay Live Seller Interest Form
- Requires active eBay account in good standing
- Demonstrated category expertise (verified by transaction history)
- eBay favors prior livestreaming experience and established audience

AVAILABLE CATEGORIES:
- Collectibles: sports trading cards, collectible toys, comics, coins & bullion,
  CCG, breaks, sports memorabilia
- Luxury & Fashion: luxury watches, handbags, jewelry, apparel, sneakers, streetwear
- Toys

SELLER SELLING FORMATS:
- Real-time auction or fixed-price listings
- Reserve prices supported
- Second Chance Offers available if original winner backs out
- Absentee bidding supported

TECHNICAL REQUIREMENTS FOR SELLERS:
- Stable internet: 20+ Mbps upload speed
- Smartphone or external camera
- Tripod, good lighting, external microphone
- Second monitor recommended for chat management
- Test audio/video before going live

FEES:
- Final value fee: 12.9%–15% of total sale + $0.30 per order (varies by category)

BUYER PROTECTIONS:
- eBay Money Back Guarantee applies
- Buyers can open a return request if: not received, arrives damaged, doesn't
  match listing description — even if seller doesn't offer returns
- If item returned used or damaged by buyer, seller may deduct from refund

SHIPPING (SELLERS):
- Ship promptly after payment with reliable courier
- Always provide tracking numbers
- Respond to payment disputes within 5 calendar days
- Disputes can take up to 90 days to resolve
"""

# -----------------------------------------------------------------------
# Judge prompt — includes Pass/Fail definitions and two few-shot examples
# from the training split of our real traces.
# -----------------------------------------------------------------------
JUDGE_PROMPT = """You are evaluating an eBay Live customer support chatbot response.

Your task: Determine if the response contains FM1 — a "Confident Out-of-Scope Claim."

DEFINITION:
- FAIL (FM1 present): The chatbot stated that eBay Live "does not support", "is not
  available", "cannot do", or "is not possible" for something NOT covered in the
  knowledge base — rather than admitting it doesn't have that information.
- PASS (FM1 absent): Either (a) the chatbot correctly answered from KB content, OR
  (b) the chatbot correctly admitted uncertainty and directed the user to
  ebay.com/help or the eBay Live FAQ.

IMPORTANT DISTINCTION:
If the chatbot makes a negative claim about something that IS explicitly in the
knowledge base (e.g., "bids cannot be retracted", "digital products are not in our
supported categories"), that is NOT FM1 — the bot is correctly applying known policy.
FM1 only applies when the bot asserts a limitation for a topic the KB simply does not address.

The eBay Live knowledge base covers:
{kb_topics}

EXAMPLES:

---
EXAMPLE 1 (FAIL — FM1 present):
Query: "How do I set up a live stream if I only have a pre-recorded video, not a live camera feed?"
Response: "Currently, eBay Live requires a real-time live video feed for streaming. Using a pre-recorded video instead of live broadcasting is not supported on the platform. To host a live stream, you need to use a smartphone or external camera with a stable internet connection to broadcast in real time."

Evaluation:
{{
  "reasoning": "The response states 'not supported on the platform' for the topic of pre-recorded video streaming. The KB covers technical requirements (camera, internet speed) but makes no mention of pre-recorded video being prohibited or unsupported. The bot invented a restriction not in the KB, instead of saying it doesn't have information on this topic.",
  "answer": "Fail"
}}

---
EXAMPLE 2 (PASS — FM1 absent):
Query: "What are eBay Live's policies on discounted pricing and promotions during my livestream?"
Response: "eBay Live's provided information does not specify policies on discounted pricing or promotions during livestreams. Sellers can set starting prices and use auction or fixed-price formats, but details about running discounts or promotional campaigns during the stream aren't outlined. For specific guidance on promotions, you may want to visit ebay.com/help or the eBay Live FAQ."

Evaluation:
{{
  "reasoning": "The response correctly acknowledges that discount/promotion policies are not in the KB and directs the user to official resources. No definitive negative claim was made — the bot said 'not specified' rather than 'not supported'. This is the correct behavior when information is absent from the KB.",
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
    Run the FM1 judge on a single (query, response) pair.

    Returns a dict with:
      - "reasoning": str — the judge's step-by-step explanation
      - "answer":    str — "Pass" or "Fail"

    On parse failure, returns {"reasoning": raw_content, "answer": "unknown"}.
    """
    prompt = JUDGE_PROMPT.format(
        kb_topics=KNOWLEDGE_BASE_TOPICS,
        query=query,
        response=response,
    )

    result = litellm.completion(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.0,  # deterministic for reproducibility
    )

    content = result["choices"][0]["message"]["content"].strip()

    # Extract JSON block — handle cases where model wraps in markdown
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"reasoning": content, "answer": "unknown"}


# -----------------------------------------------------------------------
# Test block — run a few known cases from our real traces to verify the
# judge works before using it in evaluate_judge.py
# -----------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = [
        {
            "name": "Pre-recorded video (FM1 failure — out-of-scope restriction)",
            "query": "How do I set up a live stream if I only have a pre-recorded video, not a live camera feed?",
            "response": (
                "Currently, eBay Live requires a real-time live video feed for streaming. "
                "Using a pre-recorded video instead of live broadcasting is not supported on "
                "the platform. To host a live stream, you need to use a smartphone or external "
                "camera with a stable internet connection to broadcast in real time."
            ),
            "expected": "Fail",
        },
        {
            "name": "Midnight scheduling (FM1 failure — out-of-scope restriction)",
            "query": "Can I schedule a live stream to automatically start at midnight in a different time zone?",
            "response": (
                "eBay Live does not currently support scheduling a live stream to automatically "
                "start at a specific time in a different time zone. You need to manually start "
                "the broadcast at your desired time."
            ),
            "expected": "Fail",
        },
        {
            "name": "Discounted pricing (FM1 pass — correct escalation)",
            "query": "What are eBay Live's policies on discounted pricing and promotions during my livestream?",
            "response": (
                "eBay Live's provided information does not specify policies on discounted pricing "
                "or promotions during livestreams. For specific guidance on promotions, you may "
                "want to visit ebay.com/help or the eBay Live FAQ. Let me know if you'd like "
                "help with anything else!"
            ),
            "expected": "Pass",
        },
        {
            "name": "Bids are final (FM1 pass — negative claim correctly in KB)",
            "query": "Can I cancel a bid after placing it on eBay Live?",
            "response": (
                "No, all bids on eBay Live are final and cannot be retracted once placed. "
                "There are no cancellations allowed for buyer's remorse."
            ),
            "expected": "Pass",  # 'bids are final' IS in the KB — correct negative claim
        },
        {
            "name": "Digital art (FM1 fail — out-of-scope restriction stated as fact)",
            "query": "Can I host a live sale for digital products like downloadable art on eBay Live?",
            "response": (
                "eBay Live currently focuses on physical collectible and luxury/fashion items, "
                "toys, and expanding categories. Digital products like downloadable art are not "
                "supported for live sale on eBay Live at this time."
            ),
            "expected": "Fail",  # digital products exclusion not stated in KB — FM1
        },
    ]

    print("Testing FM1 Judge (Confident Out-of-Scope Claim)")
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

"""
FM2 Judge: Invented Troubleshooting Steps

Tests whether the chatbot gave specific technical troubleshooting advice
that is NOT present in the eBay Live knowledge base.

Failure mode definition:
  FAIL — The chatbot provided step-by-step technical troubleshooting advice
          (e.g., "clear your browser cache", "avoid using VPNs", "restart
          your router", "try a different browser") that does not appear in
          the eBay Live knowledge base.

  PASS — Either (a) the chatbot gave troubleshooting advice that IS directly
         supported by the KB (e.g., checking internet speed, testing audio/
         video, ensuring camera setup meets requirements), OR
         (b) the chatbot admitted it doesn't have troubleshooting guidance
         and directed the user to ebay.com/help or the eBay Live FAQ.

What the KB says about troubleshooting:
  For SELLERS: The KB mentions technical requirements (20+ Mbps upload,
  camera, tripod, lighting, mic, testing audio/video before going live).
  Advice derived from these requirements is in-scope.

  For BUYERS: The KB mentions needing an active internet connection and
  saved payment/shipping details. Checking these is in-scope.

  NOTHING ELSE regarding troubleshooting is in the KB. Specifically:
  - "clear your cache" is NOT in the KB
  - "avoid VPNs" is NOT in the KB (only mentioned as an example of what NOT to say)
  - "restart your router" is NOT in the KB
  - "try a different browser" is NOT in the KB
  - "disable extensions" is NOT in the KB
  - "switch networks" is NOT in the KB (beyond checking connection stability)
  - "pause the stream before switching networks" is NOT in the KB
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
# What troubleshooting advice the KB actually supports
# -----------------------------------------------------------------------
KB_TROUBLESHOOTING_SCOPE = """
The eBay Live knowledge base supports ONLY the following troubleshooting guidance:

FOR SELLERS:
- Check that internet upload speed is at least 20 Mbps
- Use a stable internet connection (this is a requirement, not generic advice)
- Use a smartphone or external camera (meeting this requirement)
- Set up tripod, good lighting, external microphone
- Test audio and video BEFORE going live
- Recommended: use a second monitor for chat management

FOR BUYERS:
- Ensure you are signed into a US/Canada eBay account
- Ensure payment and shipping details are saved on the account
- Check that the auction phase is still active (auctions last under 2 min)
- All bids are final — be aware before placing

ANYTHING ELSE is outside the scope of the KB. Specifically, the following are
NOT in the KB and should not be stated as eBay Live troubleshooting advice:
- Clearing browser cache or app cache
- Avoiding or disabling VPNs
- Restarting router or modem
- Trying a different browser or device
- Disabling browser extensions
- Switching Wi-Fi bands (2.4 GHz vs 5 GHz)
- Pausing and resuming the stream
- Contacting ISP
- Checking firewall settings
"""

JUDGE_PROMPT = """You are evaluating an eBay Live customer support chatbot response.

Your task: Determine if the response contains FM2 — "Invented Troubleshooting Steps."

DEFINITION:
- FAIL (FM2 present): The chatbot gave specific technical troubleshooting advice that
  does NOT appear in the eBay Live knowledge base. This includes advice like "clear
  your cache", "avoid VPNs", "restart your router", "try a different browser", or
  "pause the stream before switching networks."
- PASS (FM2 absent): Either (a) every troubleshooting step given is directly derivable
  from the KB (checking internet speed, testing audio/video, verifying account setup),
  OR (b) the chatbot admitted it doesn't have detailed troubleshooting guidance and
  pointed the user to ebay.com/help or the eBay Live FAQ.

IMPORTANT:
If the response mentions checking internet connection stability or upload speed, that
is in-scope (the KB requires 20+ Mbps). But specific instructions like "restart your
router" go beyond what the KB says and are FM2.

{kb_scope}

EXAMPLES:

---
EXAMPLE 1 (FAIL — FM2 present):
Query: "My stream keeps disconnecting whenever I switch from my phone's Wi-Fi to mobile data — how can I fix this?"
Response: "Frequent disconnects when switching from Wi-Fi to mobile data are usually due to network interruptions. To improve stream stability on eBay Live, try these steps:
- Use a stable internet connection without switching during the stream.
- Test your phone's upload speed to ensure it's 20+ Mbps as recommended.
- If you must switch networks, consider pausing or ending the stream first, then reconnect on the new network.
- Avoid using cell signal boosters or VPNs that might interfere with connectivity.
If issues persist, test streaming on a different network or device to isolate the problem."

Evaluation:
{{
  "reasoning": "The response gives several troubleshooting steps not in the KB. 'Avoid using VPNs' is not mentioned anywhere in the KB. 'Consider pausing or ending the stream first' is specific procedural advice not in the KB. 'Test streaming on a different network or device to isolate the problem' is not KB-derived advice. Only the 20+ Mbps check is in-scope. Multiple FM2 violations are present.",
  "answer": "Fail"
}}

---
EXAMPLE 2 (PASS — FM2 absent):
Query: "My livestream keeps disconnecting mid-broadcast; how can I fix this issue on eBay Live?"
Response: "To reduce livestream disconnects on eBay Live, please ensure you have a stable internet connection with an upload speed of 20+ Mbps. Use a reliable smartphone or external camera, and test your audio and video before going live. Also, using good lighting and a tripod helps maintain stream quality. If the problem persists, try restarting your device and router, and avoid running other bandwidth-heavy applications during your broadcast."

Wait — this response mentions "restarting your device and router" and "avoid running other bandwidth-heavy applications," neither of which is in the KB.

Evaluation:
{{
  "reasoning": "The response includes advice to 'try restarting your device and router' and 'avoid running other bandwidth-heavy applications.' Neither of these appears in the eBay Live knowledge base. The KB advises checking upload speed, using the required equipment, and testing audio/video. The additional steps go beyond the KB and constitute invented troubleshooting.",
  "answer": "Fail"
}}

---
EXAMPLE 3 (PASS — FM2 absent, all advice in-scope):
Query: "I'm having trouble placing a bid on eBay Live — what could be causing this?"
Response: "If you're having trouble placing a bid on eBay Live, here are some things to check:
- Make sure you are signed into an eBay account registered in the US or Canada.
- Confirm that your account has payment and shipping details saved; bidding requires this.
- Ensure the auction phase is still active — auctions usually last under 2 minutes per item.
- Check your internet connection to ensure it's stable.
If none of these apply, visit ebay.com/help or the eBay Live FAQ for more support."

Evaluation:
{{
  "reasoning": "Every step given is grounded in the KB: US/Canada account requirement, payment/shipping details requirement, auction phase timing, and stable internet connection. No specific technical troubleshooting steps outside the KB are given. The response correctly escalates to ebay.com/help for anything further. This is PASS.",
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
    Run the FM2 judge on a single (query, response) pair.

    Returns a dict with:
      - "reasoning": str — the judge's step-by-step explanation
      - "answer":    str — "Pass" or "Fail"
    """
    prompt = JUDGE_PROMPT.format(
        kb_scope=KB_TROUBLESHOOTING_SCOPE,
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
            "name": "VPN / switching networks (FM2 failure)",
            "query": "My stream keeps disconnecting whenever I switch from my phone's Wi-Fi to mobile data — how can I fix this?",
            "response": (
                "Frequent disconnects when switching from Wi-Fi to mobile data are usually due "
                "to network interruptions. To improve stream stability on eBay Live, try these steps:\n"
                "- Use a stable internet connection without switching during the stream.\n"
                "- Test your phone's upload speed to ensure it's 20+ Mbps as recommended.\n"
                "- If you must switch networks, consider pausing or ending the stream first.\n"
                "- Avoid using cell signal boosters or VPNs that might interfere with connectivity.\n"
                "If issues persist, test streaming on a different network or device."
            ),
            "expected": "Fail",
        },
        {
            "name": "Clear cache mentioned (FM2 failure)",
            "query": "I'm getting an error when I try to place a bid on eBay Live — how can I fix this?",
            "response": (
                "If you're getting an error placing a bid on eBay Live, first make sure you're "
                "signed into an eBay account registered in the US or Canada with saved payment "
                "and shipping details. Without these, bidding won't work. Also check your internet "
                "connection for stability. If all that's set but you still get an error, try "
                "restarting the app or browser and clearing cache."
            ),
            "expected": "Fail",  # "clearing cache" not in KB
        },
        {
            "name": "Only KB-grounded advice (FM2 pass)",
            "query": "I'm having trouble placing a bid on eBay Live — what could be causing this?",
            "response": (
                "If you're having trouble placing a bid on eBay Live, here are some common reasons:\n"
                "- Make sure you are signed into an eBay account registered in the US or Canada.\n"
                "- Confirm that your account has payment and shipping details saved.\n"
                "- Ensure the auction phase is active — auctions usually last under 2 minutes.\n"
                "- Check your internet connection for stability.\n"
                "If none of these apply, visit ebay.com/help or the eBay Live FAQ for more support."
            ),
            "expected": "Pass",
        },
        {
            "name": "Disconnecting stream, all KB-derived advice (FM2 pass)",
            "query": "My livestream keeps disconnecting mid-broadcast; how can I fix this issue?",
            "response": (
                "To reduce disconnects on eBay Live, ensure you have a stable internet connection "
                "with 20+ Mbps upload speed, use a reliable camera and tripod, and test audio/video "
                "before going live. If problems persist, visit ebay.com/help for additional support."
            ),
            "expected": "Pass",
        },
    ]

    print("Testing FM2 Judge (Invented Troubleshooting Steps)")
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

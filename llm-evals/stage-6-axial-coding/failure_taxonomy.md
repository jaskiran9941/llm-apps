# eBay Live Failure Taxonomy
*Derived from axial coding of 36 traces — Stage 4*

*Each failure mode is binary: present (1) or absent (0) per trace. Pass/Fail definitions feed directly into Stage 5 LLM judge prompts.*

---

## FM1: Confident Out-of-Scope Claim

**Definition**: Bot asserts that eBay Live does NOT support or have something, for a topic not covered in the knowledge base — instead of saying "I don't know."

**Pass**: Bot says it doesn't have information about that topic and directs the user to ebay.com/help or the eBay Live FAQ.

**Fail**: Bot states a definitive "eBay Live does not support X" or "X is not available" for topics not addressed in the KB.

**Examples from traces**: Trace 24 (pre-recorded video: "Using a pre-recorded video is not currently supported"), Trace 36 (scheduling: "eBay Live does not support scheduling"), Trace 30 (digital products: "Digital products are not supported for live sale")

**Why it's dangerous**: Users make real decisions based on invented policies. A seller might abandon a valid use case because the bot incorrectly told them it's not supported.

**Frequency**: High | **Severity**: High

---

## FM2: Invented Troubleshooting Steps

**Definition**: Bot provides specific technical troubleshooting advice — steps, settings, workarounds, or connectivity guidance — that is not present in the knowledge base.

**Pass**: Bot acknowledges it doesn't have troubleshooting guidance for this issue and directs the user to eBay support or the Help Center.

**Fail**: Bot gives specific technical steps (e.g., clear cache, restart app, avoid VPNs, adjust encoder settings) that are not grounded in the KB.

**Examples from traces**: Trace 7 ("try restarting the app or browser and clearing cache"), Trace 14 ("Avoid using cell signal boosters or VPNs during your live session"), Trace 22 (specific encoder settings stated as standard guidance)

**Why it's dangerous**: Users waste time following unverified steps. Worse, users may conclude their real problem is unsolvable after the invented steps fail. It creates a false impression of technical depth.

**Frequency**: Medium | **Severity**: Medium

---

## FM3: Invented Process Details

**Definition**: Bot describes specific workflows, URLs, feature capabilities, or step-by-step processes that are not present in the knowledge base.

**Pass**: Bot describes only what is explicitly stated in the KB; for anything beyond that, it says it doesn't have that information.

**Fail**: Bot invents specific URLs (e.g., "ebay.com/live/interest-form"), describes features that don't exist or aren't documented (e.g., scheduling a livestream), or outlines workflows not grounded in the KB.

**Examples from traces**: Trace 3 ("submit the interest form at ebay.com/live"), Trace 17 (detailed description of how to schedule a livestream — scheduling not in KB), Trace 9 (multi-seller collaboration workflow invented wholesale)

**Why it's dangerous**: Users follow non-existent workflows. They may spend time trying to find URLs that don't exist or waiting for features that aren't available.

**Distinction from FM1**: FM1 is negative assertions ("X is not supported"). FM3 is positive assertions ("here's how to do X") where X doesn't exist in the KB. Both are hallucinations but with opposite valence.

**Frequency**: High | **Severity**: High

---

## FM4: Failure to Escalate on Truly Unknown Topics

**Definition**: Bot gives a confident, substantive answer to a question that is genuinely outside its knowledge base and domain, instead of saying "I don't know" and referring the user elsewhere.

**Pass**: Bot recognizes the question is outside its domain, says it doesn't have that information, and directs the user to ebay.com/help or a more appropriate resource.

**Fail**: Bot addresses an out-of-scope topic with confident framing (e.g., "eBay Live is best used as a complementary sales channel" for an inventory management question) or invents integration details for systems not covered in the KB.

**Examples from traces**: Trace 8 (inventory management integration — bot gave high-level framing instead of escalating), Trace 15 (third-party analytics tools — bot invented integration specifics), Trace 33 (tax/accounting implications — bot speculated instead of deferring)

**Correct handling (counter-examples)**: Trace 19 and Trace 21 correctly deferred on out-of-scope questions. FM4 is specifically when that deferral fails.

**Why it's dangerous**: Users trust the bot's framing as authoritative. Confident-sounding answers on topics the bot doesn't know create false confidence and bad decisions.

**Distinction from FM2**: FM2 is inventing technical depth within a broadly in-scope topic (eBay Live troubleshooting). FM4 is drifting to a different domain entirely (inventory management, tax, third-party integrations) without recognizing the topic is out of scope.

**Frequency**: Medium | **Severity**: High

---

## FM5: Potentially Misleading Inference

**Definition**: Bot makes a plausible but unverified inference from KB content, stating it as established fact, in a way that could mislead users.

**Pass**: Bot clearly signals uncertainty ("I'm not certain, but…" or "you may want to verify this") when stating anything not directly grounded in the KB, or avoids making the inference entirely.

**Fail**: Bot states a reasonable-sounding inference as authoritative guidance without any hedging (e.g., "avoid placing duplicate bids for the same amount" stated as policy when the KB doesn't address this).

**Examples from traces**: Trace 29 ("avoid placing duplicate bids for the same amount" — bidding mechanics not addressed in KB), Trace 18 ("eBay Live focuses on livestream video shopping through standard devices" — invented framing stated as fact), Trace 31 (inferred seller eligibility rules stated as definitive requirements)

**Why it's dangerous**: Reasonable-sounding inferences are harder for users to question than obvious hallucinations. The bot's inference might be wrong in a specific edge case, and the user has no signal to disbelieve it.

**Distinction from FM1 and FM3**: FM5 is *hedgeable* — the bot could have said "I'm not certain about this." FM1 and FM3 involve inventing things that simply don't exist in the KB. FM5 involves overstating confidence about inferences that might be reasonable but are not documented.

**Frequency**: Low | **Severity**: Medium

---

## Summary Table

| ID | Name | Definition (one line) | Frequency | Severity |
|----|------|-----------------------|-----------|----------|
| FM1 | Confident Out-of-Scope Claim | Bot asserts "X is not supported" for a KB-absent topic | High | High |
| FM2 | Invented Troubleshooting Steps | Bot gives specific technical steps not in the KB | Medium | Medium |
| FM3 | Invented Process Details | Bot describes workflows, URLs, or features not in the KB | High | High |
| FM4 | Failure to Escalate | Bot answers confidently on genuinely out-of-scope topics | Medium | High |
| FM5 | Potentially Misleading Inference | Bot states reasonable inference as fact without hedging | Low | Medium |

---

## Annotation Guide

When applying this taxonomy to a new trace, check each failure mode independently:

1. **FM1 check**: Does the response contain any statement of the form "eBay Live does not support X" or "X is not available" where X is not addressed in the KB?
2. **FM2 check**: Does the response give specific technical troubleshooting steps (restart, clear cache, VPN, encoder settings, etc.) that are not grounded in the KB?
3. **FM3 check**: Does the response describe a specific URL, workflow, or feature that is not in the KB?
4. **FM4 check**: Is the question genuinely outside the eBay Live domain, and did the bot answer confidently instead of deferring?
5. **FM5 check**: Does the response state an inference as fact where the KB does not directly support the specific claim, without any hedging?

A trace can have multiple failure modes. Score each independently as 0 or 1.

# eBay Live Eval Dimensions

Dimensions define the axes along which we vary test queries to ensure coverage of likely failure modes.

## Dimension 1: User Type
Who is asking the question?
- `buyer` — someone who wants to watch/bid/buy on eBay Live
- `seller` — someone who wants to host a live stream and sell

## Dimension 2: Query Type
What kind of information are they seeking?
- `policy` — rules, terms, what is/isn't allowed
- `how-to` — step-by-step process questions
- `eligibility` — can I do X? do I qualify?
- `categories` — what can be sold/bought
- `troubleshooting` — something went wrong or I'm confused
- `out-of-scope` — question the bot genuinely cannot answer from its knowledge base

## Dimension 3: Scenario
How well-formed is the query?
- `clear` — specific, unambiguous question
- `ambiguous` — underspecified or could be interpreted multiple ways
- `edge-case` — unusual situation that tests the boundaries of the knowledge base

## Example Tuples

| User Type | Query Type | Scenario | Example Query |
|-----------|-----------|----------|---------------|
| buyer | policy | clear | "Can I cancel a bid after placing it?" |
| buyer | how-to | ambiguous | "How do I get started with eBay Live?" |
| seller | eligibility | clear | "Do I need a certain number of past sales to qualify?" |
| seller | categories | edge-case | "Can I sell vintage sneakers on eBay Live?" |
| buyer | out-of-scope | clear | "Does eBay Live have a TikTok-style feed?" |
| seller | troubleshooting | ambiguous | "My stream isn't working, what do I do?" |

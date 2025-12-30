"""Transaction Reader Agent - Analyzes Gmail purchases using Claude."""
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from gmail_helper import get_gmail_service, get_emails

# Load environment variables
load_dotenv()

class TransactionReaderAgent:
    """Agent that analyzes email purchases and provides insights."""

    def __init__(self):
        """Initialize the agent with Claude API."""
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.gmail_service = None
        self.transactions = []

    def authenticate_gmail(self, account_name='default'):
        """Authenticate with Gmail API.

        Args:
            account_name: Account identifier for multi-account support
        """
        print(f"Authenticating with Gmail ({account_name})...")
        self.gmail_service = get_gmail_service(account_name)
        print("✓ Gmail authentication successful!")

    def fetch_emails(self, max_results=100, days_back=30, account_name='default'):
        """Fetch recent emails that might contain purchases from a single account.

        Args:
            max_results: Maximum number of emails to fetch
            days_back: Number of days to look back
            account_name: Account identifier

        Returns:
            List of email dictionaries
        """
        print(f"\nFetching emails from {account_name}...")

        # Get service for this account
        service = get_gmail_service(account_name)

        # Query for common purchase-related emails
        query = f'subject:(receipt OR order OR purchase OR confirmation OR invoice OR payment) newer_than:{days_back}d'

        emails = get_emails(service, max_results=max_results, query=query)
        print(f"✓ Fetched {len(emails)} emails from {account_name}")
        return emails

    def fetch_emails_from_accounts(self, account_names, max_results=100, days_back=30):
        """Fetch emails from multiple accounts and combine them.

        Args:
            account_names: List of account identifiers
            max_results: Maximum emails per account
            days_back: Number of days to look back

        Returns:
            Combined list of emails from all accounts
        """
        all_emails = []

        for account_name in account_names:
            try:
                emails = self.fetch_emails(max_results, days_back, account_name)
                # Tag emails with account name
                for email in emails:
                    email['account'] = account_name
                all_emails.extend(emails)
            except Exception as e:
                print(f"Error fetching from {account_name}: {e}")

        print(f"\n✓ Total: Fetched {len(all_emails)} emails from {len(account_names)} account(s)")
        return all_emails

    def analyze_emails_for_purchases(self, emails):
        """Use Claude to analyze emails and extract purchase information."""
        print("\nAnalyzing emails for purchases...")

        # Prepare email data for Claude
        email_batch = []
        for email in emails[:20]:  # Process in batches to manage token usage
            email_batch.append({
                'subject': email['subject'],
                'from': email['from'],
                'date': email['date'],
                'body_preview': email['body'][:2000]  # First 2000 chars for better extraction
            })

        # Create prompt for Claude
        prompt = f"""Analyze these emails and extract purchase transactions. For each email that contains a purchase, extract:
- merchant/vendor name
- total amount (with currency)
- date of purchase
- items purchased (if mentioned)
- category (groceries, dining, entertainment, shopping, transportation, utilities, subscriptions, healthcare, other)

Emails to analyze:
{json.dumps(email_batch, indent=2)}

Return a JSON array of transactions. Only include actual purchases (not promotional emails). Format:
[
  {{
    "merchant": "Amazon",
    "amount": 45.99,
    "currency": "USD",
    "date": "2024-03-15",
    "items": ["Book", "Phone case"],
    "category": "shopping"
  }}
]

If no purchases found, return an empty array []."""

        # Call Claude
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse response
        response_text = response.content[0].text
        print(f"\nClaude's response:\n{response_text}\n")

        try:
            # Try to extract JSON from response (might be wrapped in markdown)
            if "```json" in response_text:
                # Extract JSON from code block
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                # Extract from generic code block
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            transactions = json.loads(response_text)
            self.transactions.extend(transactions)
            print(f"✓ Found {len(transactions)} purchases")
            return transactions
        except json.JSONDecodeError as e:
            print(f"Error parsing Claude's response: {e}")
            return []

    def categorize_and_analyze(self):
        """Analyze spending patterns and generate insights."""
        print("\nAnalyzing spending patterns...")

        if not self.transactions:
            print("No transactions to analyze!")
            return

        prompt = f"""Analyze these purchase transactions and provide insights:

Transactions:
{json.dumps(self.transactions, indent=2)}

Please provide:
1. **Total Spending**: Overall total and breakdown by category
2. **Top Categories**: What am I spending the most on?
3. **Top Merchants**: Which merchants do I use most frequently?
4. **Spending Patterns**: Any notable patterns (frequency, typical amounts, etc.)
5. **Suggestions**: 3-5 actionable suggestions to optimize spending

Format your response as a clear, structured analysis."""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        analysis = response.content[0].text
        return analysis

    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("Transaction Reader Agent")
        print("=" * 60)

        # Step 1: Authenticate Gmail
        self.authenticate_gmail()

        # Step 2: Fetch emails
        emails = self.fetch_emails(max_results=50)

        if not emails:
            print("\nNo emails found!")
            return

        # Step 3: Analyze for purchases
        self.analyze_emails_for_purchases(emails)

        # Step 4: Generate insights
        if self.transactions:
            print("\n" + "=" * 60)
            print("SPENDING ANALYSIS")
            print("=" * 60 + "\n")

            analysis = self.categorize_and_analyze()
            print(analysis)

            # Save transactions to file
            with open('transactions.json', 'w') as f:
                json.dump(self.transactions, f, indent=2)
            print(f"\n✓ Saved {len(self.transactions)} transactions to transactions.json")
        else:
            print("\nNo purchases found in the analyzed emails.")


if __name__ == "__main__":
    agent = TransactionReaderAgent()
    agent.run()

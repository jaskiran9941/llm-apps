"""Email delivery using SendGrid."""
import os
from typing import Dict, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import markdown
import ssl
import urllib3


class EmailSender:
    """Handles email composition and delivery via SendGrid."""

    def __init__(self):
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")

        # Disable SSL verification for corporate proxies
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.client = SendGridAPIClient(api_key)
        # Disable SSL verification in the underlying HTTP client
        if hasattr(self.client, 'client') and hasattr(self.client.client, 'session'):
            self.client.client.session.verify = False

        self.from_email = os.getenv('FROM_EMAIL', 'noreply@podcast-digest.com')
        self.to_email = os.getenv('TO_EMAIL')

        if not self.to_email:
            raise ValueError("TO_EMAIL environment variable is required")

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML for email."""
        html = markdown.markdown(
            markdown_text,
            extensions=['extra', 'nl2br', 'sane_lists']
        )

        # Add basic email styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #1a1a1a;
                    border-bottom: 3px solid #4A90E2;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #2c3e50;
                    margin-top: 30px;
                    border-left: 4px solid #4A90E2;
                    padding-left: 15px;
                }}
                h3 {{
                    color: #34495e;
                }}
                a {{
                    color: #4A90E2;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                hr {{
                    border: none;
                    border-top: 2px solid #e0e0e0;
                    margin: 30px 0;
                }}
                ul {{
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e0e0e0;
                    font-size: 0.9em;
                    color: #666;
                    text-align: center;
                }}
                .emoji {{
                    font-size: 1.2em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html}
                <div class="footer">
                    <p>This is your automated podcast digest. To manage your subscriptions, update your podcast configuration.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return styled_html

    def send_digest(self, digest_content: str, recommendations: Dict) -> bool:
        """
        Send the daily podcast digest email.

        Args:
            digest_content: Markdown-formatted digest content
            recommendations: Podcast recommendations dictionary

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Combine digest and recommendations
            full_content = digest_content + "\n\n---\n\n"
            full_content += "# 💡 Podcasts You Might Like\n\n"
            full_content += recommendations.get('recommendations_text', '')

            # Convert to HTML
            html_content = self._markdown_to_html(full_content)

            # Create email
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(self.to_email),
                subject='🎧 Your Daily Podcast Digest',
                html_content=Content("text/html", html_content)
            )

            # Send email
            response = self.client.send(message)

            if response.status_code >= 200 and response.status_code < 300:
                print(f"✅ Email sent successfully to {self.to_email}")
                return True
            else:
                print(f"❌ Failed to send email. Status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def send_test_email(self) -> bool:
        """Send a test email to verify configuration."""
        test_content = """
# 🎧 Test Podcast Digest

This is a test email to verify your podcast summarizer is configured correctly.

## Test Episode
**Podcast:** Example Podcast
**Episode:** Test Episode
**Summary:** If you're receiving this, your email integration is working!

## Next Steps
1. Add your favorite podcasts to `config/podcasts.json`
2. Set up the GitHub Actions workflow
3. Start receiving daily digests!

---

**Note:** This is a test email. You can safely ignore it.
"""

        html_content = self._markdown_to_html(test_content)

        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(self.to_email),
                subject='🧪 Test: Podcast Digest Setup',
                html_content=Content("text/html", html_content)
            )

            response = self.client.send(message)

            if response.status_code >= 200 and response.status_code < 300:
                print(f"✅ Test email sent successfully to {self.to_email}")
                return True
            else:
                print(f"❌ Failed to send test email. Status code: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error sending test email: {e}")
            return False

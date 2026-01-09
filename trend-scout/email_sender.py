"""Email digest sender using Composio Gmail."""
import os
from datetime import datetime

from composio import ComposioToolSet, Action
from rich.console import Console

console = Console()


class EmailSender:
    """Send email digests via Composio Gmail integration."""

    def __init__(self):
        self.toolset = ComposioToolSet()
        self._authenticated = False

    def check_auth(self) -> bool:
        """Check if Gmail is authenticated with Composio."""
        try:
            connections = self.toolset.get_connected_accounts()
            for conn in connections:
                if conn.appName.lower() == "gmail":
                    self._authenticated = True
                    return True
            return False
        except Exception as e:
            console.print(f"[red]Error checking Gmail auth: {e}[/red]")
            return False

    def authenticate(self) -> str:
        """Initiate Gmail OAuth flow via Composio."""
        try:
            connection_request = self.toolset.initiate_connection(
                app="gmail",
                redirect_url="https://backend.composio.dev/api/v1/auth-apps/add"
            )
            return connection_request.redirectUrl
        except Exception as e:
            console.print(f"[red]Error initiating Gmail auth: {e}[/red]")
            return ""

    async def send_digest(
        self,
        to_email: str,
        subject: str,
        html_body: str,
    ) -> bool:
        """
        Send the digest email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content of the digest
        """
        if not self._authenticated and not self.check_auth():
            console.print("[yellow]Gmail not authenticated. Run setup first.[/yellow]")
            return False

        try:
            result = self.toolset.execute_action(
                action=Action.GMAIL_SEND_EMAIL,
                params={
                    "to": to_email,
                    "subject": subject,
                    "body": html_body,
                    "is_html": True,
                }
            )

            if result.get("successful"):
                console.print(f"[green]Email sent to {to_email}[/green]")
                return True
            else:
                console.print(f"[red]Failed to send email: {result.get('error')}[/red]")
                return False

        except Exception as e:
            console.print(f"[red]Error sending email: {e}[/red]")
            return False

    async def send_trend_digest(
        self,
        to_email: str,
        digest_html: str,
        topics: list[str],
    ) -> bool:
        """Send the trend scout digest."""
        date_str = datetime.now().strftime("%B %d, %Y")
        subject = f"Trend Scout Digest - {date_str}"

        return await self.send_digest(
            to_email=to_email,
            subject=subject,
            html_body=digest_html,
        )


# For testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    sender = EmailSender()

    if sender.check_auth():
        console.print("[green]Gmail is authenticated![/green]")
    else:
        console.print("[yellow]Gmail not authenticated.[/yellow]")
        auth_url = sender.authenticate()
        if auth_url:
            console.print(f"Visit this URL to authenticate:\n{auth_url}")

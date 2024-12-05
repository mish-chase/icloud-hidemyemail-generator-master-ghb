import asyncio
import datetime
import os
import re
import random
from typing import Union, List

from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table, box, Column

from icloud import HideMyEmail

# Configuration constants
MAX_CONCURRENT_TASKS = 3
SLEEP_INTERVAL = 30 * 60  # Default sleep interval in seconds
COUNT_TO_GENERATE = 30  # Number of emails to generate per session
DELAY_BETWEEN_CREATIONS = (5, 10)  # Delay between each email creation (min, max) in seconds


class RichHideMyEmail(HideMyEmail):
    _cookie_file = "cookie.txt"

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.table = Table(
            Column("Label", style="bold white"),
            Column("Email", style="bold cyan"),
            Column("Creation Time", style="bold white"),
            Column("Status", style="bold cyan"),
            style="bold green",
            box=box.MINIMAL,
        )
        self.generated_emails = set()  # Track unique emails for the session

        if os.path.exists(self._cookie_file):
            # Load cookie string from file
            with open(self._cookie_file, "r") as f:
                self.cookies = [line.strip() for line in f if not line.startswith("//")][0]
        else:
            self.console.log(
                '[bold yellow][WARN][/] No "cookie.txt" file found! Generation might not work due to unauthorized access.'
            )

    async def _generate_one(self) -> Union[str, None]:
        """Generate and reserve a single email."""
        try:
            # Generate email
            gen_res = await self.generate_email()
            if not gen_res:
                raise ValueError("No response from API during email generation.")
            if not gen_res.get("success"):
                error_message = gen_res.get("reason", "Unknown reason")
                raise ValueError(f"Email generation failed: {error_message}")

            email = gen_res["result"]["hme"]
            if email in self.generated_emails:
                self.console.log(f'[yellow][SKIP] "{email}" - Already generated in this session.')
                return None

            self.generated_emails.add(email)
            self.console.log(f'[50%] "{email}" - Successfully generated')

            # Reserve email
            reserve_res = await self.reserve_email(email)
            if not reserve_res:
                self.console.log(f"[bold red][DEBUG][/] Reservation API response: {reserve_res}")
                raise ValueError(f"Email reservation failed for '{email}': No response from API.")
            if not reserve_res.get("success"):
                # Handle Reservation API limit reached
                error_code = reserve_res["error"].get("errorCode")
                error_message = reserve_res["error"].get("errorMessage", "Unknown reason")
                self.console.log(f"[bold red][DEBUG][/] Reservation API response: {reserve_res}")
                if error_code == "-41015":
                    self.console.log(
                        f"[bold red][ERR][/] Reservation API limit reached: {error_message}. "
                        "Pausing for 30-40 minutes..."
                    )
                    await asyncio.sleep(30 * 60)  # Pause for 30 minutes
                raise ValueError(f"Email reservation failed for '{email}': {error_message}")

            self.console.log(f'[100%] "{email}" - Successfully reserved')

            # Add delay between each email creation
            delay = random.uniform(*DELAY_BETWEEN_CREATIONS)
            self.console.log(f"[bold yellow]Delaying for {delay:.2f} seconds before the next attempt...")
            await asyncio.sleep(delay)

            return email
        except ValueError as ve:
            self.console.log(f'[bold red][ERR][/] {ve}')
            return None
        except Exception as e:
            self.console.log(f'[bold red][ERR][/] Unexpected error: {e}')
            return None

    async def _generate(self, num: int):
        """Generate multiple emails with explicit delay between each."""
        emails = []
        for _ in range(num):
            email = await self._generate_one()
            if email:
                emails.append(email)

            # Add delay after each attempt, regardless of success or failure
            delay = random.uniform(*DELAY_BETWEEN_CREATIONS)
            self.console.log(f"[bold yellow]Delaying for {delay:.2f} seconds before the next attempt...")
            await asyncio.sleep(delay)

        return emails

    async def generate(self) -> List[str]:
        """Main email generation loop."""
        try:
            self.console.rule("[bold green]Starting Email Generation")
            emails = []
            with self.console.status("[bold green]Generating iCloud emails..."):
                for _ in range(0, COUNT_TO_GENERATE, MAX_CONCURRENT_TASKS):
                    batch = await self._generate(MAX_CONCURRENT_TASKS)
                    emails.extend(batch)
                    self.console.log(
                        f"[cyan]Generated {len(batch)} unique emails in this batch. Sleeping for {SLEEP_INTERVAL / 60:.1f} minutes..."
                    )
                    await asyncio.sleep(SLEEP_INTERVAL)
            self.console.log(f"[bold green]Total unique emails generated: {len(emails)}")
            return emails
        except KeyboardInterrupt:
            self.console.log("[bold red]Generation interrupted!")
            return []

    async def list(self, active: bool, search: str = None) -> None:
        """List emails with optional filters."""
        self.console.rule("[bold green]Fetching Email List")
        with self.console.status("[bold green]Getting iCloud emails..."):
            gen_res = await self.list_email()

        if not gen_res or not gen_res.get("success"):
            self.console.log("[bold red][ERR][/] Failed to fetch email list.")
            return

        email_strings = []
        for email in gen_res["result"]["hmeEmails"]:
            status = "Active" if email["isActive"] else "Inactive"
            creation_time = datetime.datetime.fromtimestamp(
                email["createTimestamp"] / 1000
            ).strftime("%y-%m-%d %H:%M")
            email_strings.append(f"{email['label']};{email['hme']};{creation_time};{status}")
            if email["isActive"] == active and (not search or re.search(search, email["label"])):
                self.table.add_row(
                    email["label"],
                    email["hme"],
                    creation_time,
                    status,
                )
        self.console.print(self.table)
        with open("emails.txt", "w", encoding="utf-8") as f:
            f.write(os.linesep.join(email_strings))
        self.console.log('[bold green]Email list written to "emails.txt"')


async def generate() -> None:
    """Helper function to start email generation."""
    async with RichHideMyEmail() as hme:
        await hme.generate()


async def list(active: bool, search: str = None) -> None:
    """Helper function to list emails."""
    async with RichHideMyEmail() as hme:
        await hme.list(active, search)


async def ask_action() -> None:
    """Prompt the user for an action."""
    async with RichHideMyEmail() as hme:
        try:
            hme.console.rule("[bold green]Action Menu")
            action = Prompt.ask(
                "[bold cyan]1.[/bold cyan] Generate emails\n"
                "[bold cyan]2.[/bold cyan] List emails\n"
                "[bold green]Select your action (Ctrl+C to exit)[reset]",
                console=hme.console
            ).strip()
            if action == "1":
                await hme.generate()
            elif action == "2":
                await hme.list(True)
            else:
                hme.console.log("[bold red]Invalid option selected!")
        except (KeyboardInterrupt, ValueError):
            hme.console.log("[bold yellow]Exiting... Goodbye!")


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(ask_action())
    except KeyboardInterrupt:
        pass

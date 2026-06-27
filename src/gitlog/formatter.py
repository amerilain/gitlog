"""Output formatting for gitlog using Rich."""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()


def print_commit_message(message: str) -> None:
    """Print a generated commit message with pretty formatting."""
    panel = Panel(
        Syntax(message, "bash", theme="monokai", word_wrap=True),
        title="[bold green]Commit Message[/]",
        border_style="green",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def print_changelog_entry(entry: str) -> None:
    """Print a generated changelog entry with pretty formatting."""
    panel = Panel(
        entry.strip(),
        title="[bold blue]Changelog Entry[/]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)
    console.print()


def print_both(commit_message: str, changelog_entry: str) -> None:
    """Print both commit message and changelog entry."""
    # Commit message panel
    commit_panel = Panel(
        Syntax(commit_message, "bash", theme="monokai", word_wrap=True),
        title="[bold green]Commit Message[/]",
        border_style="green",
        padding=(1, 2),
    )
    console.print()
    console.print(commit_panel)

    # Changelog panel
    changelog_panel = Panel(
        changelog_entry.strip(),
        title="[bold blue]Changelog Entry[/]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print()
    console.print(changelog_panel)
    console.print()


def print_auto_commit_success(message: str) -> None:
    """Print success message after auto-commit."""
    text = Text()
    text.append("\n✓ ", style="bold green")
    text.append("Auto-commit successful\n\n", style="green")
    text.append(message, style="dim")
    console.print(text)


def print_auto_commit_failed(error: str) -> None:
    """Print error message when auto-commit fails."""
    text = Text()
    text.append("\n✗ ", style="bold red")
    text.append("Auto-commit failed: ", style="red")
    text.append(error, style="red dim")
    console.print(text)


def print_diff_summary(diff: str, file_count: int) -> None:
    """Print a summary of the diff being processed."""
    lines = diff.splitlines()
    additions = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Files changed", str(file_count))
    table.add_row("Additions", f"[green]+{additions}[/]")
    table.add_row("Deletions", f"[red]-{deletions}[/]")
    table.add_row("Total lines", str(len(lines)))

    panel = Panel(
        table,
        title="[bold]Diff Summary[/]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(panel)


def print_error(message: str) -> None:
    """Print an error message."""
    text = Text()
    text.append("\n✗ ", style="bold red")
    text.append(message, style="red")
    console.print(text)
    console.print()


def print_info(message: str) -> None:
    """Print an info message."""
    text = Text()
    text.append("ℹ ", style="bold blue")
    text.append(message, style="blue")
    console.print(text)


def print_success(message: str) -> None:
    """Print a success message."""
    text = Text()
    text.append("✓ ", style="bold green")
    text.append(message, style="green")
    console.print(text)

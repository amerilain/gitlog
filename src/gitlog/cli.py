"""Main CLI entry point for gitlog."""

import os
import sys
from typing import Optional

import click

from . import __version__
from .git import (
    GitError,
    auto_commit,
    get_changed_files,
    get_diff,
    get_diff_if_staged_empty,
)
from .formatter import (
    print_auto_commit_success,
    print_both,
    print_changelog_entry,
    print_commit_message,
    print_diff_summary,
    print_error,
    print_info,
    print_success,
)
from .ai import (
    generate_changelog_entry,
    generate_commit_and_changelog,
    generate_commit_message,
)


MODEL_CHOICES = ["claude-sonnet-4", "claude-haiku-3"]
FORMAT_CHOICES = ["conventional", "angular", "simple"]
OUTPUT_CHOICES = ["message", "changelog", "both"]


@click.command(
    name="gitlog",
    help="Generate AI-powered commit messages and changelog entries from git diffs.",
    context_settings={"help_option_names": ["--help", "-h"]},
)
@click.option(
    "--staged/--all",
    default=True,
    help="Use staged changes only (default) or all unstaged changes.",
)
@click.option(
    "--commit",
    is_flag=True,
    default=False,
    help="Auto-commit with the generated message.",
)
@click.option(
    "--changelog",
    is_flag=True,
    default=False,
    help="Also generate a changelog entry.",
)
@click.option(
    "--format",
    type=click.Choice(FORMAT_CHOICES),
    default="conventional",
    help="Commit message format style.",
)
@click.option(
    "--model",
    type=click.Choice(MODEL_CHOICES),
    default="claude-sonnet-4",
    help="Claude model to use.",
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (or ANTHROPIC_API_KEY env var).",
    metavar="KEY",
)
@click.option(
    "--output",
    type=click.Choice(OUTPUT_CHOICES),
    default="message",
    help="What to generate. Use 'both' for commit message + changelog.",
)
@click.option(
    "--version",
    is_flag=True,
    default=False,
    help="Show the version and exit.",
)
def cli(
    staged: bool,
    commit: bool,
    changelog: bool,
    format: str,
    model: str,
    api_key: Optional[str],
    output: str,
    version: bool,
) -> None:
    """Analyze git diff and generate a commit message and/or changelog entry."""
    if version:
        click.echo(f"gitlog v{__version__}")
        sys.exit(0)

    # Resolve output mode
    if changelog and output == "message":
        output = "both"

    # Step 1: Get the git diff
    try:
        cwd = os.getcwd()

        if staged:
            diff = get_diff(staged=True, cwd=cwd)
        else:
            diff = get_diff(staged=False, cwd=cwd)

        files = get_changed_files(cwd)
        print_diff_summary(diff, len(files))

    except GitError as e:
        print_error(str(e))
        sys.exit(1)

    # Step 2: Verify API key is present
    resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not resolved_key:
        print_error(
            "Anthropic API key is required. "
            "Provide via --api-key or set the ANTHROPIC_API_KEY environment variable."
        )
        sys.exit(1)

    # Step 3: Generate using Claude
    try:
        with click.progressbar(
            length=1,
            label="Generating commit message",
            item_show_func=lambda x: " done" if x else " thinking...",
        ) as bar:
            bar.update(0)

            if output == "both":
                commit_msg, changelog_entry = generate_commit_and_changelog(
                    diff=diff,
                    format_style=format,
                    model=model,
                    api_key=resolved_key,
                    cwd=cwd,
                )
                bar.update(1)
            elif output == "changelog":
                changelog_entry = generate_changelog_entry(
                    diff=diff,
                    model=model,
                    api_key=resolved_key,
                    cwd=cwd,
                )
                commit_msg = ""
                bar.update(1)
            else:
                commit_msg = generate_commit_message(
                    diff=diff,
                    format_style=format,
                    model=model,
                    api_key=resolved_key,
                    cwd=cwd,
                )
                changelog_entry = ""
                bar.update(1)
    except (ValueError, RuntimeError) as e:
        print_error(str(e))
        sys.exit(1)

    # Step 4: Output results
    if output == "both" or output == "message":
        print_commit_message(commit_msg)
    if output == "both" or output == "changelog":
        print_changelog_entry(changelog_entry)

    # Step 5: Auto-commit if requested
    if commit and commit_msg:
        try:
            auto_commit(commit_msg, cwd=cwd)
            print_auto_commit_success(commit_msg)
        except GitError as e:
            print_auto_commit_failed(str(e))
            sys.exit(1)
    elif commit and not commit_msg:
        print_error("Cannot auto-commit: no commit message generated when output=changelog.")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()

"""Claude API interaction for gitlog."""

import os
from typing import Optional

from anthropic import Anthropic

from .git import get_branch_name, get_changed_files

# Default model mapping
MODEL_MAP = {
    "claude-sonnet-4": "claude-sonnet-4-20250514",
    "claude-haiku-3": "claude-haiku-3-20250313",
}

SYSTEM_PROMPT = """You are a highly skilled technical writing assistant. Your job is to analyze git diffs and generate concise, descriptive commit messages and changelog entries.

## Commit Message Rules
- Follow the Conventional Commits specification: `type(scope): description`
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- Scope is optional and should reference the module/component affected
- Description is imperative, lowercase, no period at end
- Keep the first line under 72 characters
- If more context is needed, add a blank line then a short body

## Changelog Entry Rules
- Same types as commit messages
- Human-readable summary of what changed and why
- Reference any breaking changes with `BREAKING CHANGE:`
- Use bullet points for multiple changes

Output only the generated content. No explanations, no greetings."""


def _get_api_key(api_key: Optional[str] = None) -> str:
    """Resolve the API key from arg or environment."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "Anthropic API key required. Provide via --api-key or "
            "set the ANTHROPIC_API_KEY environment variable."
        )
    return key


def _resolve_model(model: str) -> str:
    """Resolve model alias to actual model ID."""
    return MODEL_MAP.get(model, model)


def _truncate_diff(diff: str, max_chars: int = 50000) -> str:
    """Truncate diff if it's too large for the API."""
    if len(diff) <= max_chars:
        return diff
    return (
        diff[: max_chars - 200]
        + f"\n\n... [diff truncated: {len(diff) - max_chars + 200} more characters]"
    )


def generate_commit_message(
    diff: str,
    format_style: str = "conventional",
    model: str = "claude-sonnet-4",
    api_key: Optional[str] = None,
    cwd: Optional[str] = None,
) -> str:
    """Generate a commit message from a git diff using Claude.

    Args:
        diff: The git diff text.
        format_style: Commit style (conventional, angular, simple).
        model: Claude model to use.
        api_key: Anthropic API key.
        cwd: Working directory for context.

    Returns:
        The generated commit message.

    Raises:
        ValueError: If API key is missing.
        RuntimeError: If Claude API call fails.
    """
    key = _get_api_key(api_key)
    resolved_model = _resolve_model(model)
    truncated_diff = _truncate_diff(diff)

    branch = get_branch_name(cwd)
    files = get_changed_files(cwd)

    format_instructions = {
        "conventional": (
            "Use Conventional Commits format: type(scope): description\n"
            "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert\n"
            "Example: feat(auth): add OAuth2 login flow\n"
            "If there are breaking changes, add ! before the colon: feat(api)!: drop v1 endpoints"
        ),
        "angular": (
            "Use Angular commit format: <type>(<scope>): <subject>\n"
            "Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert\n"
            "Keep subject under 72 chars, lowercase, no period.\n"
            "Add body after blank line for extra context."
        ),
        "simple": (
            "Use simple one-line format: a concise, imperative sentence.\n"
            "Example: Add OAuth2 login flow with refresh tokens\n"
            "No type prefixes. Keep under 72 characters."
        ),
    }

    fmt = format_instructions.get(format_style, format_instructions["conventional"])

    user_prompt = f"""Branch: {branch}
Changed files: {', '.join(files) if files else 'unknown'}
Format style: {format_style}

{fmt}

Here is the diff:

```diff
{truncated_diff}
```

Generate a commit message following the rules above. Output only the commit message."""

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model=resolved_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text if response.content else ""
        return content.strip().strip("```").strip()
    except Exception as e:
        raise RuntimeError(f"Claude API request failed: {e}")


def generate_changelog_entry(
    diff: str,
    model: str = "claude-sonnet-4",
    api_key: Optional[str] = None,
    cwd: Optional[str] = None,
) -> str:
    """Generate a changelog entry from a git diff using Claude.

    Args:
        diff: The git diff text.
        model: Claude model to use.
        api_key: Anthropic API key.
        cwd: Working directory for context.

    Returns:
        The generated changelog entry.

    Raises:
        ValueError: If API key is missing.
        RuntimeError: If Claude API call fails.
    """
    key = _get_api_key(api_key)
    resolved_model = _resolve_model(model)
    truncated_diff = _truncate_diff(diff)

    branch = get_branch_name(cwd)
    files = get_changed_files(cwd)

    user_prompt = f"""Branch: {branch}
Changed files: {', '.join(files) if files else 'unknown'}

Here is the diff:

```diff
{truncated_diff}
```

Generate a changelog entry with:
- Type prefix (feat, fix, etc.)
- Human-readable summary bullet point
- Reference any breaking changes with `BREAKING CHANGE:`

Example:
### Features
- **auth**: add OAuth2 login flow with refresh token support

Output only the changelog entry. No explanations."""

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model=resolved_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text if response.content else ""
        return content.strip().strip("```").strip()
    except Exception as e:
        raise RuntimeError(f"Claude API request failed: {e}")


def generate_commit_and_changelog(
    diff: str,
    format_style: str = "conventional",
    model: str = "claude-sonnet-4",
    api_key: Optional[str] = None,
    cwd: Optional[str] = None,
) -> tuple[str, str]:
    """Generate both commit message and changelog entry in one API call.

    This is more efficient than two separate calls when both are needed.
    """
    key = _get_api_key(api_key)
    resolved_model = _resolve_model(model)
    truncated_diff = _truncate_diff(diff)

    branch = get_branch_name(cwd)
    files = get_changed_files(cwd)

    format_instructions = {
        "conventional": "Conventional Commits: type(scope): description",
        "angular": "Angular format: <type>(<scope>): <subject>",
        "simple": "Simple one-line format",
    }
    fmt = format_instructions.get(format_style, format_instructions["conventional"])

    user_prompt = f"""Branch: {branch}
Changed files: {', '.join(files) if files else 'unknown'}
Format: {format_style} ({fmt})

Here is the diff:

```diff
{truncated_diff}
```

Generate TWO things separated by the marker '---CHANGELOG---':

1. **Commit message** (first section, before the marker)
   - For {format_style} format

2. **Changelog entry** (second section, after the marker)
   - Human-readable summary with type prefix and bullet points
   - Include BREAKING CHANGE: if applicable

No other text before or after. Just the commit message, the marker, and the changelog entry."""

    try:
        client = Anthropic(api_key=key)
        response = client.messages.create(
            model=resolved_model,
            max_tokens=1536,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content = response.content[0].text if response.content else ""
        content = content.strip().strip("```").strip()

        if "---CHANGELOG---" in content:
            parts = content.split("---CHANGELOG---", 1)
            commit_msg = parts[0].strip()
            changelog_entry = parts[1].strip()
        else:
            # Fallback: treat whole output as commit message
            commit_msg = content
            changelog_entry = ""

        return commit_msg, changelog_entry
    except Exception as e:
        raise RuntimeError(f"Claude API request failed: {e}")

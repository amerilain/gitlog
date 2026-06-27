"""Git operations for gitlog - extracting diffs and commit info."""

import os
import subprocess
from pathlib import Path
from typing import Optional


class GitError(Exception):
    """Raised when git operations fail."""
    pass


def find_repo_root(path: Optional[str] = None) -> Path:
    """Find the git repository root from the given path or CWD."""
    target = path or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise GitError(f"Not a git repository (or any parent): {e.stderr.strip()}")
    except FileNotFoundError:
        raise GitError("Git is not installed or not found in PATH")
    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")


def get_diff(staged: bool = True, cwd: Optional[str] = None) -> str:
    """Get the git diff.

    Args:
        staged: If True, use --staged (staged changes only).
                If False, use unstaged changes (diff HEAD).
        cwd: Working directory for git commands.

    Returns:
        The diff output as a string.

    Raises:
        GitError: If git commands fail.
    """
    target = cwd or os.getcwd()
    try:
        if staged:
            result = subprocess.run(
                ["git", "diff", "--staged"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
        else:
            # Check if there's a HEAD to diff against
            subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )

        diff = result.stdout.strip()
        if not diff:
            raise GitError("No changes found. Nothing to commit.")
        return diff
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip()
        # Check if this was a rev-parse failure (no commits yet)
        if hasattr(e, "cmd") and "rev-parse" in e.cmd:
            raise GitError("No commits yet in this repository. Use --all to diff against an empty tree.")
        # Check if not in a git repo at all
        if "not a git repository" in stderr.lower():
            raise GitError(f"Not a git repository: {stderr}")
        raise GitError(f"Git diff failed: {stderr}")
    except FileNotFoundError:
        raise GitError("Git is not installed or not found in PATH")
    except subprocess.TimeoutExpired:
        raise GitError("Git command timed out")


def get_diff_if_staged_empty(cwd: Optional[str] = None) -> str:
    """Get staged diff, falling back to unstaged if nothing staged."""
    target = cwd or os.getcwd()
    try:
        # Check if there's anything staged
        staged_result = subprocess.run(
            ["git", "diff", "--staged", "--stat"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        if staged_result.stdout.strip():
            return get_diff(staged=True, cwd=target)
        # No staged changes, try unstaged
        return get_diff(staged=False, cwd=target)
    except GitError:
        return get_diff(staged=False, cwd=target)


def get_branch_name(cwd: Optional[str] = None) -> str:
    """Get the current git branch name."""
    target = cwd or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        branch = result.stdout.strip()
        return branch or "HEAD"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_changed_files(cwd: Optional[str] = None) -> list[str]:
    """Get list of changed files in the working tree."""
    target = cwd or os.getcwd()
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        if not files:
            result = subprocess.run(
                ["git", "diff", "HEAD", "--name-only"],
                cwd=target,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return files
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def auto_commit(message: str, cwd: Optional[str] = None) -> bool:
    """Auto-commit with the given message using git commit."""
    target = cwd or os.getcwd()
    try:
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=target,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return True
    except subprocess.CalledProcessError as e:
        raise GitError(f"Auto-commit failed: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise GitError("Git commit timed out")

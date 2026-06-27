# gitlog — AI-Powered Commit Messages & Changelogs

`gitlog` analyzes your staged git diff and uses Claude AI to generate polished, conventional commit messages and changelog entries — right from your terminal.

## Features

- 🤖 **AI-powered** — Generates commit messages using Claude's semantic analysis
- 🎨 **Multiple formats** — Conventional Commits, Angular, or simple one-liner
- 📋 **Changelog generation** — Optional human-readable changelog entries
- ✅ **Auto-commit** — Generate and commit in one step
- 🎯 **Smart diff selection** — Staged by default, falls back to unstaged
- 📊 **Pretty output** — Rich terminal formatting with diff summaries

## Installation

```bash
# Install from source
pip install git+https://github.com/your-org/gitlog.git

# Or local development install
cd gitlog
pip install -e .
```

## Usage

```bash
# Basic usage — generate a commit message from staged changes
gitlog

# Use all unstaged changes
gitlog --all

# Generate both commit message and changelog
gitlog --changelog

# Auto-commit with the generated message
gitlog --commit

# Choose format style
gitlog --format angular

# Specify output type
gitlog --output changelog

# Use a faster model
gitlog --model claude-haiku-3

# All options
gitlog --staged --commit --changelog --format conventional --model claude-sonnet-4
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--staged`/`--all` | `--staged` | Use staged or all unstaged changes |
| `--commit` | off | Auto-commit with generated message |
| `--changelog` | off | Also generate changelog entry |
| `--format` | `conventional` | Commit style: `conventional`, `angular`, or `simple` |
| `--model` | `claude-sonnet-4` | Claude model: `claude-sonnet-4` or `claude-haiku-3` |
| `--api-key` | env var | Anthropic API key |
| `--output` | `message` | What to output: `message`, `changelog`, or `both` |

## Environment Variables

- `ANTHROPIC_API_KEY` — Your Anthropic API key (required)

## Configuration

### API Key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or use `--api-key` on each invocation.

## Example Output

```
╭─ Diff Summary ─────────────────────────────────╮
│ Files changed    3                              │
│ Additions        +42                            │
│ Deletions        -15                            │
│ Total lines      180                            │
╰─────────────────────────────────────────────────╯

╭─ Commit Message ───────────────────────────────╮
│ feat(auth): add OAuth2 login with refresh token │
│                                                 │
│ Implements OAuth2 authorization code flow       │
│ with PKCE and refresh token rotation.           │
│                                                 │
│ Closes #42                                      │
╰─────────────────────────────────────────────────╯
```

## License

MIT — free for personal and commercial use.

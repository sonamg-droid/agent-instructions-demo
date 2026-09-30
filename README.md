# agent-instructions-demo

A harmless sample repository for demonstrating AI agent instruction scanning.

A tiny, functional Python changelog formatter: it parses
[Keep a Changelog](https://keepachangelog.com) style markdown and renders it
back in a normalized form (canonical category order, trimmed bullets).

## Usage

```python
from changelog_formatter import format_changelog

print(format_changelog(open("CHANGELOG.md").read()))
```

## Install and test

```bash
python -m venv .venv
source .venv/bin/activate
pip install pytest
pytest
```

## Structure

- `src/changelog_formatter.py` — parser and renderer
- `tests/test_changelog_formatter.py` — test suite
- `AGENTS.md` — instructions for AI coding agents

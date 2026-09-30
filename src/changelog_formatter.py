"""Parse and render Keep a Changelog style markdown files.

This module is intentionally small and dependency-free. It exists as a clean,
functional test target for the AI Agent Instruction Scanner example.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

CATEGORY_ORDER: tuple[str, ...] = (
    "Added",
    "Changed",
    "Deprecated",
    "Removed",
    "Fixed",
    "Security",
)

UNRELEASED: str = "Unreleased"
_BULLET_PREFIX: str = "- "


@dataclass
class Release:
    """A single release section parsed from a changelog document."""

    version: str
    date: str | None = None
    entries: dict[str, list[str]] = field(default_factory=dict)

    @property
    def is_unreleased(self) -> bool:
        return self.version == UNRELEASED


def parse_changelog(text: str) -> list[Release]:
    """Parse a Keep a Changelog style document into a list of releases.

    Release headings look like ``## [1.2.0] - 2024-05-01`` or ``## [Unreleased]``.
    Bullet lines may be prefixed with a category tag such as
    ``- **Added**: Add frobnicator``. Untagged bullets inherit the most recent
    ``### Category`` heading inside the same release; with no heading, they
    land under ``Changed``.
    """
    releases: list[Release] = []
    current: Release | None = None
    current_category: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = _new_release(line[3:])
            current_category = None
            releases.append(current)
        elif line.startswith("### ") and current is not None:
            current_category = line[4:].strip() or None
        elif line.startswith(_BULLET_PREFIX) and current is not None:
            category, message = _split_bullet(line[2:].strip(), current_category)
            if message:
                current.entries.setdefault(category, []).append(message)
    return releases


def render_changelog(releases: Sequence[Release]) -> str:
    """Render releases back to normalized Keep a Changelog markdown."""
    lines: list[str] = ["# Changelog", ""]
    for release in releases:
        heading = release.version
        if release.date:
            heading = f"{release.version} - {release.date}"
        lines.append(f"## {heading}")
        lines.append("")
        for category in _sorted_categories(release.entries):
            lines.append(f"### {category}")
            lines.append("")
            lines.extend(
                f"{_BULLET_PREFIX}{message}"
                for message in release.entries[category]
            )
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_changelog(text: str) -> str:
    """Parse a changelog document and render it in normalized form."""
    return render_changelog(parse_changelog(text))


def _new_release(heading: str) -> Release:
    version_part, sep, date_part = heading.partition("-")
    version = version_part.strip().strip("[]").strip() or UNRELEASED
    date = date_part.strip() if sep else None
    return Release(version=version, date=date or None)


def _split_bullet(message: str, fallback_category: str | None = None) -> tuple[str, str]:
    for category in CATEGORY_ORDER:
        tag = f"**{category}**"
        if message.startswith(tag):
            rest = message[len(tag):]
            return category, rest.lstrip(": ").strip()
        if message.startswith(f"{category}:"):
            return category, message[len(category) + 1:].strip()
    if fallback_category:
        return fallback_category, message
    return "Changed", message


def _sorted_categories(entries: dict[str, list[str]]) -> list[str]:
    return sorted(entries, key=_category_sort_key)


def _category_sort_key(category: str) -> tuple[int, str]:
    if category in CATEGORY_ORDER:
        return (0, CATEGORY_ORDER.index(category))
    return (1, category)

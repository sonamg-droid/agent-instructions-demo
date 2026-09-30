import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from changelog_formatter import (  # noqa: E402
    Release,
    format_changelog,
    parse_changelog,
    render_changelog,
)

SAMPLE = """\
# Changelog

## [Unreleased]

### Added
- **Added**: `format_changelog` convenience function.
- Initial public release notes.

### Fixed
- **Fixed**: handle empty changelog input without crashing.
"""

ONE_RELEASE = """\
## [1.2.0] - 2024-05-01

- **Added**: Add frobnicator API.
- **Fixed**: Trim bullet whitespace.
- Legacy note without a tag.
"""


def test_parse_releases_and_dates():
    releases = parse_changelog(SAMPLE)
    assert len(releases) == 1
    release = releases[0]
    assert release.version == "Unreleased"
    assert release.date is None
    assert release.is_unreleased
    assert release.entries["Added"] == [
        "`format_changelog` convenience function.",
        "Initial public release notes.",
    ]


def test_parse_tagged_and_untagged_bullets():
    releases = parse_changelog(ONE_RELEASE)
    release = releases[0]
    assert release.version == "1.2.0"
    assert release.date == "2024-05-01"
    assert release.entries["Added"] == ["Add frobnicator API."]
    assert release.entries["Fixed"] == ["Trim bullet whitespace."]
    assert release.entries["Changed"] == ["Legacy note without a tag."]


def test_parse_colon_style_tags():
    releases = parse_changelog("## 0.1.0\n- Security: Rotate signing keys.\n")
    assert releases[0].version == "0.1.0"
    assert releases[0].date is None
    assert releases[0].entries["Security"] == ["Rotate signing keys."]


def test_parse_ignores_bullets_before_first_release():
    releases = parse_changelog("- stray bullet\n## 1.0.0\n- First entry.\n")
    assert len(releases) == 1
    assert releases[0].entries == {"Changed": ["First entry."]}


def test_render_orders_categories():
    rendered = render_changelog(
        [
            Release(
                version="2.0.0",
                date="2026-01-02",
                entries={
                    "Fixed": ["Fix parser edge case."],
                    "Added": ["Add renderer."],
                    "Custom": ["Odd category."],
                },
            )
        ]
    )
    assert rendered.index("### Added") < rendered.index("### Fixed")
    assert rendered.index("### Fixed") < rendered.index("### Custom")
    assert "## 2.0.0 - 2026-01-02" in rendered


def test_render_unreleased_has_no_date():
    rendered = render_changelog([Release(version="Unreleased", entries={})])
    assert "## Unreleased\n" in rendered


def test_format_round_trip():
    formatted = format_changelog(SAMPLE)
    assert formatted.startswith("# Changelog")
    assert "## Unreleased" in formatted
    assert format_changelog(formatted) == formatted


def test_format_empty_input():
    assert format_changelog("") == "# Changelog\n"


def test_parse_empty_text():
    assert parse_changelog("") == []
    assert parse_changelog("no headings here\n") == []

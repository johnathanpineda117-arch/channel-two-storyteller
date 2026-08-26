"""Shared test helpers.

Kept out of the test modules themselves so no test has to import another test
module to reuse them.
"""

import re
from pathlib import Path

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def github_heading_slug(heading: str) -> str:
    """Match GitHub heading anchors.

    GitHub replaces each whitespace character after stripping punctuation and
    emoji, so a removed emoji or slash leaves a double dash rather than a
    collapsed single hyphen.
    """

    text = heading.lstrip("#").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s", "-", text)


def headings_in(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    slugs: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not _HEADING_RE.match(line):
            continue
        slug = github_heading_slug(line)
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def citation_resolves(source: str) -> bool:
    """Check that a ``document.md#anchor`` citation points at a real heading."""

    document, separator, anchor = source.partition("#")
    if not (separator and document.endswith(".md") and anchor):
        return False
    path = REPOSITORY_ROOT / document
    return path.is_file() and anchor in headings_in(path)

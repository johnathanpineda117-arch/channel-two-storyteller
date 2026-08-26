"""Knowledge catalog tests."""

from channel2.knowledge import load_catalog
from channel2.models import ContentPillar, StoryMode


def test_catalog_matches_schema_enums() -> None:
    catalog = load_catalog()

    assert catalog.entry_ids("content_pillars") == {
        item.value for item in ContentPillar
    }
    assert catalog.entry_ids("story_modes") == {item.value for item in StoryMode}
    assert len(catalog.hook_types) == 10


def test_catalog_entries_link_to_design_docs() -> None:
    catalog = load_catalog()
    entries = (
        catalog.content_pillars + catalog.hook_types + catalog.story_modes
    )
    assert all(".md#" in entry.source for entry in entries)

"""Load and validate the versioned Channel 2 knowledge catalog."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from channel2.config import load_settings
from channel2.models import ContentPillar, StoryMode


class KnowledgeEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)


class KnowledgeCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    content_pillars: list[KnowledgeEntry]
    hook_types: list[KnowledgeEntry]
    story_modes: list[KnowledgeEntry]

    def entry_ids(self, collection: str) -> set[str]:
        entries: list[KnowledgeEntry] = getattr(self, collection)
        return {entry.id for entry in entries}


def _ensure_unique(entries: list[KnowledgeEntry], collection: str) -> None:
    ids = [entry.id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate ids in knowledge collection: {collection}")


def load_catalog(path: Path | None = None) -> KnowledgeCatalog:
    """Load the catalog and ensure it stays aligned with schema enums."""

    catalog_path = path or load_settings().knowledge_path
    raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog = KnowledgeCatalog.model_validate(raw)

    for collection in ("content_pillars", "hook_types", "story_modes"):
        _ensure_unique(getattr(catalog, collection), collection)

    expected_pillars = {item.value for item in ContentPillar}
    expected_modes = {item.value for item in StoryMode}
    if catalog.entry_ids("content_pillars") != expected_pillars:
        raise ValueError("content pillar catalog does not match ContentPillar enum")
    if catalog.entry_ids("story_modes") != expected_modes:
        raise ValueError("story mode catalog does not match StoryMode enum")

    return catalog

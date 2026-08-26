"""Load and validate the versioned Channel 2 knowledge catalog."""

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from channel2.config import load_settings
from channel2.models.story import ContentPillar, StoryMode
from channel2.models.vocabulary import (
    Decision,
    EmotionalTarget,
    HookType,
    StoryStructure,
    Tempo,
    VisualFormat,
)


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
    story_structures: list[KnowledgeEntry]
    visual_formats: list[KnowledgeEntry]
    tempos: list[KnowledgeEntry]
    emotional_targets: list[KnowledgeEntry]
    decisions: list[KnowledgeEntry]

    def entry_ids(self, collection: str) -> set[str]:
        entries: list[KnowledgeEntry] = getattr(self, collection)
        return {entry.id for entry in entries}


# Each documented collection must match exactly one code enum. A term cannot be
# added to either side alone.
COLLECTION_ENUMS: dict[str, type[StrEnum]] = {
    "content_pillars": ContentPillar,
    "hook_types": HookType,
    "story_modes": StoryMode,
    "story_structures": StoryStructure,
    "visual_formats": VisualFormat,
    "tempos": Tempo,
    "emotional_targets": EmotionalTarget,
    "decisions": Decision,
}


def _ensure_unique(entries: list[KnowledgeEntry], collection: str) -> None:
    ids = [entry.id for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate ids in knowledge collection: {collection}")


def load_catalog(path: Path | None = None) -> KnowledgeCatalog:
    """Load the catalog and ensure it stays aligned with schema enums."""

    catalog_path = path or load_settings().knowledge_path
    raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog = KnowledgeCatalog.model_validate(raw)

    for collection, enum_type in COLLECTION_ENUMS.items():
        _ensure_unique(getattr(catalog, collection), collection)
        documented = catalog.entry_ids(collection)
        defined = {item.value for item in enum_type}
        if documented != defined:
            undocumented = sorted(defined - documented)
            unrecognized = sorted(documented - defined)
            raise ValueError(
                f"{collection} does not match {enum_type.__name__}: "
                f"missing from catalog {undocumented}, "
                f"missing from enum {unrecognized}"
            )

    return catalog

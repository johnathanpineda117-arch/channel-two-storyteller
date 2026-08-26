"""Knowledge catalog tests."""

import inspect
from enum import StrEnum

import pytest
import yaml

from channel2.knowledge import load_catalog
from channel2.knowledge.loader import COLLECTION_ENUMS, KnowledgeCatalog
from channel2.models import vocabulary as vocabulary_module
from helpers import REPOSITORY_ROOT, headings_in


def test_every_collection_matches_its_enum() -> None:
    catalog = load_catalog()

    for collection, enum_type in COLLECTION_ENUMS.items():
        assert catalog.entry_ids(collection) == {item.value for item in enum_type}, (
            f"{collection} drifted from {enum_type.__name__}"
        )


def test_collection_enums_registration_is_complete() -> None:
    vocabulary_enums = {
        cls
        for _, cls in inspect.getmembers(vocabulary_module, inspect.isclass)
        if isinstance(cls, type) and issubclass(cls, StrEnum) and cls is not StrEnum
    }
    registered = set(COLLECTION_ENUMS.values())
    assert vocabulary_enums <= registered, (
        "unregistered catalog enums: "
        + ", ".join(sorted(cls.__name__ for cls in vocabulary_enums - registered))
    )

    catalog_collections = {
        name for name in KnowledgeCatalog.model_fields if name != "version"
    }
    assert catalog_collections == set(COLLECTION_ENUMS), (
        "COLLECTION_ENUMS must map every catalog collection and no others"
    )


def test_catalog_entries_link_to_design_docs() -> None:
    catalog = load_catalog()

    for collection in COLLECTION_ENUMS:
        for entry in getattr(catalog, collection):
            document, separator, anchor = entry.source.partition("#")
            assert separator and document.endswith(".md") and anchor, (
                f"{collection}/{entry.id} citation is not a markdown heading anchor"
            )
            source_path = REPOSITORY_ROOT / document
            assert source_path.is_file(), (
                f"{collection}/{entry.id} cites missing file {document}"
            )
            assert anchor in headings_in(source_path), (
                f"{collection}/{entry.id} cites unknown heading "
                f"{document}#{anchor}"
            )


def test_catalog_documents_no_untyped_escape_hatch() -> None:
    # An "other" bucket would let creative variables become uncomparable.
    catalog = load_catalog()

    for collection in COLLECTION_ENUMS:
        assert "other" not in catalog.entry_ids(collection)


def test_undocumented_enum_term_is_rejected(tmp_path) -> None:
    raw = yaml.safe_load(_catalog_source_text())
    raw["decisions"] = [
        entry for entry in raw["decisions"] if entry["id"] != "no-decision"
    ]
    drifted = tmp_path / "catalog.yaml"
    drifted.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(ValueError, match=r"missing from catalog \['no-decision'\]"):
        load_catalog(drifted)


def test_undefined_catalog_term_is_rejected(tmp_path) -> None:
    raw = yaml.safe_load(_catalog_source_text())
    raw["visual_formats"].append(
        {
            "id": "claymation",
            "name": "Claymation",
            "description": "A format nobody added to the enum.",
            "source": "README.md#4-visual-philosophy",
        }
    )
    drifted = tmp_path / "catalog.yaml"
    drifted.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(ValueError, match=r"missing from enum \['claymation'\]"):
        load_catalog(drifted)


def _catalog_source_text() -> str:
    from channel2.config import load_settings

    return load_settings().knowledge_path.read_text(encoding="utf-8")

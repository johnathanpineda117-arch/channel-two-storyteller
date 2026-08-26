"""Knowledge catalog tests."""

import pytest
import yaml

from channel2.knowledge import load_catalog
from channel2.knowledge.loader import COLLECTION_ENUMS


def test_every_collection_matches_its_enum() -> None:
    catalog = load_catalog()

    for collection, enum_type in COLLECTION_ENUMS.items():
        assert catalog.entry_ids(collection) == {item.value for item in enum_type}, (
            f"{collection} drifted from {enum_type.__name__}"
        )


def test_catalog_entries_link_to_design_docs() -> None:
    catalog = load_catalog()

    for collection in COLLECTION_ENUMS:
        for entry in getattr(catalog, collection):
            assert ".md#" in entry.source, f"{collection}/{entry.id} has no doc anchor"


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

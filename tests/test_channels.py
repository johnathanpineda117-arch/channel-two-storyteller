"""Channel registry tests.

These cover the registry itself. ``StoryRecord`` and ``Pipeline`` are not yet
channel-aware, so the end-to-end isolation behavior is not provable here.
"""

import copy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from channel2.knowledge import UnknownChannelError, load_catalog, load_channels
from channel2.models import Channel, ContentPillar, StoryClassification
from channel2.models.channel import VerificationPolicy
from helpers import REPOSITORY_ROOT, citation_resolves, headings_in

_LEGACY_PILLARS = {
    ContentPillar.HUMAN_STORIES,
    ContentPillar.UNBELIEVABLE_SURVIVAL,
    ContentPillar.FUNNY_RELATABLE,
    ContentPillar.MYSTERY_STRANGE,
    ContentPillar.SATISFYING_EMOTIONAL,
}


def _registry_source() -> dict:
    from channel2.config import load_settings

    return yaml.safe_load(load_settings().channels_path.read_text(encoding="utf-8"))


def _load_modified(tmp_path: Path, mutate) -> None:
    raw = copy.deepcopy(_registry_source())
    mutate(raw)
    path = tmp_path / "channels.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    load_channels(path)


def test_registered_channels_resolve_by_id() -> None:
    registry = load_channels()

    roblox = registry.get("robloxtales")
    legacy = registry.get("legacy-storyteller")

    assert roblox.active
    assert not legacy.active


def test_unknown_channel_fails_instead_of_defaulting() -> None:
    registry = load_channels()

    with pytest.raises(UnknownChannelError, match="unknown channel 'moneyplaybook'"):
        registry.get("moneyplaybook")


def test_pillar_validity_is_scoped_to_the_channel() -> None:
    registry = load_channels()
    roblox = registry.get("robloxtales")
    legacy = registry.get("legacy-storyteller")

    assert roblox.allows_pillar(ContentPillar.ROBUX)
    assert not legacy.allows_pillar(ContentPillar.ROBUX)

    assert legacy.allows_pillar(ContentPillar.UNBELIEVABLE_SURVIVAL)
    assert not roblox.allows_pillar(ContentPillar.UNBELIEVABLE_SURVIVAL)


def test_no_active_channel_can_reach_a_legacy_pillar() -> None:
    # Legacy terms stay defined so old records remain interpretable, but they
    # must not silently become current truth for a live channel.
    for channel in load_channels().channels:
        if channel.active:
            assert not channel.pillars & _LEGACY_PILLARS, channel.channel_id


def test_every_channel_pillar_is_documented_vocabulary() -> None:
    # The forward direction only. A documented pillar may legitimately exist
    # before any channel activates it, exactly like staged vocabulary
    # elsewhere; vocabulary must not force product configuration.
    documented = {entry.id: entry for entry in load_catalog().content_pillars}

    for channel in load_channels().channels:
        for pillar in channel.pillars:
            entry = documented.get(pillar.value)
            assert entry is not None, (
                f"{channel.channel_id} uses undocumented pillar {pillar.value}"
            )
            assert citation_resolves(entry.source), (
                f"{channel.channel_id} uses pillar {pillar.value}, whose "
                f"citation {entry.source} does not resolve"
            )


def test_verification_requirements_are_channel_specific() -> None:
    registry = load_channels()
    roblox = registry.get("robloxtales").verification_policy
    legacy = registry.get("legacy-storyteller").verification_policy

    assert not roblox.requires_verification(StoryClassification.FICTION)
    assert not roblox.allows(StoryClassification.NONFICTION)

    assert legacy.requires_verification(StoryClassification.NONFICTION)
    assert not legacy.requires_verification(StoryClassification.FICTION)


def test_policy_cannot_require_verification_it_never_publishes() -> None:
    with pytest.raises(ValidationError, match="does not publish"):
        VerificationPolicy(
            allowed_classifications={StoryClassification.FICTION},
            verification_required_for={StoryClassification.NONFICTION},
        )


def test_channel_pillars_must_be_defined_vocabulary(tmp_path: Path) -> None:
    def add_undefined_pillar(raw: dict) -> None:
        raw["channels"][0]["pillars"].append("crypto")

    with pytest.raises(ValidationError):
        _load_modified(tmp_path, add_undefined_pillar)


def test_channel_must_declare_at_least_one_pillar(tmp_path: Path) -> None:
    def empty_pillars(raw: dict) -> None:
        raw["channels"][0]["pillars"] = []

    with pytest.raises(ValidationError):
        _load_modified(tmp_path, empty_pillars)


def test_duplicate_channel_identity_is_rejected(tmp_path: Path) -> None:
    def duplicate_id(raw: dict) -> None:
        raw["channels"][1]["channel_id"] = raw["channels"][0]["channel_id"]

    with pytest.raises(ValidationError, match="duplicate channel channel_id"):
        _load_modified(tmp_path, duplicate_id)

    def duplicate_name(raw: dict) -> None:
        raw["channels"][1]["name"] = raw["channels"][0]["name"]

    with pytest.raises(ValidationError, match="duplicate channel name"):
        _load_modified(tmp_path, duplicate_name)


def test_unrecognized_channel_keys_are_rejected(tmp_path: Path) -> None:
    def add_stray_key(raw: dict) -> None:
        raw["channels"][0]["audience"] = "kids"

    with pytest.raises(ValidationError):
        _load_modified(tmp_path, add_stray_key)


def test_channel_definitions_cite_design_docs() -> None:
    for channel in load_channels().channels:
        document, separator, anchor = channel.source.partition("#")
        assert separator and document.endswith(".md") and anchor, (
            f"{channel.channel_id} citation is not a markdown heading anchor"
        )
        source_path = REPOSITORY_ROOT / document
        assert source_path.is_file(), (
            f"{channel.channel_id} cites missing file {document}"
        )
        assert anchor in headings_in(source_path), (
            f"{channel.channel_id} cites unknown heading {document}#{anchor}"
        )


def test_channel_configuration_is_immutable() -> None:
    channel = load_channels().get("robloxtales")

    with pytest.raises(ValidationError):
        channel.active = False


def test_channel_is_exported_from_models() -> None:
    assert Channel.model_fields.keys() >= {
        "channel_id",
        "name",
        "pillars",
        "verification_policy",
        "active",
    }
